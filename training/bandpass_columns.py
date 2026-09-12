#!/usr/bin/env python3
r"""bandpass_columns.py — frequency selection, with the aggregate partialled out.

Two things are measured per band:

  1. aggregate: |corr(agg_r, X[:, t])| inside round r's known window.  This is
     a fair statistic — no column predictor involved.

  2. per-column: the PARTIAL correlation
         corr( X - proj(X|agg),  HD_c - proj(HD_c|agg) )
     NOT the raw correlation.  This matters: the 64 column HDs sum to the
     aggregate, so each HD_c is inherently correlated with agg.  A raw
     correlation with a permuted null would score every column as significant
     purely from that shared component — the null permutation destroys the
     column-aggregate coupling that the real data has.  Partialling both sides
     removes it, and then the permutation null is valid.

Usage:
  .venv/bin/python training/bandpass_columns.py <h5> [<h5> ...]
"""
import argparse
import os
import sys

import numpy as np
from scipy.signal import butter, sosfiltfilt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from labels import load_state, permutation_round  # noqa: E402

FIRST_ROUND_SAMPLE = 110
SAMPLES_PER_ROUND = 8


def column_hd(A, B):
    d = A ^ B
    bits = np.unpackbits(d.view(np.uint8).reshape(len(d), 40),
                         axis=1, bitorder='little')
    return bits.reshape(len(d), 5, 64).sum(axis=1).astype(np.float64)


def resid(Y, Z):
    Zc = np.column_stack([np.ones(len(Z)), Z])
    coef, *_ = np.linalg.lstsq(Zc, Y, rcond=None)
    return Y - Zc @ coef


def main():
    import h5py
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', nargs='+')
    ap.add_argument('--n-perm', type=int, default=120)
    ap.add_argument('--win', type=int, default=12)
    ap.add_argument('--q', type=float, default=3.0)
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
    nyq = fs / 2
    print(f'[+] {Ntr} traces, fs={fs/1e6:.0f} MS/s, crypto={crypto/1e6:.1f} MHz, '
          f'Q={args.q}, window +-{args.win}\n')

    S = load_state(K, N)
    Hc, AGG, centres = [], [], []
    for r in range(12):
        nxt = permutation_round(S.copy(), r)
        h = column_hd(S, nxt)
        Hc.append(h)
        AGG.append(h.sum(1))
        centres.append(FIRST_ROUND_SAMPLE + SAMPLES_PER_ROUND * r)
        S = nxt

    rng = np.random.default_rng(0)
    freqs = np.array([1, 2, 3, 3.5, 4, 5, 6, 8, 10, 14, 18]) * 1e6

    print('  f (MHz)  agg|r|   best-col |r_partial|  null p99.9  cols>null')
    for f in freqs:
        lo = max(f - f / args.q, 0.05e6)
        hi = min(f + f / args.q, nyq * 0.98)
        if hi <= lo:
            continue
        sos = butter(4, [lo / nyq, hi / nyq], btype='band', output='sos')
        Xf = sosfiltfilt(sos, X, axis=1)
        Xf = (Xf - Xf.mean(0)) / np.where(Xf.std(0) > 0, Xf.std(0), 1.0)

        agg_best, col_best, null_best, above = 0.0, 0.0, 0.0, 0
        for r in range(12):
            c0 = centres[r]
            ls, hs = max(0, c0 - args.win), min(T, c0 + args.win + 1)
            Xw = Xf[:, ls:hs]
            ag = AGG[r]
            agg_best = max(agg_best,
                           float(np.abs(((ag - ag.mean()) / ag.std()) @ Xw
                                        / Ntr).max()))
            # residualise traces and columns on the aggregate
            Xr = np.stack([resid(Xw[:, j], ag) for j in range(Xw.shape[1])], 1)
            Xrz = (Xr - Xr.mean(0)) / np.where(Xr.std(0) > 0, Xr.std(0), 1.0)
            Hr = np.stack([resid(Hc[r][:, c], ag) for c in range(64)], 1)
            Hrz = (Hr - Hr.mean(0)) / np.where(Hr.std(0) > 0, Hr.std(0), 1.0)
            Hrz = np.nan_to_num(Hrz)
            C = np.abs(Hrz.T @ Xrz) / Ntr
            col_best = max(col_best, float(C.max()))

            m = 0.0
            for _ in range(max(10, args.n_perm // 12)):
                P = Hrz[rng.permutation(Ntr)]
                P = (P - P.mean(0)) / np.where(P.std(0) > 0, P.std(0), 1.0)
                m = max(m, float((np.abs(np.nan_to_num(P).T @ Xrz) / Ntr).max()))
            null_best = max(null_best, m)
            above += int((C.max(1) > m).sum())
        print(f'   {f/1e6:4.1f}   {agg_best:.4f}    {col_best:.4f}        '
              f'{null_best:.4f}     {above}/768')

    print('\nWith the aggregate partialled out of both sides, a column above')
    print('null would mean real column-level signal in that band.')


if __name__ == '__main__':
    main()
