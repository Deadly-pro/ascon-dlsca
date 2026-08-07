#!/usr/bin/env python3
r"""live_query.py — single-trace fixed-key capture primitive for ACPPA.

Board-side half of the adaptive closed loop (training/adaptive.py). Programs
the CW305 once, loads ONE fixed (unknown-to-the-selection-logic) key, then
answers per-query: set nonce -> arm ADC -> go -> capture one trace -> read
ciphertext/tag. No HDF5, no batch.

Alignment/normalization is NOT done here — adaptive.py preprocesses the trace
against the profiling npz's stored reference so live traces see identical
features to the training data.

Verification is full-key only: a single column's 2 recovered key bits cannot
be checked against ciphertext (the whole key drives the output). After all 64
columns' bits are recovered, assemble the key and call verify_key(), which
re-encrypts a fresh query and compares against ascon_ref.

Usage (imported by adaptive.py; also runnable standalone):
    python3 live_query.py --key <hex> --nonce <hex>     # one-shot sanity
"""
import argparse
import os
import sys

import chipwhisperer as cw

from ascon_ref import ascon_encrypt
from cw305_ascon_shim import wrap


class LiveQuery:
    def __init__(self, bitstream, key, samples=2000, gain=20, program=True):
        assert len(key) == 16
        self.target = cw.target(None, cw.targets.CW305, force=True,
                                bsfile=None if not program else bitstream,
                                fpga_id='100t', platform='cw305')
        if program:
            self.target.vccint_set(1.0)
            self.target.pll.pll_enable_set(True)
            self.target.pll.pll_outenable_set(False, 0)
            self.target.pll.pll_outenable_set(True, 1)
            self.target.pll.pll_outenable_set(False, 2)
            self.target.pll.pll_outfreq_set(10e6, 1)
        self.target.clkusbautooff = True
        self.target.clksleeptime = 1
        self.target.fpga_write(0x00, [0x19])   # enable tio_clkout
        self.t = wrap(self.target)
        self.t.loadEncryptionKey(key)

        self.scope = cw.scope()
        self.scope.gain.db = gain
        self.scope.adc.samples = samples
        self.scope.adc.offset = 0
        self.scope.clock.adc_src = 'clkgen_x4'
        self.scope.clock.clkgen_freq = 40e6
        self.scope.clock.reset_adc()
        self.scope.trigger.triggers = 'tio4'

    def query(self, nonce):
        """One adaptive query: (nonce 16 bytes) -> (trace, ciphertext+tag).

        Returns (None, None) if the capture timed out (caller retries).
        """
        self.t.loadInput(nonce)
        self.scope.arm()
        self.t.go()
        if self.scope.capture():
            return None, None
        ct = bytes(self.t.readOutput())
        trace = self.scope.get_last_trace()
        return trace, ct

    def verify_key(self, candidate_key, nonce=None):
        """Full-key check: encrypt a fresh query under the candidate and compare.

        Returns (bool, ct_oracle, ct_fpga).
        """
        if len(candidate_key) != 16:
            return False, None, None
        nonce = os.urandom(16) if nonce is None else nonce
        self.t.loadEncryptionKey(candidate_key)
        self.t.loadInput(nonce)
        self.t.go()
        got = bytes(self.t.readOutput())
        exp = ascon_encrypt(candidate_key, nonce, b'\x00' * 4, b'\x00' * 16)
        ok = got == exp
        return ok, exp.hex(), got.hex()

    def close(self):
        try:
            self.target.dis()
        except Exception:
            pass
        try:
            self.scope.dis()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--key', required=True, help='16-byte fixed key hex')
    ap.add_argument('--nonce', required=True, help='16-byte nonce hex')
    args = ap.parse_args()

    key = bytes.fromhex(args.key)
    nonce = bytes.fromhex(args.nonce)
    if len(key) != 16 or len(nonce) != 16:
        sys.exit('key/nonce must be 16 bytes hex')

    lq = LiveQuery(args.bitstream, key)
    try:
        trace, ct = lq.query(nonce)
        if trace is None:
            sys.exit('trigger timeout')
        ok, exp, got = lq.verify_key(key, nonce)
        print(f'trace: {len(trace)} samples, range '
              f'[{trace.min():.3f}, {trace.max():.3f}] V')
        print(f'ct: got={got} exp={exp} -> {"PASS" if ok else "FAIL"}')
    finally:
        lq.close()


if __name__ == '__main__':
    main()
