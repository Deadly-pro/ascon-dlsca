#!/usr/bin/env python3
r"""sim_sweep.py — leakage-amplitude sweep for the virtual-board ACPPA study.

For each amp in --amps: generate a synthetic training h5 (SimBoard, noise
model fitted from the real unmasked capture), preprocess, train the S-box
column profile, run the offline premise check, then (optionally) run the live
`adaptive.py --attack --sim` closed loop against the virtual board.

Writes training/results/sim_sweep.json + a console table:

    amp | sim-SNR(dB) | profile val | premise top-1 | attack: queries / correct?

amp=1.0 reproduces the real capture's SNR; the real board's S-box false
convergence should be reproduced at amp=1 and fixed at higher amps.

Usage:
    .venv/bin/python training/sim_sweep.py --amps 1 2 4 8 16 --queries 40
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from sim_board import SimBoard, _fit_from_h5  # noqa: E402


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return r.stdout + r.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--h5', default='Dataset/main_unmasked_merged.h5')
    ap.add_argument('--column', type=int, default=0)
    ap.add_argument('--key', default='000102030405060708090a0b0c0d0e0f')
    ap.add_argument('--amps', type=float, nargs='*', default=[1, 2, 4, 8, 16])
    ap.add_argument('--ntrain', type=int, default=3000, help='sim traces per amp')
    ap.add_argument('--queries', type=int, default=40, help='max attack queries')
    ap.add_argument('--no-attack', action='store_true', help='skip live sim attack')
    ap.add_argument('--workdir', default='/tmp/opencode/sim_sweep')
    args = ap.parse_args()

    os.makedirs(args.workdir, exist_ok=True)
    name = os.path.splitext(os.path.basename(args.h5))[0]
    truth = args.key
    results = []

    # reference SNR of the real capture for the chosen column
    fit = _fit_from_h5(args.h5, args.column)

    for amp in args.amps:
        tag = f'{name}_c{args.column}_a{amp:g}'
        sim_h5 = os.path.join(args.workdir, f'{tag}.h5')
        npz = os.path.join(ROOT, 'training', 'data', f'{tag}.npz')
        model = os.path.join(ROOT, 'training', 'models', f'{tag}_c{args.column}_sbox_cnn1.pt')

        print(f'\n=== amp {amp:g} ===')
        if not os.path.exists(sim_h5):
            b = SimBoard(args.h5, bytes.fromhex(truth), column=args.column,
                         amp=amp, seed=3)
            b.generate_h5(sim_h5, n=args.ntrain)
        run([sys.executable, os.path.join(ROOT, 'training', 'preprocess.py'), sim_h5])
        run([sys.executable, os.path.join(ROOT, 'training', 'train.py'), npz,
             '--target', 'sbox', '--arch', 'cnn1', '--window', '1600',
             '--epochs', '30', '--seed', '3'])

        # offline premise check
        out = run([sys.executable, os.path.join(ROOT, 'training', 'adaptive.py'),
                   '--validate', '--npz', npz, '--model', model,
                   '--column', str(args.column)])
        premise = {}
        for line in out.splitlines():
            line = line.strip()
            if 'top-1' in line:
                premise['top1'] = line
            if 'rank' in line and 'mean' in line:
                premise['rank'] = line
            if 'HW-class top-1' in line:
                premise['hw_top1'] = line

        attack = {'queries': None, 'hyp': None, 'correct': None}
        if not args.no_attack:
            out = run([sys.executable, os.path.join(ROOT, 'training', 'adaptive.py'),
                       '--attack', '--sim', '--npz', npz, '--model', model,
                       '--column', str(args.column), '--key', truth,
                       '--max-queries', str(args.queries), '--sim-amp', str(amp)])
            for line in out.splitlines():
                line = line.strip()
                if 'converged at query' in line:
                    attack['queries'] = int(line.split('query ')[1].split(':')[0])
                    attack['hyp'] = int(line.split('hyp ')[1].split(' ')[0])
                if 'no convergence after' in line:
                    attack['hyp'] = int(line.split('top hyp ')[1].split(',')[0])
                    attack['queries'] = int(line.split('after ')[1].split(' ')[0])
            if attack['hyp'] is not None:
                hyps = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
                k = bytes.fromhex(truth)
                c = args.column
                k0 = (k[c // 8] >> (c % 8)) & 1
                k1 = (k[8 + c // 8] >> (c % 8)) & 1
                true_h = int(np.flatnonzero((hyps[:, 0] == k0) & (hyps[:, 1] == k1))[0])
                attack['correct'] = bool(attack['hyp'] == true_h)

        results.append({'amp': amp, 'premise': premise, 'attack': attack})
        print(json.dumps({'amp': amp, 'attack': attack}, indent=1))

    out_json = os.path.join(ROOT, 'training', 'results', 'sim_sweep.json')
    with open(out_json, 'w') as f:
        json.dump({'column': args.column, 'key': truth, 'runs': results}, f, indent=2)
    print(f'\n[+] wrote {out_json}')

    print('\n=== summary ===')
    print('amp | sim-SNR | queries | hyp | correct?')
    for r in results:
        a = r['attack']
        print(f"{r['amp']:>3g} | {r['amp']:g}x | {a['queries'] if a['queries'] else '-'} "
              f"| {a['hyp'] if a['hyp'] is not None else '-'} | {a['correct']}")


if __name__ == '__main__':
    main()
