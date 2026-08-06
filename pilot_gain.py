#!/usr/bin/env python3
"""pilot_gain.py — pre-collection hardware calibration pilot.

Implements the fix sequence (gain -> ADC sync -> clock verify) on a small
batch before bulk capture.

  1. GAIN SWEEP: for programmable gain in {25, 15, 5, 0, -5}, capture ~5
     traces and report true peak amplitude (not just SNR). Target: max abs
     <= 0.35 V (70% of the +/-0.5 V ADC rail) so nothing clips.
     NOTE: a fixed ~20 dB external/hardware stage is always in the path,
     so the *programmable* gain must be much lower than the old 25 dB.

  2. ADC SYNC: switch adc_src to extclk_x4 (ADC clocked from tio_clkout =
     the crypto clock via ODDR) and confirm captures still succeed with a
     sample count the ADC buffer handles (try 24000 -> 20000 -> 16000).

  3. CLOCK VERIFY: read back the CDCE906 PLL registers via
     target.pll.pllread(1) / pll_outfreq_get(1) to get the *actual* crypto
     clock, independent of the "10 MHz" label in the metadata.

Usage:
    python3 pilot_gain.py -b vivado_ascon/ascon_cw305_top.bit
"""
import argparse
import os
import sys
import time

import numpy as np
import chipwhisperer as cw

from ascon_ref import batch_fpga_expected
from cw305_ascon_shim import wrap

GAIN_CANDIDATES = [25, 15, 5, 0, -5]
TRACES_PER_GAIN = 5


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(here, 'vivado_ascon', 'ascon_cw305_top.bit'))
    args = ap.parse_args()

    print("[+] Opening CW305 target ...")
    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=args.bitstream, fpga_id='100t', platform='cw305')
    target.vccint_set(1.0)
    target.pll.pll_enable_set(True)
    target.pll.pll_outenable_set(False, 0)
    target.pll.pll_outenable_set(True, 1)
    target.pll.pll_outenable_set(False, 2)
    target.pll.pll_outfreq_set(10e6, 1)
    target.clkusbautooff = True
    target.clksleeptime = 1
    t = wrap(target)

    scope = cw.scope()
    scope.clock.adc_src = 'clkgen_x4'
    scope.clock.clkgen_freq = 40e6
    scope.clock.reset_adc()
    scope.trigger.triggers = 'tio4'
    scope.adc.offset = 0

    # ---- 3. CLOCK VERIFY first (cheap, no ADC needed) ----
    print("\n=== 3. PLL / crypto clock readback ===")
    try:
        n, m, outdiv = target.pll.pllread(1)
        freq = target.pll.pll_outfreq_get(1)
        print(f"  PLL1: N={n} M={m} outdiv={outdiv}  -> {freq/1e6:.3f} MHz "
              f"(configured 10 MHz)")
    except Exception as e:
        print(f"  pllread failed: {e}")

    # ---- 1. GAIN SWEEP ----
    print("\n=== 1. Gain sweep (programmable, +~20 dB fixed in path) ===")
    print(f"  {'gain':>5} {'peak_abs':>10} {'max':>8} {'min':>8} {'std':>8}  verdict")
    best_gain = None
    for gain in GAIN_CANDIDATES:
        scope.gain.db = gain
        scope.adc.samples = 5000
        peaks = []
        ok = 0
        for i in range(TRACES_PER_GAIN):
            key = os.urandom(16)
            nonce = os.urandom(16)
            exp = batch_fpga_expected([(key, nonce)])[0]
            t.loadEncryptionKey(key)
            t.loadInput(nonce)
            scope.arm()
            t.go()
            ret = scope.capture()
            got = t.readOutput()
            if not ret and got == exp:
                ok += 1
            trace = scope.get_last_trace()
            peaks.append(np.abs(trace).max())
        peak_abs = float(np.mean(peaks))
        verdict = "CLIP!" if peak_abs > 0.45 else ("OK" if peak_abs <= 0.35 else "warm")
        if peak_abs <= 0.35:
            best_gain = gain
        tr = scope.get_last_trace()
        print(f"  {gain:>5} {peak_abs:>10.4f} {tr.max():>8.4f} {tr.min():>8.4f} "
              f"{tr.std():>8.4f}  {verdict} (verify {ok}/{TRACES_PER_GAIN})")

    if best_gain is None:
        print("\n[!] No gain setting gave peak <= 0.35V — signal still too hot.")
        print("    Check the fixed stage or add external attenuation.")
        best_gain = GAIN_CANDIDATES[-1]

    # ---- 2. ADC SYNC (extclk_x4) + buffer check ----
    print("\n=== 2. ADC sync: extclk_x4 (crypto-clock-locked) ===")
    scope.gain.db = best_gain
    ok_samples = None
    for samples in (24000, 20000, 16000, 12000):
        scope.adc.samples = samples
        scope.clock.adc_src = 'extclk_x4'
        scope.clock.reset_adc()
        good = 0
        for i in range(3):
            key = os.urandom(16)
            nonce = os.urandom(16)
            exp = batch_fpga_expected([(key, nonce)])[0]
            t.loadEncryptionKey(key)
            t.loadInput(nonce)
            scope.arm()
            t.go()
            ret = scope.capture()
            got = t.readOutput()
            if not ret and got == exp:
                good += 1
        print(f"  samples={samples}: verify {good}/3")
        if good == 3:
            ok_samples = samples
            break

    if ok_samples is None:
        print("\n[!] extclk_x4 not stable at any sample count — "
              "stick with clkgen_x4 + manual alignment")
        sys.exit(1)

    # Final trace stats at chosen settings
    scope.adc.samples = ok_samples
    key = os.urandom(16)
    nonce = os.urandom(16)
    exp = batch_fpga_expected([(key, nonce)])[0]
    t.loadEncryptionKey(key)
    t.loadInput(nonce)
    scope.arm()
    t.go()
    ret = scope.capture()
    got = t.readOutput()
    tr = scope.get_last_trace()
    print(f"\n[+] RECOMMENDED SETTINGS:")
    print(f"    gain     = {best_gain} dB  (programmable; +~20 dB fixed)")
    print(f"    adc_src  = extclk_x4  (locked to crypto clock)")
    print(f"    samples  = {ok_samples}")
    print(f"    peak_abs = {np.abs(tr).max():.4f} V  ({'in rails' if np.abs(tr).max()<0.45 else 'CLIPPING!'})")
    print(f"    verify   = {'PASS' if got == exp else 'FAIL'}")
    print(f"    crypto   = {freq/1e6:.3f} MHz actual (pllread)")

    target.dis()
    scope.dis()


if __name__ == '__main__':
    main()
