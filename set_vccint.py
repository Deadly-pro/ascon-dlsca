#!/usr/bin/env python3
r"""set_vccint.py — set the CW305 core voltage (VCCINT) and optionally verify
the ASCON core still passes KAT at that voltage, without reflashing.

The voltage setting persists on the board supply after this script exits
(until changed or the board is power-cycled), so the Phase-2 flow is:

    python3 set_vccint.py --vcc 0.95 --kat
    python3 collect_dataset.py -n 300 -M 16 --gain 35 --no-program \
        -o Dataset/probe_v095.h5
    python3 set_vccint.py --vcc 1.00        # restore before leaving

Usage:
  python3 set_vccint.py --vcc 0.95 --kat   # set + KAT-check via AsconMux shim
  python3 set_vccint.py --read              # just read current voltage
"""
import sys, os, argparse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import chipwhisperer as cw
from ascon_ref import fpga_expected
from cw305_ascon_shim import wrap


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--vcc', type=float, help='core voltage in V (e.g. 0.95)')
    ap.add_argument('--read', action='store_true', help='only read voltage')
    ap.add_argument('--kat', action='store_true',
                    help='verify 3 random-key KATs after setting')
    args = ap.parse_args()

    # open WITHOUT programming (keeps the resident bitstream)
    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=None, fpga_id='100t', platform='cw305')
    try:
        if args.read or args.vcc is None:
            print(f'VCCINT = {target.vccint_get():.3f} V')
            return
        print(f'setting VCCINT {target.vccint_get():.3f} -> {args.vcc} V ...')
        target.vccint_set(args.vcc)
        time.sleep(0.5)
        got = target.vccint_get()
        print(f'VCCINT now {got:.3f} V')
        if abs(got - args.vcc) > 0.02:
            print('[!] readback differs from request — supply limit?')
        if args.kat:
            t = wrap(target)
            rng = np.random.default_rng(11)
            ok = 0
            for _ in range(3):
                k = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
                n = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
                t.loadEncryptionKey(k); t.loadInput(n); t.go()
                if bytes(t.readOutput()) == fpga_expected(k, n):
                    ok += 1
            print(f'KAT at {got:.3f} V: {ok}/3 '
                  f'{"PASS — core functional, timing marginal" if ok == 3 else "FAIL — raise voltage"}')
            if ok < 3:
                target.vccint_set(1.0)
                print('restored 1.0 V (safe state)')
                sys.exit(1)
    finally:
        target.dis()


if __name__ == '__main__':
    main()
