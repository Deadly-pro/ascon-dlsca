#!/usr/bin/env python3
r"""percolumn_localized.py — single-column CPA inside a KNOWN round window.

Until now every per-column test searched all ~2000 samples for its peak, so
the null was a max-over-2000 statistic and the detectable per-trace rho was
inflated accordingly.  round_localize.py shows the rounds are resolved in
time (7.85-7.89 samples/round at 5 MHz, R^2 > 0.997, identical peak samples
across gains and runs).  So we no longer have to search: each round r sits in
a known ~1-cycle window at sample 110 + 8*(r-1).

Restricting the search to that window shrinks the max-statistic null from
max-over-2000 to max-over-W, which buys real sensitivity:

    null ~ sqrt(2 ln S / N)   ->   ratio sqrt(ln 2000 / ln W)

This script asks the question that matters: inside its own round window, is
a SINGLE column's 5-bit switching resolvable, or is it still buried in the
320-bit aggregate that shares that same clock cycle?

Usage:
  .venv/bin/python training/percolumn_localized.py <h5> [<h5> ...]
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from labels import load_state, permutation_round  # noqa: E402

FIRST_ROUND_SAMPLE = 110      # measured; round r peak = FIRST + 8*(r-1)
SAMPLES_PER_ROUND = 8


def popcount64(a):
    m1 = np.uint64(0x5555555555555555)
    m2 = np.uint64(0x3333333333333333)
    m4 = np.uint64(0x0F0F0F0F0F0F0F0F)
    h01 = np.uint64(0x0101010101010101)
    a = a.astype(np.uint64, copy=True)
    a = a - ((a >> np.uint64(1)) & m1)
    a = (a & m2) + ((a >> np.uint64(2)) & m2)
    a = (a + (a >> np.uint64(4))) & m4
    return (a * h01) >> np.uint64(56)


def column_hd(A, B):
    """Per-column Hamming distance: (N,5) -> (N,64).

    Bit j of the result is the HD of column j summed over the 5 state words,
    i.e. the switching contribution of that single 5-bit ASCON column.
    """
    d = A ^ B                                   # (N,5) uint64
    bits = np.unpackbits(d.view(np.uint8).reshape(len(d), 40),
                         axis=1, bitorder='little')     # (N,320)
    return bits.reshape(len(d), 5, 64).sum(axis=1).astype(np.float64)


def main():
    import h5py
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', nargs='+')
    ap.add_argument('--n-perm', type=int, default=200)
    ap.add_argument('--win', type=int, default=12,
                    help='samples searched around each round peak')
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
    K = np.vstack(K)
    N = np.vstack(N)
    Ntr = len(X)
    Xz = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1.0)

    print(f'[+] {Ntr} traces, T={T}, fs={fs/1e6:.0f} MS/s, '
          f'crypto={crypto/1e6:.1f} MHz')
    print(f'[+] window +-{args.win} samples around each round peak\n')

    S = load_state(K, N)
    rng = np.random.default_rng(0)

    print('  round  win-peak  best-col  |r|     null(p99.9)  null(mean)  '
          'cols>null')
    for r in range(12):
        nxt = permutation_round(S.copy(), r)
        Hc = column_hd(S, nxt)                   # (N,64) per-column HD
        S = nxt
        centre = FIRST_ROUND_SAMPLE + SAMPLES_PER_ROUND * r
        lo = max(0, centre - args.win)
        hi = min(T, centre + args.win + 1)
        Xw = Xz[:, lo:hi]

        Hz = (Hc - Hc.mean(0)) / np.where(Hc.std(0) > 0, Hc.std(0), 1.0)
        C = np.abs(Hz.T @ Xw) / Ntr              # (64, W)
        peak = C.max(1)                          # per column
        pk_smp = C.argmax(1) + lo

        # null: random predictors over the SAME restricted window
        nl = np.empty(args.n_perm)
        for i in range(args.n_perm):
            P = rng.permutation(Ntr)
            Pz = Hc[P]
            Pz = (Pz - Pz.mean(0)) / np.where(Pz.std(0) > 0, Pz.std(0), 1.0)
            nl[i] = (np.abs(Pz.T @ Xw) / Ntr).max()
        nl.sort()
        n999 = float(np.quantile(nl, 0.999))

        best = int(peak.argmax())
        above = int((C.max(1) > n999).sum())
        print(f'   {r+1:2d}    {pk_smp[best]:5d}   col {best:2d}   '
              f'{peak[best]:.4f}   {n999:.4f}      {nl.mean():.4f}    '
              f'{above}/64')

    print('\nIf best-col |r| exceeds the restricted null and clusters at a')
    print('consistent column, that column is resolvable. If every round sits')
    print('at the null, a single 5-bit column is not separable from the')
    print('320-bit aggregate even when we know the cycle it lives in.')


if __name__ == '__main__':
    main()
