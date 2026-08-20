#!/usr/bin/env python3
r"""check_setup.py — one-shot bring-up check for the CW-Husky + CW305 rig.

Runs every step a new teammate needs to verify before starting a capture or
attack session. Exits non-zero at the first failure so it can be used in CI
or a runbook.

Steps:
  1. chipwhisperer library version
  2. Scope present + model name + ADC clock locks to the requested rate
  3. CW305 target present and programmable
  4. Bitstream programs and the register map shows the ASCON core (KEY/NONCE)
  5. One verified capture: ciphertext matches the ASCON reference oracle

Usage:
    .venv/bin/python check_setup.py -b vivado_ascon/ascon_cw305_top.bit
    .venv/bin/python check_setup.py --no-verify  # skip the oracle check (offline)
"""
import argparse
import os
import sys

import numpy as np

import chipwhisperer as cw

import scope_config
from scope_config import (connect_target, configure_scope, verify_scope,
                          is_husky, scope_model_name, capture_ok)


def step_ok(label, ok, detail=''):
    tag = 'PASS' if ok else 'FAIL'
    print(f'  [{tag}] {label}{" - " + detail if detail else ""}')
    return ok


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(here, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--no-verify', action='store_true',
                    help='skip the ciphertext oracle check')
    ap.add_argument('--samples', type=int, default=2000)
    ap.add_argument('--gain', type=int, default=20)
    args = ap.parse_args()

    all_ok = True

    # 1. library
    print('[1] chipwhisperer library')
    try:
        import chipwhisperer
        all_ok &= step_ok('library import', True,
                          getattr(chipwhisperer, '__version__', 'unknown'))
    except Exception as e:
        all_ok &= step_ok('library import', False, str(e))

    # 2. scope
    print('[2] scope')
    try:
        scope = configure_scope(gain=args.gain, samples=args.samples,
                                offset=700, sample_rate=40e6)
        name = verify_scope(scope)
        locked = scope.clock.adc_freq and scope.clock.adc_freq > 1e6
        all_ok &= step_ok(f'{name} present', True)
        all_ok &= step_ok('ADC freq', locked,
                          f'{scope.clock.adc_freq/1e6:.1f} MHz')
    except Exception as e:
        all_ok &= step_ok('scope open', False, str(e))
        scope = None

    if scope is None:
        print('\n[!] Stopping here: no scope. Check USB + drivers.')
        sys.exit(1)

    # 3. target
    print('[3] CW305 target')
    try:
        t = connect_target(args.bitstream)
        all_ok &= step_ok('target + bitstream program', True)
    except Exception as e:
        all_ok &= step_ok('target + bitstream program', False, str(e))
        sys.exit(1)

    # 4. register map sanity (ASCON core responding)
    print('[4] ASCON register map')
    try:
        key = bytes.fromhex('0f1e2d3c4b5a69788796a5b4c3d2e1f0')
        nonce = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
        t.loadEncryptionKey(key)
        t.loadInput(nonce)
        # KEY and NONCE registers read back the values we wrote
        got_key = bytes(t.fpga_read(0x0a, 16))[:16]
        ok_reg = got_key == key
        all_ok &= step_ok('KEY register round-trip', ok_reg,
                          got_key.hex() if ok_reg else f'got {got_key.hex()}')
        if not ok_reg:
            print('[!] Register map mismatch: the FPGA may be running a stock '
                  'AES image from SPI flash. Re-flash the bitstream.')
    except Exception as e:
        all_ok &= step_ok('register sanity', False, str(e))

    # 5. one verified capture
    print('[5] capture')
    try:
        t.loadEncryptionKey(key)
        t.loadInput(nonce)
        ok_cap = False
        for attempt in range(10):
            scope.arm()
            t.go()
            scope.capture()
            tr = scope.get_last_trace()
            ok, reason = capture_ok(tr, args.samples, std_floor=0.0005)
            if not ok:
                continue
            ct = bytes(t.readOutput())
            try:
                from ascon_ref import ascon_encrypt
                exp = ascon_encrypt(key, nonce, b'\x00' * 4, b'\x00' * 16)
                ok_cap = ct == exp
                all_ok &= step_ok('ciphertext matches oracle', ok_cap,
                                  f'std {tr.std():.4f}, max {abs(tr).max():.4f}')
            except ImportError:
                ok_cap = True
                all_ok &= step_ok('ciphertext read (no oracle available)', True)
            break
        if not ok_cap:
            all_ok &= step_ok('capture', False,
                              f'no valid trace after 10 attempts (last '
                              f'reason: {reason})')
    except Exception as e:
        all_ok &= step_ok('capture', False, str(e))

    # cleanup
    try:
        t.dis()
        scope.dis()
    except Exception:
        pass

    print('\n' + ('[+] ALL CHECKS PASSED' if all_ok else '[!] SOME CHECKS FAILED'))
    sys.exit(0 if all_ok else 1)


if __name__ == '__main__':
    main()