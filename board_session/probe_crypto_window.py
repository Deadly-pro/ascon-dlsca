#!/usr/bin/env python3
r"""probe_crypto_window.py — where does the crypto actually land in time?

The AGENTS notes say the unmasked core completes encryption in ~3.5-8.5 us
(~35-85 cycles at 10 MHz).  All our sprint captures used scope.adc.offset =
700, i.e. they SKIP 700 samples = 17.5 us at 40 MS/s before recording.  If
the trigger fires when the core starts, the whole operation finished before
the window opened and every trace except a settling DC tail is empty.

This probe captures single traces at a ladder of small offsets (with a gain
low enough that the trigger transient does not rail) and prints the energy
profile of each, so we can see where - if anywhere - a burst sits.

Usage:
  .venv/bin/python board_session/probe_crypto_window.py
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scope_config import connect_target, configure_scope  # noqa: E402

BS = os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit')
NS = 2000


def main():
    t = connect_target(BS, crypto_hz=10e6, program=True)
    raw = t._t
    time.sleep(0.4)
    raw.fpga_write(0x00, [0x19])          # keep tio_clkout enabled
    time.sleep(0.2)

    # low gain: we want to SEE the transient shape, not saturate on it
    scope = configure_scope(gain=20, samples=NS, offset=0, sample_rate=40e6,
                            extclk=False, crypto_hz=10e6)
    print(f'[+] gain 20, {NS} samples @ 40 MS/s = {NS/40e6*1e6:.0f} us window')
    print(f'[+] crypto at 10 MHz -> one clock cycle = 4 samples\n')

    rng = np.random.default_rng(1)
    for off in (0, 50, 100, 200, 300, 400, 600, 700):
        scope.adc.offset = off
        traces = []
        for _ in range(6):
            scope.arm()
            t.loadInput(rng.integers(0, 256, 16, dtype=np.uint8))
            t.go()
            scope.capture()
            tr = scope.get_last_trace()
            if tr is not None and tr.size:
                traces.append(np.asarray(tr, dtype=np.float64))
        if not traces:
            print(f'  offset {off:4d}: no traces')
            continue
        A = np.vstack(traces)
        m = A.mean(0)
        sd = A.std(0)
        # energy in 4-sample (one clock cycle) blocks
        nb = 20
        prof = [f'{np.abs(m[i:i+nb]).mean():.4f}' for i in range(0, 400, nb)]
        print(f'  offset {off:4d} ({off/40e6*1e6:6.2f} us): '
              f'mean[0:400] blocks = {" ".join(prof)}')
        print(f'                 overall std {A.std():.5f}  '
              f'max|mean| {np.abs(m).max():.4f} at {np.abs(m).argmax()}')

    scope.dis()
    t.close()
    print('\nIf a distinct burst sits at some offset, THAT is the crypto window '
          'and all sprint captures at offset 700 missed it.')


if __name__ == '__main__':
    main()
