#!/usr/bin/env python3
r"""battery_ampmux.py — per-column max|r| of the muxed burst vs corrected labels.

For each trace, the muxed amplifier fires one burst whose 5-bit pattern is
HW's complement source: the round-1 aff1+chi intermediate of column
sel_col (6 nonce bits, nonce byte 8). This battery:

  1. computes the corrected aff1+chi label (lab.round1_sbox_hw) per column,
  2. masks traces to those whose recorded nonce selects that column,
  3. Pearson-correlates the burst-current amplitude (z-scored per sample)
     against the column HW label,
  4. reports max |r| per column, its sample position, a label-permutation
     null (expected max under noise), and flags any column beating it.

The historical per-column floor across all amplified bitstreams was
0.118-0.135. A beating null with the corrected algebra is the success signal.

Usage:
    .venv/bin/python battery_ampmux.py Dataset/ampmux.h5 [--col 0]
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import labels as lab


def sel_col_from_nonce(nonce):
    """Column selected by the RTL: {nonce2[5:4], nonce2[1:0]} with nonce2
    little-endian, so byte index 8 holds bits [7:0]."""
    nb8 = int(nonce[8])
    return ((nb8 >> 4) & 3) << 4 | ((nb8 >> 1) & 1) << 1 | (nb8 & 1)


def per_sample_r(z, h):
    """Pearson r per sample: (m,S) z-scored traces vs (m,) HW label."""
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
    ap.add_argument('--col', type=int, default=None, help='only this column')
    ap.add_argument('--min-traces', type=int, default=30,
                    help='skip columns with fewer qualifying traces')
    ap.add_argument('--n-perm', type=int, default=3,
                    help='label-permutation nulls per column')
    ap.add_argument('--window', type=str, default=None,
                    help='sample slice a:b to restrict the scan')
    args = ap.parse_args()

    import h5py
    with h5py.File(args.h5) as f:
        tr = f['traces'][:]
        keys = f['keys'][:]
        nonces = f['nonces'][:]
    if args.window:
        sl = slice(*[int(x) for x in args.window.split(':')])
        tr = tr[:, sl]
    n, s = tr.shape
    sys.stdout.write(f'[{n} traces x {s} samples]\n')
    sys.stdout.write('computing corrected aff1+chi labels ... ')
    sys.stdout.flush()
    hw = lab.round1_sbox_hw(keys, nonces)          # (n, 64)
    sys.stdout.write('done\n')

    mu = tr.mean(0, keepdims=True)
    sd = tr.std(0, keepdims=True)
    z = (tr - mu) / np.maximum(sd, 1e-12)

    sc = np.array([sel_col_from_nonce(b) for b in nonces])
    cols = [args.col] if args.col is not None else range(64)

    sys.stdout.write(f'\n{"col":>4} {"n":>5} {"max|r|":>8} {"@samp":>6} '
                     f'{"null98":>7} {"win?":>5}\n')
    wins = []
    for c in cols:
        m = sc == c
        if m.sum() < args.min_traces:
            continue
        r = per_sample_r(z[m], hw[m, c].astype(np.float64))
        mx = float(np.abs(r).max())
        at = int(np.abs(r).argmax())
        # label-permutation null: expected 98th pct of |r| under noise
        nulls = []
        rng = np.random.default_rng(c)
        for _ in range(args.n_perm):
            h2 = rng.permutation(hw[m, c].astype(np.float64))
            nr = per_sample_r(z[m], h2)
            nulls.append(np.percentile(np.abs(nr), 98))
        null98 = float(np.max(nulls))
        win = mx > null98
        wins.append(win)
        sys.stdout.write(f'{c:>4} {int(m.sum()):>5} {mx:>8.4f} {at:>6} '
                         f'{null98:>7.4f} {"YES" if win else "":>5}\n')
        sys.stdout.flush()

    if wins:
        sys.stdout.write(f'\ncolumns beating permutation null: '
                         f'{sum(wins)}/{len(wins)}\n')
        sys.stdout.write('historical per-column floor was 0.118-0.135\n')


if __name__ == '__main__':
    main()