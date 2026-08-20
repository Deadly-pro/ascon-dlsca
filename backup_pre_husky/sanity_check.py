#!/usr/bin/env python3
"""sanity_check.py — known-vector verification of the CW305 Ascon-128 core.

Programs the bitstream (or uses an already-loaded one), runs multiple
test vectors with known key/nonce pairs, reads back the ciphertext,
tag, and combined readout, and compares against the standard ASCON-128
reference (ascon_ref.py).

Usage:
    python3 sanity_check.py -b vivado_ascon/ascon_cw305_top.bit
    python3 sanity_check.py --no-program
    python3 sanity_check.py -k <hex> -n <hex>   # single custom vector
"""
import argparse
import os
import sys

import chipwhisperer as cw

from ascon_ref import ascon_encrypt, fpga_expected
from cw305_ascon_shim import wrap

# (key_hex, nonce_hex, ct_hex, tag_hex, ro_hex)
VECTORS = [
    ("000102030405060708090a0b0c0d0e0f", "000102030405060708090a0b0c0d0e0f",
     "19378c6a", "19c8f96a6b6a4fe5caa719a760c78aba",
     "19c8f96a6b6a4fe5caa719a719378c6a"),
    ("deadbeefcafebabe0001020304050607", "102030405060708090a0b0c0d0e0f000",
     "d1dc9341", "94f0b9bc9fa873085c828fe648c34f28",
     "94f0b9bc9fa873085c828fe6d1dc9341"),
    ("00000000000000000000000000000000", "00000000000000000000000000000000",
     "9761cfb5", "3e2a56698ec81e2e053815e880d27d7d",
     "3e2a56698ec81e2e053815e89761cfb5"),
    ("ffffffffffffffffffffffffffffffff", "ffffffffffffffffffffffffffffffff",
     "864ebb5a", "6a9d3f7ad41bbe299bf436206894108b",
     "6a9d3f7ad41bbe299bf43620864ebb5a"),
    ("0123456789abcdef0123456789abcdef", "fedcba9876543210fedcba9876543210",
     "4dc496f3", "502074376152408dc9d4707221552e27",
     "502074376152408dc9d470724dc496f3"),
]


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(here, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--no-program', action='store_true')
    ap.add_argument('-k', '--key', default=None, help='16-byte key hex (single-shot)')
    ap.add_argument('-n', '--nonce', default=None, help='16-byte nonce hex (single-shot)')
    args = ap.parse_args()

    print(f"[+] Opening CW305 target "
          f"({'programming ' + args.bitstream if not args.no_program else 'no-program'})...")
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
    t = wrap(target)

    if args.key:
        # single-shot custom: compute expected on the fly
        key = bytes.fromhex(args.key)
        nonce = bytes.fromhex(args.nonce)
        if len(key) != 16 or len(nonce) != 16:
            sys.exit("key/nonce must be 16 bytes")

        t.loadEncryptionKey(key)
        t.loadInput(nonce)
        t.go()
        got_ro = bytes(t.readOutput())
        got_ct = bytes(target.fpga_read(0x09, 16))[:4]
        got_tag = bytes(target.fpga_read(0x0c, 16))
        exp_ct_tag = ascon_encrypt(key, nonce, b'\x00\x00\x00\x00', b'\x00\x00\x00\x00')
        exp_ct, exp_tag = exp_ct_tag[:4], exp_ct_tag[4:]
        exp_ro = fpga_expected(key, nonce)

        print(f"{'✓' if got_ct==exp_ct else '✗'} CT  = {got_ct.hex()}")
        print(f"{'✓' if got_tag==exp_tag else '✗'} TAG = {got_tag.hex()}")
        print(f"{'✓' if got_ro==exp_ro else '✗'} RO  = {got_ro.hex()}")
        target.dis()
        sys.exit(0 if (got_ro == exp_ro) else 1)

    # --- batch mode: run VECTORS against lookup table ---
    failed = 0
    for ki, (k_hex, n_hex, exp_ct_hex, exp_tag_hex, exp_ro_hex) in enumerate(VECTORS):
        key = bytes.fromhex(k_hex)
        nonce = bytes.fromhex(n_hex)

        t.loadEncryptionKey(key)
        t.loadInput(nonce)
        t.go()

        got_ro = bytes(t.readOutput())
        got_ct = bytes(target.fpga_read(0x09, 16))[:4]
        got_tag = bytes(target.fpga_read(0x0c, 16))

        ok_ct  = got_ct.hex() == exp_ct_hex
        ok_tag = got_tag.hex() == exp_tag_hex
        ok_ro  = got_ro.hex() == exp_ro_hex

        print(f"\n--- Vector {ki+1} ---")
        print(f"  K  = {k_hex}")
        print(f"  N  = {n_hex}")
        print(f"  CT  {'✓' if ok_ct else '✗'} fpga={got_ct.hex()} exp={exp_ct_hex}")
        print(f"  TAG {'✓' if ok_tag else '✗'} fpga={got_tag.hex()}")
        print(f"  RO  {'✓' if ok_ro else '✗'} fpga={got_ro.hex()} exp={exp_ro_hex}")
        if ok_ct and ok_tag and ok_ro:
            print(f"  PASS")
        else:
            if not ok_tag:
                print(f"       TAG exp={exp_tag_hex}")
            failed += 1

    target.dis()

    if failed:
        print(f"\n[!] {failed}/{len(VECTORS)} FAILED")
        sys.exit(1)
    else:
        print(f"\n[+] ALL {len(VECTORS)}/{len(VECTORS)} PASSED")


if __name__ == '__main__':
    main()
