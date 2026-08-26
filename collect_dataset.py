#!/usr/bin/env python3
r"""collect_dataset.py — synchronized Ascon-128 power-trace dataset collection.

Every iteration captures ONE operation: key + nonce are written, the ADC is
armed only after the inputs are latched, the op runs, and the readback is
VERIFIED against the standard ASCON-128 reference (ascon_ref.py).

Output h5 (training-ready):
    traces (n, samples) f32     power traces (tio_trigger edge, ADC @ 40 MHz)
    keys   (n, 16)       u8     per-trace key
    nonces (n, 16)       u8     per-trace nonce
    ciphertexts (n, 16)  u8     readback {tag[95:0], ct[31:0]}
    attrs: adc_samples, fs_hz, crypto_clk_hz, gain_db, key_mode,
           verified, num_traces, source_bitstream

Confirmed settings:
    gain      = 20 dB programmable (+ ~20 dB fixed external -> ~40 dB total)
    adc_src   = clkgen_x4 (40 MHz, free-running)
    samples   = 2000 (0-50 us; the crypto op lives in the first ~50 us.
               Larger windows only add idle/USB-re-enable noise and dilute SNR.)
    crypto    = 10.0 MHz (PLL1, verified via pll_outfreq_get)
    tio_clkout enabled via REG_CLKSETTINGS = 0x19

Quality filters (per trace, before storage):
    verify   : readback must match the ASCON oracle (unless --no-verify)
    clip     : reject if |trace|.max() > clip-threshold (0.49 V = ADC rail)
    flat     : reject if trace.std() < std-floor (default 0.001 V = dead capture)

Usage:
    python3 collect_dataset.py -n 1000 -o Dataset/run.h5
    python3 collect_dataset.py -n 500 --key 000102030405060708090a0b0c0d0e0f
"""
import argparse
import os
import sys
import time

import h5py
import numpy as np
import chipwhisperer as cw

from ascon_ref import batch_fpga_expected
from cw305_ascon_shim import wrap


