#!/usr/bin/env python3
r"""stochastic_profile.py — joint per-bit stochastic model, round-windowed.

Priority 3, first item.  Where perbit_localized.py tests each bit's switching
independently (univariate), a stochastic model fits all 320 bits jointly:

    y = sum_b w_b * sw_b + c

with y the cycle-integrated trace inside a known round window.  A joint fit
can in principle recover a bit whose individual correlation is buried, because
it can use the structure of the other bits to cancel shared noise.

Rigor: the model is scored on HELD-OUT traces (k-fold), against a permutation
null.  In-sample R^2 with 320 regressors on ~2100 samples is meaningless
without this, and in-sample numbers are exactly how the earlier false
positives happened.

Usage:
  .venv/bin/python training/stochastic_profile.py <h5> [<h5> ...]
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


def cv_r2(B, y, folds=5, ridge=1.0, seed=0):
    """Held-out R^2 of a ridge fit of y on B (+intercept).

    Features are standardised using TRAIN-fold statistics only, so that the
    ridge penalty is on a meaningful scale.  Without this the 0/1 switching
    columns have unit-ish variance, ridge=1.0 is effectively no penalty, and
    both the observed and the null R^2 come out deeply negative (which says
    nothing about signal either way).
    """
    n = len(y)
    idx = np.random.default_rng(seed).permutation(n)
    chunks = np.array_split(idx, folds)
    pred = np.empty(n)
    for i in range(folds):
        te = chunks[i]
        tr = np.concatenate([chunks[j] for j in range(folds) if j != i])
        mu = B[tr].mean(0)
        sd = B[tr].std(0)
        sd = np.where(sd > 1e-12, sd, 1.0)
        A = np.column_stack([np.ones(len(tr)), (B[tr] - mu) / sd])
        At = np.column_stack([np.ones(len(te)), (B[te] - mu) / sd])
        reg = ridge * np.eye(A.shape[1])
        reg[0, 0] = 0.0
        try:
            w = np.linalg.solve(A.T @ A + reg, A.T @ y[tr])
        except np.linalg.LinAlgError:
            w = np.linalg.lstsq(A, y[tr], rcond=None)[0]
        pred[te] = At @ w
    ss_res = ((y - pred) ** 2).sum()
    ss_tot = ((y - y.mean()) ** 2).sum()
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0.0


def main():
    import h5py
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', nargs='+')
    ap.add_argument('--n-perm', type=int, default=100)
    ap.add_argument('--win', type=int, default=12)
    ap.add_argument('--folds', type=int, default=5)
    ap.add_argument('--ridge', type=float, default=1.0,
                    help='ridge strength; 320 regressors need real '
                         'regularisation or CV R^2 is meaningless (a weak '
                         'ridge makes observed and null both deeply negative)')
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
    print(f'[+] {Ntr} traces, cycle boxcar {sm}, {args.folds}-fold CV, '
          f'window +-{args.win}\n')

    S = load_state(K, N)
    rng = np.random.default_rng(0)
    ys = []

    print('  round   y-std    CV R^2 (bits)   null mean   null p95   top |w| bit')
    for r in range(12):
        nxt = permutation_round(S.copy(), r)
        sw = np.unpackbits((S ^ nxt).view(np.uint8).reshape(len(S), 40),
                           axis=1, bitorder='little').astype(np.float64)
        S = nxt
        centre = FIRST_ROUND_SAMPLE + SAMPLES_PER_ROUND * r
        lo, hi = max(0, centre - args.win), min(T, centre + args.win + 1)
        y = X[:, lo:hi].mean(1)
        ys.append(y)

        keep = sw.std(0) > 0.05   # bit must switch in at least ~5% of traces;
        B = sw[:, keep]           # near-constant bits amplify under z-scoring
        keepidx = np.where(keep)[0]

        r2 = cv_r2(B, y, folds=args.folds, ridge=args.ridge)

        nl = np.array([cv_r2(B, y[rng.permutation(Ntr)], folds=args.folds,
                             ridge=args.ridge, seed=i + 1)
                       for i in range(args.n_perm)])
        # full-data fit for the dominant weights
        Bc = np.column_stack([np.ones(Ntr), B])
        reg = 1e-2 * np.eye(Bc.shape[1])
        reg[0, 0] = 0
        w = np.linalg.solve(Bc.T @ Bc + reg, Bc.T @ y)
        top = int(keepidx[np.abs(w[1:]).argmax()])

        print(f'   {r+1:2d}    {y.std():.5f}     {r2:+.5f}       '
              f'{nl.mean():+.5f}   {np.quantile(nl,0.95):+.5f}   bit {top:3d} '
              f'(|w|={np.abs(w[1:]).max():.2e})')

    print('\n  Held-out R^2 should exceed the null for a usable stochastic')
    print('  model. At or below the null means the 320-bit switching pattern')
    print('  carries no more information about this cycle than chance.')


if __name__ == '__main__':
    main()
