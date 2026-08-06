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


class AsconMux:
    def __init__(self, target):
        self._t = target

    def loadEncryptionKey(self, key):
        self._t.fpga_write(REG_KEY, list(key))

    def loadInput(self, nonce):
        self._t.fpga_write(REG_NONCEIN, list(nonce))
        self._t.fpga_write(REG_TEXTIN, [0] * 16)
        self._t.fpga_write(REG_TEXTIN_BUF, [0] * 16)
        self._t.fpga_write(REG_VALID_AD, [AD_BYTES])
        self._t.fpga_write(REG_VALID_MSG, [PT_BYTES])

    def go(self):
        self._t.go()

    def is_done(self):
        return True  # core finishes in ~10µs at 10MHz; ADC capture is ~ms

    def readOutput(self):
        time.sleep(0.01)  # safety margin for core completion
        ct = bytes(self._t.fpga_read(REG_CIPHEROUT, 16))
        tag = bytes(self._t.fpga_read(REG_TAGOUT, 16))
        return tag[:12] + ct[:4]

    def __getattr__(self, name):
        return getattr(self._t, name)


def wrap(target):
    return AsconMux(target)
