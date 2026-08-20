#!/usr/bin/env python3
r"""pick_gain.py — pick the best scope gain at the pipeline config.

The pilot's "recommended" is measured at extclk_x4/24000 samples, which is
NOT the collection config (clkgen_x4, 2000 samples, offset 700). This probe
tests the actual config: for each candidate gain, 10 captures, reports
good/clip/flat counts and mean std. Prints the verdict + the exact
collect_dataset command to run next.
"""
import argparse
import os
import sys

import numpy as np

import chipwhisperer as cw

from cw305_ascon_shim import wrap


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(here, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--gains', type=str, default='20,15,10,5,0,-5',
                    help='comma-separated candidate gains')
    ap.add_argument('--n', type=int, default=10, help='captures per gain')
    args = ap.parse_args()
    gains = [int(g) for g in args.gains.split(',')]

    t = cw.target(None, cw.targets.CW305, force=True, bsfile=args.bitstream,
                  fpga_id='100t', platform='cw305')
    t.vccint_set(1.0)
    t.pll.pll_enable_set(True)
    t.pll.pll_outenable_set(False, 0)
    t.pll.pll_outenable_set(True, 1)
    t.pll.pll_outenable_set(False, 2)
    t.pll.pll_outfreq_set(10e6, 1)
    t.fpga_write(0x00, [0x19])
    w = wrap(t)
    w.loadEncryptionKey(bytes.fromhex('0f1e2d3c4b5a69788796a5b4c3d2e1f0'))
    w.loadInput(bytes.fromhex('000102030405060708090a0b0c0d0e0f'))

    s = cw.scope()
    s.adc.samples = 2000
    s.adc.offset = 700
    s.clock.adc_src = 'clkgen_x4'
    s.clock.clkgen_freq = 40e6
    s.clock.reset_adc()
    s.trigger.triggers = 'tio4'

    # ADC clock sanity: after a replug the scope can come up with adc_freq=0
    # (clock PLL not locked), which makes capture() divide by zero. Re-run
    # reset_adc() up to a few times; if it stays 0, report and exit cleanly.
    for attempt in range(5):
        if s.clock.adc_freq and s.clock.adc_freq > 1e6:
            break
        print(f'[!] adc_freq bad ({s.clock.adc_freq}) — re-syncing ADC clock '
              f'(attempt {attempt + 1}/5)')
        s.clock.reset_adc()
    if not s.clock.adc_freq or s.clock.adc_freq <= 1e6:
        print(f'[!] ADC clock failed to lock (adc_freq={s.clock.adc_freq}). '
              f'Re-seat the CW-Lite USB and re-run.')
        t.dis()
        s.dis()
        sys.exit(2)
    print(f'[+] adc_freq = {s.clock.adc_freq/1e6:.1f} MHz')

    print(f"{'gain':>5} {'good':>5} {'clips':>5} {'flats':>5}  verdict")
    results = {}
    for gain in gains:
        s.gain.db = gain
        stds, clips, flats = [], 0, 0
        for _ in range(args.n):
            s.arm()
            w.go()
            s.capture()
            tr = s.get_last_trace()
            if tr is None or tr.size != 2000 or tr.std() < 0.01:
                flats += 1
                continue
            if np.abs(tr).max() > 0.49:
                clips += 1
                continue
            stds.append(float(tr.std()))
        nz = len(stds)
        if nz:
            std = float(np.mean(stds))
            verdict = 'BEST' if nz >= args.n - 1 and std < 0.45 else \
                      'ok' if nz >= args.n // 2 and std < 0.45 else 'weak'
            print(f'{gain:>5} {nz:>5}/{args.n} {clips:>5} {flats:>5}  '
                  f'{verdict} (std {std:.3f})')
            results[gain] = (nz, clips, flats, std)
        else:
            print(f'{gain:>5} {nz:>5}/{args.n} {clips:>5} {flats:>5}  '
                  f'dead (all flat/clip)')

    t.dis()
    s.dis()

    if not results:
        print('\n[!] no gain stored anything — check cable/bitstream')
        sys.exit(1)
    # best: most good captures, then lowest clip, then mid-range std
    def score(item):
        g, (nz, clips, flats, std) = item
        return (-nz, clips, abs(std - 0.2))
    best = min(results.items(), key=score)[0]
    print(f'\n[+] USE GAIN: {best}')
    print(f'    python3 collect_dataset.py -n 3000 '
          f'-o Dataset/main_live_g20.h5 --gain {best} '
          f'-b vivado_ascon/ascon_cw305_top.bit')
    print('    Then tell the main machine: the gain used + the stored/clip/flat '
          'counts from the run.')


if __name__ == '__main__':
    main()
