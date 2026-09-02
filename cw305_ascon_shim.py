#!/usr/bin/env python3
r"""cw305_ascon_shim.py — map old CW305 API to compact-yet-fast-ascon register layout.

REGS: KEY=0x0a, TEXTIN=0x06(AD data), NONCEIN=0x0d, CipherOut=0x09, CaptOut=0x0c,
      TEXTIN_BUF=0x12(PT data), VALID_AD=0x10, VALID_MSG=0x11
"""
import time

REG_KEY        = 0x0a
REG_TEXTIN     = 0x06
REG_NONCEIN    = 0x0d
REG_CIPHEROUT  = 0x09
REG_TAGOUT     = 0x0c
REG_TEXTIN_BUF = 0x12
REG_VALID_AD   = 0x10
REG_VALID_MSG  = 0x11

AD_BYTES = 4
PT_BYTES = 4


def _w32rev(b):
    r"""Byte-reverse each 32-bit word of a 16-byte value.

    The CW305 register file packs written bytes little-endian (byte k ->
    reg[8k+:8]) while the LWC core expects big-endian 32-bit words, so raw
    writes reach the core with every word byte-reversed — board-verified:
    the core computes encryption(w32rev(K), w32rev(N)). Reversing here makes
    the core see the key/nonce exactly as the host intends, so the oracle,
    labels, attack assembly and fpga_expected all work in the natural
    byte order. (AD/PT are fixed 4 zero bytes: invariant, no transform.)
    """
    return bytes(x for i in range(0, len(b), 4) for x in b[i:i + 4][::-1])


class AsconMux:
    def __init__(self, target):
        self._t = target

    def loadEncryptionKey(self, key):
        self._t.fpga_write(REG_KEY, list(_w32rev(bytes(key))))

    def loadInput(self, nonce):
        self._t.fpga_write(REG_NONCEIN, list(_w32rev(bytes(nonce))))
        self._t.fpga_write(REG_TEXTIN, [0] * 16)
        self._t.fpga_write(REG_TEXTIN_BUF, [0] * 16)
        self._t.fpga_write(REG_VALID_AD, [AD_BYTES])
        self._t.fpga_write(REG_VALID_MSG, [PT_BYTES])

    def go(self):
        self._t.go()

    def is_done(self):
        return True  # core finishes in ~10µs at 10MHz; ADC capture is ~ms

    def readOutput(self):
        # Core finishes in ~35-85 cycles (~35 us at 2.5 MHz); two host
        # fpga_read round-trips exceed this, so no sleep is needed at any
        # crypto clock we use. Verified by KAT readback in sanity_check.
        ct = bytes(self._t.fpga_read(REG_CIPHEROUT, 16))
        tag = bytes(self._t.fpga_read(REG_TAGOUT, 16))
        return tag[:12] + ct[:4]

    def __getattr__(self, name):
        return getattr(self._t, name)


def wrap(target):
    return AsconMux(target)
