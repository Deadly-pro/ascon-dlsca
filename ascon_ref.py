#!/usr/bin/env python3
"""ascon_ref.py — ASCON-128 oracle for the CW305 Ascon core.

Uses the official `ascon` PyPI package, validated against the vendored HDL's own
testbench vectors (ascon-hw-public/testbench/output.txt) — see _selftest().
The vendored cores compute standard ASCON-128 (r=64, a=12, b=6).

FPGA config (vivado_ascon/src/ascon_cw305_core.v):
    key/nonce 16 B, AD = 32 zero bits (l=32), PT = 32 zero bits (y=32).
    data_o = {tag[95:0], ct[31:0]}; bits shift out LSB-first, so the CW305
    register read returns ct little-endian (4 B) then the low 96 tag bits
    little-endian.
"""
import ascon

# one PT/AD length step: the core takes y=l=32 bits of (zero) AD and PT
_ADPT = b'\x00\x00\x00\x00'


def hdl_encrypt(key, nonce, ad=_ADPT, pt=_ADPT):
    """Full ASCON-128 AEAD as the FPGA core computes it. Returns (ct, tag) bytes."""
    out = ascon.encrypt(key, nonce, ad, pt)
    return out[:len(pt)], out[len(pt):]


def fpga_expected(key, nonce):
    """Expected 16-byte readback {tag[95:0], ct[31:0]} from the CW305 core.

    The core exposes the ciphertext/tag VALUES (LSB-first serial out), so the
    register read returns ct little-endian then the low 96 tag bits little-endian.
    """
    ct, tag = hdl_encrypt(key, nonce)
    return ct[::-1] + tag[4:][::-1]


def _selftest():
    """Reproduce the ascon-hw-public HDL testbench vectors (AD='ASCON', PT='ascon')."""
    vectors = [
        ('00a14b66b34c7101e798a43505a17d58', '33b1ba07991290964c7d834e82a9e9b7',
         '058d7f924a', '2ef5cd71ce2d15ba2e72719e19a7865e'),
        ('3ffa75efbd1705fa8f9ced62e5bb0be3', '9691163337dd55217ea2a6b21eaa19b2',
         'c21061905f', '77d70aaf2501e3b27c1849182d2f2149'),
        ('48cf10c0c0b094675d2ea3f3e1d2ba4f', '9b6d4051ee79e0a11e1506ea2e28a6f3',
         'b2fcca289c', '3268668d2247e66c74f38963ea4b5793'),
        ('56e759939bf9986b0a065e3c4a3a1fde', 'c55ad3708b68e88129e6bb2fd3c71165',
         '1a8da85bcb', 'ae84b851ed225aafc85d5eeaad888631'),
    ]
    ok = True
    for i, (k, n, exp_ct, exp_tag) in enumerate(vectors):
        ct, tag = hdl_encrypt(bytes.fromhex(k), bytes.fromhex(n),
                              bytes.fromhex('4153434f4e'), bytes.fromhex('6173636f6e'))
        if ct.hex() != exp_ct or tag.hex() != exp_tag:
            print(f"selftest vector {i} FAILED: ct={ct.hex()} tag={tag.hex()}")
            ok = False
    if ok:
        print(f"selftest OK: {len(vectors)}/4 HDL vectors matched")


if __name__ == '__main__':
    _selftest()
