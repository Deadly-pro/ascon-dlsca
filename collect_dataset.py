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
    gain      = 25 dB programmable (+ ~20 dB fixed external -> ~45 dB total)
    adc_src   = clkgen_x4 (40 MHz, free-running)
    samples   = 24000 (>24430 causes CW-Lite buffer underrun)
    crypto    = 10.0 MHz (PLL1, verified via pll_outfreq_get)
    tio_clkout enabled via REG_CLKSETTINGS = 0x19

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
    while not target.is_done() and time.time() - t0 < timeout:
        time.sleep(0.001)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(here, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('-n', '--num', type=int, default=1000, help='traces to collect')
    ap.add_argument('-s', '--samples', type=int, default=24000)
    ap.add_argument('-o', '--output', default=os.path.join(here, 'Dataset', 'ascon_dataset.h5'))
    ap.add_argument('--key', type=str, default=None, help='16-byte key hex; random if omitted')
    ap.add_argument('--no-verify', action='store_true', help='skip per-trace readback verification')
    ap.add_argument('--max-fail', type=int, default=10, help='abort after N consecutive failures')
    ap.add_argument('--gain', type=int, default=25)
    ap.add_argument('--no-program', action='store_true')
    args = ap.parse_args()

    fixed_key = None if args.key is None else bytes.fromhex(args.key)
    if fixed_key is not None and len(fixed_key) != 16:
        sys.exit("key must be 16 bytes in hex")

    print(f"[+] Connecting CW305 target ...")
    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=None if args.no_program else args.bitstream,
                       fpga_id='100t', platform='cw305')
    if not args.no_program:
        target.vccint_set(1.0)
        target.pll.pll_enable_set(True)
        target.pll.pll_outenable_set(False, 0)
        target.pll.pll_outenable_set(True, 1)
        target.pll.pll_outenable_set(False, 2)
        target.pll.pll_outfreq_set(10e6, 1)
    target.clkusbautooff = True
    target.clksleeptime = 1
    target.fpga_write(0x00, [0x19])   # enable tio_clkout
    t = wrap(target)

    scope = cw.scope()
    scope.gain.db = args.gain
    scope.adc.samples = args.samples
    scope.adc.offset = 0
    scope.clock.adc_src = 'clkgen_x4'
    scope.clock.clkgen_freq = 40e6
    scope.clock.reset_adc()
    scope.trigger.triggers = 'tio4'

    traces, keys, nonces, cts = [], [], [], []
    fails = 0
    key_mode = 'fixed' if fixed_key is not None else 'random'
    print(f"[+] collecting {args.num} traces ({key_mode} key, {args.samples} samples)")
    print(f"[+] gain={args.gain} dB, adc_src=clkgen_x4, verify={'ON' if not args.no_verify else 'off'}")
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
        scope.arm()
        t.go()
        ret = scope.capture()
        if ret:
            print(f"    trace {i}: trigger timeout, skipping")
            _drain(t)
            fails += 1
            continue

        ct = bytes(t.readOutput())

        if not args.no_verify:
            exp = exp_list[i]
            if ct != exp:
                print(f"    trace {i}: VERIFY FAILED got={ct.hex()} exp={exp.hex()} - skipping")
                fails += 1
                if fails >= args.max_fail:
                    sys.exit(f"aborting: {fails} unverified traces")
                continue

        traces.append(scope.get_last_trace())
        keys.append(key)
        nonces.append(nonce)
        cts.append(ct)
        if i % 50 == 0 or i == args.num - 1:
            print(f"    {i+1}/{args.num} (fails: {fails})")

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
        f.attrs['source_bitstream'] = os.path.basename(args.bitstream)

    print(f"[+] Saved {tr.shape[0]} verified traces -> {args.output} (fails: {fails})")

    target.dis()
    scope.dis()


if __name__ == '__main__':
    main()
