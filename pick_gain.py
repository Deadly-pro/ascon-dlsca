#!/usr/bin/env python3
r"""pick_gain.py — pick the best scope gain at the pipeline config.

Runs a gain sweep at the collection config (40 MHz sample clock, 2000 samples,
offset 700) and reports good/clip/flat counts and mean std per gain. The scope
model (CW-Husky vs CW-Lite/CW-Pro) is auto-detected.

Usage:
    python3 pick_gain.py -b vivado_ascon/ascon_cw305_top.bit
    python3 pick_gain.py --gains 25,20,15,10,5,0,-5,-10,-15
"""
import argparse
import os
import sys

import numpy as np

import chipwhisperer as cw

from scope_config import connect_target, configure_scope, is_husky
import scope_config


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(here, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--gains', type=str, default='25,20,15,10,5,0,-5,-10,-15',
                    help='comma-separated candidate gains')
    ap.add_argument('--n', type=int, default=10, help='captures per gain')
    args = ap.parse_args()
    gains = [int(g) for g in args.gains.split(',')]

    if np.any(np.abs(gains) > 100) or len(gains) > 20:
        sys.exit('gain list looks wrong; use -15..65 typical range')

    w = connect_target(args.bitstream)
    w.loadEncryptionKey(bytes.fromhex('0f1e2d3c4b5a69788796a5b4c3d2e1f0'))
    w.loadInput(bytes.fromhex('000102030405060708090a0b0c0d0e0f'))

    s = configure_scope(gain=gains[0], samples=2000, offset=700, sample_rate=40e6)
    print(f'[+] scope: {"CW-Husky" if is_husky(s) else "CW-Lite/CW-Pro"}')

    # ADC clock sanity: after a replug the scope can come up with adc_freq=0
    # (clock PLL not locked), which makes capture() divide by zero. Re-run
    # reset_adc() up to a few times; if it stays 0, report and exit cleanly.
    for attempt in range(8):
        if s.clock.adc_freq and s.clock.adc_freq > 1e6:
            break
        print(f'[!] adc_freq bad ({s.clock.adc_freq}) - re-syncing ADC clock '
              f'(attempt {attempt + 1}/8)')
        s.clock.reset_adc()
    if not s.clock.adc_freq or s.clock.adc_freq <= 1e6:
        print(f'[!] ADC clock failed to lock (adc_freq={s.clock.adc_freq}). '
              f'Check the USB connection, then replug and re-run.')
        w.dis()
        s.dis()
        sys.exit(2)
    print(f'[+] adc_freq = {s.clock.adc_freq/1e6:.1f} MHz')

    print(f"{'gain':>5} {'good':>5} {'clips':>5} {'flats':>5}  verdict")
    results = {}
    for gain in gains:
        if is_husky(s) and not (scope_config.HUSKY_GAIN_MIN <= gain <= scope_config.HUSKY_GAIN_MAX):
            print(f'{gain:>5}   out of Husky probe range '
                  f'({scope_config.HUSKY_GAIN_MIN:.0f}..'
                  f'{scope_config.HUSKY_GAIN_MAX:.0f})')
            continue
        s.gain.db = gain
        stds, clips, flats = [], 0, 0
        for _ in range(args.n):
            s.arm()
            w.go()
            s.capture()
            tr = s.get_last_trace()
            if tr is None or tr.size != 2000 or tr.std() < 0.001:
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

    w.dis()
    s.dis()

    if not results:
        print('\n[!] no gain stored anything - check cables/bitstream')
        sys.exit(1)
    # best: most good captures, then lowest clip, then mid-range std
    def score(item):
        g, (nz, clips, flats, std) = item
        return (-nz, clips, abs(std - 0.2))
    best = min(results.items(), key=score)[0]
    print(f'\n[+] USE GAIN: {best}')
    print(f'    python3 collect_dataset.py -n 3000 '
          f'-o Dataset/main_live.h5 --gain {best} '
          f'-b vivado_ascon/ascon_cw305_top.bit')


if __name__ == '__main__':
    main()