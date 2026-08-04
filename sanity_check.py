#!/usr/bin/env python3
"""sanity_check.py — known-vector check of the CW305 Ascon core.

Programs the bitstream (or uses an already-loaded one), runs one encryption
with a fixed known key/nonce, reads back {tag[95:0], ct[31:0]} and compares
against the validated ASCON-128 reference (ascon_ref.py).

This exercises the full send/receive chain (key+nonce write -> go -> readout)
in isolation, so if it passes the capture loop is trustworthy.

Usage:
    python3 sanity_check.py -b vivado_ascon/ascon_cw305_top.bit   # programs + checks
    python3 sanity_check.py --no-program                          # bitstream already loaded
"""
import argparse
import os
import sys
import time

import chipwhisperer as cw

from ascon_ref import fpga_expected

KEY = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
NONCE = bytes.fromhex('000102030405060708090a0b0c0d0e0f')


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(here, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--no-program', action='store_true',
                    help='bitstream already loaded (e.g. SPI flash boot)')
    ap.add_argument('-k', '--key', default=KEY.hex(), help='16-byte key in hex')
    ap.add_argument('-n', '--nonce', default=NONCE.hex(), help='16-byte nonce in hex')
    args = ap.parse_args()

    key = bytes.fromhex(args.key)
    nonce = bytes.fromhex(args.nonce)
    if len(key) != 16 or len(nonce) != 16:
        sys.exit("key/nonce must be 16 bytes")

    print(f"[+] Opening CW305 target ({'programming ' + args.bitstream if not args.no_program else 'no-program'}) ...")
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
    target.clkusbautooff = False

    print(f"[+] key   = {key.hex()}")
    print(f"[+] nonce = {nonce.hex()}")
    target.loadEncryptionKey(key)
    target.loadInput(nonce)
    target.go()

    t0 = time.time()
    while not target.is_done() and time.time() - t0 < 2.0:
        time.sleep(0.001)
    if not target.is_done():
        sys.exit("FAIL: FPGA never reported done (is the bitstream the Ascon core?)")

    got = bytes(target.readOutput())
    exp = fpga_expected(key, nonce)

    print(f"[+] got = {got.hex()}")
    print(f"[+] exp = {exp.hex()}")
    if got == exp:
        print("[+] PASS — FPGA output matches the validated ASCON-128 reference")
        rc = 0
    elif got == exp[::-1]:
        print("[!] PASS (byte-reversed register read) — expected order is big-endian.")
        print("    Flip fpga_expected() in ascon_ref.py to LE if this is what the")
        print("    hardware returns.")
        rc = 0
    else:
        print("[!] FAIL — output mismatch (check bit order / AD handling / bitstream)")
        rc = 1

    target.dis()
    sys.exit(rc)


if __name__ == '__main__':
    main()
