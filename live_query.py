#!/usr/bin/env python3
r"""live_query.py — single-trace fixed-key capture primitive for ACPPA.

Board-side half of the adaptive closed loop (training/adaptive.py). Programs
the CW305 once, loads ONE fixed (unknown-to-the-selection-logic) key, then
answers per-query: set nonce -> arm ADC -> go -> capture one trace -> read
ciphertext/tag. No HDF5, no batch.

Scope setup is delegated to scope_config.py, which auto-detects the capture
hardware (CW-Husky vs CW-Lite/CW-Pro) and applies the correct clock settings.

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

from ascon_ref import fpga_expected
from cw305_ascon_shim import wrap
from scope_config import (connect_target, configure_scope,
                          setup_scope_clock, is_husky, scope_model_name)


class LiveQuery:
    # NOTE (Aug 24): defaults retuned for the NEW unmasked rprimas core —
    # crypto completes in ~50-90 cycles (~5-9 us) vs ~3 ms for the old serial
    # masked core. At 40 MS/s that is ~200-360 samples starting AT the
    # trigger, so offset must be small.
    def __init__(self, bitstream, key, samples=1200, gain=-2, offset=0,
                 std_floor=0.001, program=True, extclk=False, crypto_mhz=10.0):
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
            self.target.pll.pll_outfreq_set(float(crypto_mhz) * 1e6, 1)
        self.target.clkusbautooff = True
        self.target.clksleeptime = 1
        self.target.fpga_write(0x00, [0x19])   # enable tio_clkout
        self.t = wrap(self.target)
        self.key = bytes(key)
        self.t.loadEncryptionKey(self.key)

        self.scope = configure_scope(gain=gain, samples=samples, extclk=extclk,
                                     offset=offset, sample_rate=40e6,
                                     crypto_hz=crypto_mhz*1e6)
        self.std_floor = std_floor

    def set_key(self, key):
        """Rotate the FPGA key in place (no re-program, no scope re-init).
        Used by the live training loop to serve a fresh key per episode."""
        assert len(key) == 16
        self.key = bytes(key)
        self.t.loadEncryptionKey(self.key)

    def query(self, nonce, _strikes=0):
        """One adaptive query: (nonce 16 bytes) -> (trace, ciphertext+tag).

        Returns (None, None) if the capture timed out or came back flat
        (std < std_floor — the capture() return flag is unreliable on this
        harness, so judge by content); caller retries the same nonce.

        Short captures (ADC clock drift: trace.size != samples) are treated as
        a clock state fault: re-run reset_adc() up to 3 times to re-sync the
        ADC PLL, then retry. Repeated failure returns None so the caller can
        fall back to a full scope re-init.
        """
        self.t.loadInput(nonce)
        self.scope.arm()
        self.t.go()
        self.scope.capture()
        trace = self.scope.get_last_trace()
        if trace is None or trace.size != self.scope.adc.samples:
            if _strikes < 3:
                self.scope.clock.reset_adc()
                return self.query(nonce, _strikes + 1)
            return None, None
        if trace.std() < self.std_floor:
            return None, None
        ct = bytes(self.t.readOutput())
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
        # FPGA readback is tag[:12]+ct[:4] for AD=4/PT=4 (single-block adapter);
        # fpga_expected encodes exactly that, so compare against it directly.
        exp = fpga_expected(candidate_key, nonce)
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
            sys.exit('trigger timeout or flat capture')
        ok, exp, got = lq.verify_key(key, nonce)
        print(f'scope      : {scope_model_name(lq.scope)}')
        print(f'trace      : {len(trace)} samples, range '
              f'[{trace.min():.3f}, {trace.max():.3f}] V')
        print(f'ct         : got={got} exp={exp} -> {"PASS" if ok else "FAIL"}')
    finally:
        lq.close()


if __name__ == '__main__':
    main()