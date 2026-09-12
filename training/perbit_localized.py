#!/usr/bin/env python3
r"""perbit_localized.py — per-bit switching DPA inside known round windows.

residual_cpa.py showed that no *column* (a 5-bit ASCON column) leaks more
than its proportional share of the aggregate.  This goes one level finer: it
tests each of the 320 state BITS individually.

Model: bit b of the state switches (0->1 or 1->0) between the state entering
round r and the state leaving it.  That per-bit switching indicator is the
finest-grained leakage predictor available — it is what a per-bit stochastic
model would use as its regressor set.

    sw_b = bit_b(S_r) XOR bit_b(S_{r+1})          b = 0..319
    score_b = max_t |corr(sw_b, X[:, t])|   over the round's known window

Null: permutation of the bit vectors, max over the same window, Holm-corrected
across all 320 x 12 = 3840 tests.

This is the standard rigour the project adopted after the seven documented
false positives: no method gets to skip the max-statistic null.

Usage:
  .venv/bin/python training/perbit_localized.py <h5> [<h5> ...]
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from labels import load_state, permutation_round  # noqa: E402

FIRST_ROUND_SAMPLE = 110
SAMPLES_PER_ROUND = 8


def holm(p):
    p = np.asarray(p, float)
    o = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    run = 0.0
    for rank, idx in enumerate(o):
        run = max(run, p[idx] * (m - rank))
        adj[idx] = min(run, 1.0)
    return adj


def main():
    import h5py
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', nargs='+')
    ap.add_argument('--n-perm', type=int, default=200)
    ap.add_argument('--win', type=int, default=12)
    args = ap.parse_args()

    X, K, N = [], [], []
    fs = crypto = None
    for p in args.h5:
        with h5py.File(p, 'r') as f:
            a = dict(f.attrs)
            X.append(f['traces'][:].astype(np.float64))
            K.append(f['keys'][:])
            N.append(f['nonces'][:])
            fs = fs or a.get('fs_hz')
            crypto = crypto or a.get('crypto_clk_hz')
    T = min(x.shape[1] for x in X)
    X = np.vstack([x[:, :T] for x in X])
    K, N = np.vstack(K), np.vstack(N)
    Ntr = len(X)
    sm = int(round(fs / crypto))
    if sm > 1:
        k = np.ones(sm) / sm
        X = np.apply_along_axis(lambda r: np.convolve(r, k, mode='same'), 1, X)
    Xz = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1.0)
    print(f'[+] {Ntr} traces, fs={fs/1e6:.0f} MS/s, crypto={crypto/1e6:.1f} MHz, '
          f'cycle boxcar {sm}, window +-{args.win}\n')

    S = load_state(K, N)
    rng = np.random.default_rng(0)
    all_peak, all_names = [], []

    print('  round  best-bit  |r|     null p99.9  bits>null  worst Holm p')
    for r in range(12):
        nxt = permutation_round(S.copy(), r)
        # per-bit switching: (N, 320)
        sw = np.unpackbits((S ^ nxt).view(np.uint8).reshape(len(S), 40),
                           axis=1, bitorder='little').astype(np.float64)
        S = nxt
        centre = FIRST_ROUND_SAMPLE + SAMPLES_PER_ROUND * r
        lo, hi = max(0, centre - args.win), min(T, centre + args.win + 1)
        Xw = Xz[:, lo:hi]

        keep = sw.std(0) > 1e-9          # bits that never switch carry nothing
        swv = sw[:, keep]
        swz = (swv - swv.mean(0)) / swv.std(0)
        C = np.abs(swz.T @ Xw) / Ntr     # (nbits, W)
        peak = C.max(1)

        nl = np.empty(args.n_perm)
        for i in range(args.n_perm):
            P = swz[rng.permutation(Ntr)]
            nl[i] = (np.abs(P.T @ Xw) / Ntr).max()
        nl.sort()
        n999 = float(np.quantile(nl, 0.999))
        # permutation p-value for each bit vs this null
        pv = np.array([(1 + (nl >= v).sum()) / (1 + args.n_perm) for v in peak])
        padj = holm(pv)
        best = int(peak.argmax())
        all_peak.append(peak[best])
        idx = np.where(keep)[0]
        all_names.append(int(idx[best]))
        print(f'   {r+1:2d}     bit {int(idx[best]):3d}   {peak[best]:.4f}   '
              f'{n999:.4f}   {int((peak>n999).sum()):3d}/{len(peak):3d}    '
              f'{padj.min():.4f}')

    print(f'\n  best bits across rounds: {all_names}')
    print(f'  distinct: {len(set(all_names))}/12')
    print('\nIf no bit clears the null and the winners never repeat, the')
    print('aggregate model already exhausts what is measurable: individual')
    print('bits are not separable from the bulk switching of their cycle.')


if __name__ == '__main__':
    main()
