#!/usr/bin/env python3
r"""dbg_extclk.py — why does extclk capture come back flat?

The extclk PLL now locks correctly (clkgen_src=extclk, adc_freq=40 MHz
derived from the 10 MHz crypto clock), but traces are flat (std ~0).
That means the ADC is sampling a quiet window, or has no clock at all.

This probe separates the causes:
  1. Is tio_clkout actually toggling?  (frequency counter / extclk monitor)
  2. System-clock capture at the same settings: does it show signal?
     -> if yes, the pipeline is fine and only the extclk timing is wrong
  3. extclk capture at several ADC offsets: does any offset find the burst?
     -> locates where the crypto activity actually lands in extclk mode

Usage:
  .venv/bin/python board_session/dbg_extclk.py
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import chipwhisperer as cw                      # noqa: E402
from scope_config import connect_target, configure_scope  # noqa: E402
from cw305_ascon_shim import wrap               # noqa: E402

KEY = bytes.fromhex('0123456789abcdef0123456789abcdef')
BS = os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit')


def grab(scope, target, nonce, off):
    scope.adc.offset = off
    scope.arm()
    target.loadInput(nonce)
    target.go()
    scope.capture()
    tr = scope.get_last_trace()
    if tr is None or tr.size == 0:
        return None
    return tr


def main():
    print('[1] connect target (PLL + tio_clkout)')
    t = connect_target(BS, crypto_hz=10e6, program=True)
    raw = t._t
    time.sleep(0.5)                      # let the target PLL settle
    # re-assert tio_clkout enable in case programming cleared it
    raw.fpga_write(0x00, [0x19])
    time.sleep(0.3)

    print('[2] system-clock baseline (should show signal)')
    scope = configure_scope(gain=50, samples=2000, offset=700, sample_rate=40e6,
                            extclk=False, crypto_hz=10e6)
    print(f'    clkgen_src={scope.clock.clkgen_src} '
          f'adc_freq={scope.clock.adc_freq/1e6:.2f}MHz')
    nonce = os.urandom(16)
    stds = []
    for _ in range(5):
        tr = grab(scope, t, nonce, 700)
        if tr is not None:
            stds.append(float(tr.std()))
    print(f'    system-clock trace std: {[round(s,5) for s in stds]}')
    scope.dis()

    print('[3] extclk: is the incoming clock seen?')
    scope = configure_scope(gain=50, samples=2000, offset=700, sample_rate=40e6,
                            extclk=True, crypto_hz=10e6)
    print(f'    clkgen_src={scope.clock.clkgen_src} '
          f'adc_freq={scope.clock.adc_freq/1e6:.2f}MHz '
          f'adc_mul={scope.clock.adc_mul}')
    try:
        scope.clock.pll.display_settings()
    except Exception as e:
        print(f'    (display_settings unavailable: {e})')

    print('[4] extclk at several offsets — where is the burst?')
    best = None
    for off in (0, 50, 100, 200, 400, 700, 1000, 1500, 2000, 2500):
        vals = []
        for _ in range(3):
            tr = grab(scope, t, os.urandom(16), off)
            if tr is not None:
                vals.append(float(tr.std()))
        if vals:
            m = max(vals)
            print(f'    offset {off:5d}: std {[round(v,5) for v in vals]}')
            if best is None or m > best[1]:
                best = (off, m)
    if best:
        print(f'    -> best offset {best[0]} with std {best[1]:.5f}')
        if best[1] < 0.001:
            print('    FLAT EVERYWHERE: the ADC has no clock (tio_clkout not '
                  'toggling) or the core is not running under extclk.')
        else:
            print(f'    signal found at offset {best[0]} — use that for extclk '
                  'captures (system clock used 700).')
    scope.dis()
    t.close()


if __name__ == '__main__':
    main()