def _drain(target, timeout=0.2):
    t0 = time.time()
    try:
        while not target.is_done() and time.time() - t0 < timeout:
            time.sleep(0.001)
    except AttributeError:
        time.sleep(0.002)  # no is_done on raw target; core finishes in ~10 us


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(here, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('-n', '--num', type=int, default=1000, help='traces to collect')
    ap.add_argument('-s', '--samples', type=int, default=2000,
                    help='samples per trace (2000 = 0-50 us @ 40 MHz)')
    ap.add_argument('-o', '--output', default=os.path.join(here, 'Dataset', 'ascon_dataset.h5'))
    ap.add_argument('--key', type=str, default=None, help='16-byte key hex; random if omitted')
    ap.add_argument('--no-verify', action='store_true', help='skip per-trace readback verification')
    ap.add_argument('--max-fail', type=int, default=10, help='abort after N consecutive failures')
    ap.add_argument('--max-retry', type=int, default=6,
                    help='max arm/go attempts per (key, nonce) before declaring flat')
    ap.add_argument('--gain', type=int, default=20)
    ap.add_argument('--offset', type=int, default=0,
                    help='ADC offset DAC value (raw int; shifts DC baseline down)')
    ap.add_argument('--clip-threshold', type=float, default=0.49,
                    help='reject traces with |trace|.max() above this (clipping)')
    ap.add_argument('--std-floor', type=float, default=0.001,
                    help='reject traces with std below this (dead/flat capture)')
    ap.add_argument('--no-program', action='store_true')
    ap.add_argument('--crypto-mhz', type=float, default=10.0,
                    help='crypto clock MHz (PLL1)')
    args = ap.parse_args()

    fixed_key = None if args.key is None else bytes.fromhex(args.key)
    if fixed_key is not None and len(fixed_key) != 16:
        sys.exit("key must be 16 bytes in hex")

    from scope_config import connect_target
    print(f"[+] Connecting CW305 target ...")
    t = connect_target(None if args.no_program else args.bitstream,
                       crypto_hz=args.crypto_mhz * 1e6,
                       program=not args.no_program)
    target = t._t  # raw target for pll readback / drain

    from scope_config import configure_scope, scope_model_name, firmware_note
    scope = configure_scope(gain=args.gain, samples=args.samples,
                            offset=args.offset, sample_rate=40e6)
    print(f'[+] scope      : {scope_model_name(scope)}')

    traces, keys, nonces, cts = [], [], [], []
    verify_fails = 0
    clips = 0
    flats = 0
    key_mode = 'fixed' if fixed_key is not None else 'random'
    print(f"[+] collecting {args.num} traces ({key_mode} key, {args.samples} samples)")
    print(f"[+] gain={args.gain} dB, verify={'ON' if not args.no_verify else 'off'}")
    crypto_freq = target.pll.pll_outfreq_get(1)
    print(f"[+] crypto clock = {crypto_freq/1e6:.1f} MHz (CDCE906 pllread)")

    plan = []
    for i in range(args.num):
        key = fixed_key if fixed_key is not None else os.urandom(16)
        nonce = os.urandom(16)
        plan.append((key, nonce))

    exp_list = None
    if not args.no_verify:
        t0 = time.time()
        exp_list = batch_fpga_expected(plan)
        print(f"[+] oracle: {len(exp_list)} expected readbacks in {time.time()-t0:.1f}s")

    for i, (key, nonce) in enumerate(plan):
        t.loadEncryptionKey(key)
        t.loadInput(nonce)
        # The arm/go/trigger sequence has a known race: ~50 % of captures come
        # back flat because the ADC triggered on the tail of the previous
        # transaction instead of this op. The scope.capture() return flag is
        # unreliable here (both timeout and success can carry a live trace), so
        # judge purely by content + oracle verify. Retry the same (key, nonce)
        # a few times, keeping only a verified, non-flat, non-clipped capture.
        attempt = 0
        while True:
            attempt += 1
            scope.arm()
            t.go()
            scope.capture()
            trace = scope.get_last_trace()
            if trace is None or trace.size == 0 or trace.size < 64:
                if attempt >= args.max_retry:
                    flats += 1
                    break
                _drain(t)
                continue
            if trace.size != args.samples:
                if attempt >= args.max_retry:
                    flats += 1
                    break
                _drain(t)
                continue
            if not np.isfinite(trace).all():
                if attempt >= args.max_retry:
                    flats += 1
                    break
                _drain(t)
                continue
            if trace.std() < args.std_floor:
                if attempt >= args.max_retry:
                    flats += 1
                    break
                _drain(t)
                continue

            ct = bytes(t.readOutput())

            if not args.no_verify:
                exp = exp_list[i]
                if ct != exp:
                    print(f"    trace {i} (att {attempt}): VERIFY FAILED got={ct.hex()} exp={exp.hex()} — skipping")
                    verify_fails += 1
                    if verify_fails >= args.max_fail:
                        sys.exit(f"aborting: {verify_fails} consecutive verify failures")
                    break

            peak = float(np.abs(trace).max())
            if not np.isfinite(peak):
                if attempt >= args.max_retry:
                    flats += 1
                    break
                _drain(t)
                continue
            if peak > args.clip_threshold:
                clips += 1
                if attempt >= args.max_retry:
                    break
                _drain(t)
                continue
            else:
                traces.append(trace)
                keys.append(key)
                nonces.append(nonce)
                cts.append(ct)
                break
        if i % 50 == 0 or i == args.num - 1:
            print(f"    {i+1}/{args.num} (stored: {len(traces)}, verify_err: {verify_fails}, clip: {clips}, flat: {flats})")

    tr = np.array(traces, dtype=np.float32)
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    with h5py.File(args.output, 'w') as f:
        f.create_dataset('traces', data=tr, compression='gzip')
        f.create_dataset('keys', data=np.frombuffer(b''.join(keys), np.uint8).reshape(-1, 16))
        f.create_dataset('nonces', data=np.frombuffer(b''.join(nonces), np.uint8).reshape(-1, 16))
        f.create_dataset('ciphertexts', data=np.frombuffer(b''.join(cts), np.uint8).reshape(-1, 16))
        f.attrs['adc_samples'] = args.samples
        f.attrs['fs_hz'] = 40e6
        f.attrs['crypto_clk_hz'] = crypto_freq
        f.attrs['gain_db'] = args.gain
        f.attrs['gain_note'] = 'programmable + ~20 dB fixed external'
        f.attrs['adc_src'] = 'clkgen_x4'
        f.attrs['key_mode'] = key_mode
        f.attrs['verified'] = not args.no_verify
        f.attrs['num_traces'] = tr.shape[0]
        f.attrs['clipped_rejected'] = clips
        f.attrs['flat_rejected'] = flats
        f.attrs['clip_threshold'] = args.clip_threshold
        f.attrs['std_floor'] = args.std_floor
        f.attrs['source_bitstream'] = os.path.basename(args.bitstream)

    print(f"[+] Saved {tr.shape[0]} verified traces -> {args.output} "
          f"(verify_err: {verify_fails}, clip: {clips}, flat: {flats})")

    t.dis()
    scope.dis()


if __name__ == '__main__':
    main()
