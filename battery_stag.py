#!/usr/bin/env python3
r"""battery_stag.py — per-column max|r| of the staggered amplifier.

Every trace contains all 64 column bursts (leak_cnt == c+1 cycles after the
round-1 sample). No masking: correlate ALL traces against each column's
corrected aff1+chi label and scan the window. A working stagger shows a
per-column comment ladder of correlation peaks stepping 16 samples/cycle.

Usage:
    .venv/bin/python battery_stag.py Dataset/ampstag.h5 [--col 0]
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import labels as lab


def per_sample_r(z, h):
    hc = h - h.mean()
    zc = z - z.mean(0)
    num = zc.T @ hc
    den = np.sqrt(np.sum(zc * zc, axis=0)) * np.sqrt(hc @ hc)
    r = num / np.maximum(den, 1e-12)
    r[den == 0] = 0.0
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('h5')
    ap.add_argument('--col', type=int, default=None)
    ap.add_argument('--top', type=int, default=16, help='rows per column to show')
    ap.add_argument('--n-perm', type=int, default=3)
    args = ap.parse_args()

    import h5py
    with h5py.File(args.h5) as f:
        tr = f['traces'][:]
        keys = f['keys'][:]
        nonces = f['nonces'][:]
    n, s = tr.shape
    sys.stdout.write(f'[{n} traces x {s} samples]\ncomputing labels ... ')
    sys.stdout.flush()
    hw = lab.round1_sbox_hw(keys, nonces)
    sys.stdout.write('done\n')

    mu = tr.mean(0, keepdims=True)
    sd = tr.std(0, keepdims=True)
    z = (tr - mu) / np.maximum(sd, 1e-12)

    cols = [args.col] if args.col is not None else range(64)
    sys.stdout.write(f'\n{"col":>4} {"max|r|":>8} {"@samp":>6} {"null95":>7} '
                     f'{">null?":>7}\n')
    hits = []
    for c in cols:
        r = per_sample_r(z, hw[:, c].astype(np.float64))
        mx = float(np.abs(r).max())
        at = int(np.abs(r).argmax())
        rng = np.random.default_rng(c)
        nulls = []
        for _ in range(args.n_perm):
            h2 = rng.permutation(hw[:, c].astype(np.float64))
            nr = per_sample_r(z, h2)
            nulls.append(np.percentile(np.abs(nr), 95))
        null95 = float(np.max(nulls))
        win = mx > null95
        hits.append(win)
        sys.stdout.write(f'{c:>4} {mx:>8.4f} {at:>6} {null95:>7.4f} '
                         f'{"YES" if win else "":>7}\n')
        sys.stdout.flush()
    if hits:
        sys.stdout.write(f'\ncolumns beating null: {sum(hits)}/{len(hits)}\n')
        if args.col is None:
            # ladder check: peaks should step ~16 samples/cycle
            poss = []
            for c in range(64):
                r = per_sample_r(z, hw[:, c].astype(np.float64))
                poss.append(int(np.abs(r).argmax()))
            poss = np.array(poss)
            sys.stdout.write('peak-sample deltas (col c+1 - c), first 12: '
                             f'{np.diff(poss)[:12]}\n')


if __name__ == '__main__':
    main()