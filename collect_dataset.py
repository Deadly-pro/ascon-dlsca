#!/usr/bin/env python3
"""collect_dataset.py — synchronized ASCON power-trace dataset collection.

Every iteration captures ONE operation: random (or fixed) key + random nonce
are written, the ADC is armed only after the inputs are latched, the op runs,
and the ciphertext is read back and VERIFIED against the ASCON-128 reference.
A trace is stored only if its key/nonce/ct verify — so the trace, key, nonce
and ciphertext stored at index i always belong to the SAME operation.

Output h5 (training-ready):
    traces (n, samples) f32     power traces (CW305 tio_trigger, ADC @ extclk_x4)
    keys   (n, 16)      u8      per-trace key
    nonces (n, 16)      u8      per-trace nonce
    ciphertexts (n, 16) u8      readback {tag[95:0], ct[31:0]}
    attrs: adc_samples, fs_hz, crypto_clk_hz, gain_db, key_mode,
           verified, num_traces, source_bitstream

Usage:
    python3 collect_dataset.py -n 1000 -s 25000 -o Dataset/ascon_dataset.h5
    python3 collect_dataset.py -n 500  --key 000102030405060708090a0b0c0d0e0f   # fixed key
"""
import argparse
import os
import sys
import time

import h5py
import numpy as np
import chipwhisperer as cw

from ascon_ref import fpga_expected


def _drain(target, timeout=2.0):
    """Wait for the FPGA op to finish so tio_trigger deasserts before the next
    arm(). Needed even when the scope missed the trigger - the op already ran
    and a lingering high trigger would misalign the next trace."""
    t0 = time.time()
    while not target.is_done() and time.time() - t0 < timeout:
        time.sleep(0.001)
    return target.is_done()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('-n', '--num', type=int, default=1000, help='number of traces')
    ap.add_argument('-s', '--samples', type=int, default=25000,
                    help='ADC samples per trace (40 MS/s; bit-serial op ~800 us)')
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(here, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('-o', '--output', default=os.path.join(here, 'Dataset', 'ascon_dataset.h5'))
    ap.add_argument('--key', default=None, metavar='HEX',
                    help='fixed key for all traces (default: random per trace)')
    ap.add_argument('--no-verify', action='store_true',
                    help='skip ciphertext verification (not recommended)')
    ap.add_argument('--max-fail', type=int, default=10,
                    help='abort after this many unverified traces')
    args = ap.parse_args()

    fixed_key = bytes.fromhex(args.key) if args.key else None
    if fixed_key is not None and len(fixed_key) != 16:
        sys.exit("--key must be 16 bytes")

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    # ---- scope (CW-Lite ADC) ----
    scope = cw.scope()
    scope.default_setup()
    scope.gain.db = 25
    scope.adc.samples = args.samples
    scope.adc.offset = 0
    scope.adc.basic_mode = "rising_edge"
    scope.trigger.triggers = "tio4"          # CW305 tio_trigger -> CW-Lite tio4
    scope.io.tio1 = "serial_rx"
    scope.io.tio2 = "serial_tx"
    scope.io.hs2 = "disabled"

    # ---- CW305 target: program bitstream + configure PLL/crypto clock ----
    target = cw.target(scope, cw.targets.CW305, force=True,
                       bsfile=args.bitstream, fpga_id='100t', platform='cw305')
    target.vccint_set(1.0)
    target.pll.pll_enable_set(True)
    target.pll.pll_outenable_set(False, 0)
    target.pll.pll_outenable_set(True, 1)    # crypto clock out -> pll_clk1
    target.pll.pll_outenable_set(False, 2)
    target.pll.pll_outfreq_set(10e6, 1)      # 10 MHz crypto clock
    target.clkusbautooff = True              # drop USB clock noise during capture
    target.clksleeptime = 1

    # ADC clocked off the FPGA's crypto clock (4x oversample), must lock
    scope.clock.adc_src = "extclk_x4"
    locked = False
    for _ in range(5):
        try:
            scope.clock.reset_adc()
            locked = True
            break
        except OSError:
            time.sleep(0.1)
    if not locked:
        sys.exit("ADC failed to lock - check tio_clkout/clock DIP switch (K16) and PLL")

    traces, keys, nonces, cts = [], [], [], []
    fails = 0
    key_mode = 'fixed' if fixed_key is not None else 'random'
    print(f"[+] collecting {args.num} traces ({key_mode} key, {args.samples} samples)")
    print(f"[+] verifying ciphertext readback per trace: {not args.no_verify}")

    for i in range(args.num):
        key = fixed_key if fixed_key is not None else os.urandom(16)
        nonce = os.urandom(16)

        # Load ALL inputs BEFORE arming: USB register writes take variable ms,
        # so arm only once the FPGA is idle and inputs are latched. This keeps
        # the ADC trigger window in lockstep with the op being sent/received.
        target.loadEncryptionKey(key)
        target.loadInput(nonce)
        scope.arm()
        target.go()
        ret = scope.capture()
        if ret:
            print(f"    trace {i}: trigger timeout, skipping")
            _drain(target)
            fails += 1
            continue

        t0 = time.time()
        while not target.is_done() and time.time() - t0 < 1.0:
            time.sleep(0.001)
        if not target.is_done():
            print(f"    trace {i}: FPGA still busy, skipping")
            fails += 1
            continue
        ct = bytes(target.readOutput())

        if not args.no_verify:
            exp = fpga_expected(key, nonce)
            if ct != exp:
                print(f"    trace {i}: VERIFY FAILED (got={ct.hex()} exp={exp.hex()}) - skipping")
                fails += 1
                if fails >= args.max_fail:
                    sys.exit(f"aborting: {fails} unverified traces (sync broken?)")
                continue

        traces.append(scope.get_last_trace())
        keys.append(key)
        nonces.append(nonce)
        cts.append(ct)

        if (i + 1) % 100 == 0:
            print(f"    {i+1}/{args.num} (fails: {fails})")

    if not traces:
        sys.exit("no traces collected")

    tr = np.array(traces, dtype=np.float32)
    with h5py.File(args.output, 'w') as f:
        f.create_dataset('traces', data=tr, compression='gzip')
        f.create_dataset('keys', data=np.frombuffer(b''.join(keys), np.uint8).reshape(-1, 16))
        f.create_dataset('nonces', data=np.frombuffer(b''.join(nonces), np.uint8).reshape(-1, 16))
        f.create_dataset('ciphertexts', data=np.frombuffer(b''.join(cts), np.uint8).reshape(-1, 16))
        f.attrs['adc_samples'] = args.samples
        f.attrs['fs_hz'] = 40e6
        f.attrs['crypto_clk_hz'] = 10e6
        f.attrs['gain_db'] = 25
        f.attrs['key_mode'] = key_mode
        f.attrs['verified'] = not args.no_verify
        f.attrs['num_traces'] = tr.shape[0]
        f.attrs['source_bitstream'] = os.path.basename(args.bitstream)
    print(f"[+] Saved {tr.shape[0]} verified traces -> {args.output} (fails: {fails})")

    target.dis()
    scope.dis()


if __name__ == '__main__':
    main()
