#!/usr/bin/env python3
r"""residual_cpa.py — Priority 1b: partial out the aggregate, then test columns.

The round localization gives each round a known ~1-cycle window.  Inside that
window the measured power is dominated by the 320-bit aggregate switching of
that round (|r| ~ 0.35-0.43).  A single column contributes 5 of those 320 bits.

The question this answers is sharper than "is there per-column leakage":

    Is any single column's switching visible *on top of* the aggregate that
    shares its clock cycle?

We use the partial correlation, which removes the aggregate from BOTH sides:

    r_partial(c, t) = corr( X[:,t] - proj(X[:,t] | agg) ,
                            HD_c    - proj(HD_c    | agg) )

If the leakage were exactly proportional across columns (every column leaking
its fair share), the partial correlation would vanish: the aggregate already
explains HD_c.  A nonzero partial correlation means a column leaks MORE than
its share, or that the aggregate model is inadequate.

Null: permutation of the column labels within the restricted window, using the
same residualised trace, so the max-statistic null has the correct degrees of
freedom.

Usage:
  .venv/bin/python training/residual_cpa.py <h5> [<h5> ...]
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


def column_hd(A, B):
    d = A ^ B
    bits = np.unpackbits(d.view(np.uint8).reshape(len(d), 40),
                         axis=1, bitorder='little')
    return bits.reshape(len(d), 5, 64).sum(axis=1).astype(np.float64)


def resid(Y, Z):
    """Residual of Y after least-squares projection on Z (+intercept)."""
    Zc = np.column_stack([np.ones(len(Z)), Z])
    coef, *_ = np.linalg.lstsq(Zc, Y, rcond=None)
    return Y - Zc @ coef


def zs(a):
    a = np.asarray(a, float)
    s = a.std()
    return (a - a.mean()) / (s if s > 1e-12 else 1.0)


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
    # The round's switching is spread across the whole clock cycle, so the
    # traces must be integrated over one cycle (boxcar = samples/cycle)
    # before the aggregate is correlated; without this the aggregate is
    # under-modelled (|r| ~ 0.07 instead of ~0.4) and the residual is wrong.
    sm = int(round(fs / crypto))
    if sm > 1:
        k = np.ones(sm) / sm
        X = np.apply_along_axis(lambda r: np.convolve(r, k, mode='same'), 1, X)
    print(f'[+] {Ntr} traces, fs={fs/1e6:.0f} MS/s, crypto={crypto/1e6:.1f} MHz, '
          f'cycle boxcar {sm}, window +-{args.win}')

    S = load_state(K, N)
    rng = np.random.default_rng(0)

    print('\n  round  agg|r|  best-col |r_partial|  null p99.9  null mean  '
          'cols>null')
    allbest = []
    for r in range(12):
        nxt = permutation_round(S.copy(), r)
        Hc = column_hd(S, nxt)
        S = nxt
        agg = Hc.sum(1)

        centre = FIRST_ROUND_SAMPLE + SAMPLES_PER_ROUND * r
        lo, hi = max(0, centre - args.win), min(T, centre + args.win + 1)
        Xw = X[:, lo:hi]

        # aggregate correlation in this window (the thing we are partialling)
        aggr = np.abs(zs(agg) @ zs(Xw) / Ntr).max()

        # residualise the traces on the aggregate, per sample
        Xr = np.stack([resid(Xw[:, j], agg) for j in range(Xw.shape[1])], 1)
        Xrz = (Xr - Xr.mean(0)) / np.where(Xr.std(0) > 0, Xr.std(0), 1.0)

        # residualise each column's HD on the aggregate
        Hr = np.stack([resid(Hc[:, c], agg) for c in range(64)], 1)
        Hrz = (Hr - Hr.mean(0)) / np.where(Hr.std(0) > 0, Hr.std(0), 1.0)
        Hrz = np.nan_to_num(Hrz)

        C = np.abs(Hrz.T @ Xrz) / Ntr            # (64, W)
        peak = C.max(1)

        nl = np.empty(args.n_perm)
        for i in range(args.n_perm):
            P = rng.permutation(Ntr)
            Pz = Hrz[P]
            Pz = (Pz - Pz.mean(0)) / np.where(Pz.std(0) > 0, Pz.std(0), 1.0)
            nl[i] = (np.abs(np.nan_to_num(Pz).T @ Xrz) / Ntr).max()
        nl.sort()
        n999 = float(np.quantile(nl, 0.999))
        best = int(peak.argmax())
        allbest.append(best)
        print(f'   {r+1:2d}   {aggr:.4f}    col {best:2d}   {peak[best]:.4f}      '
              f'{n999:.4f}    {nl.mean():.4f}    {int((peak>n999).sum())}/64')

    print(f'\n  best columns across rounds: {allbest}')
    uniq, cnt = np.unique(allbest, return_counts=True)
    print(f'  distinct best columns: {len(uniq)}/12  '
          f'(consistent column would repeat)')
    print('\nIf |r_partial| clears its null and the best column repeats across')
    print('rounds, a column leaks more than its proportional share. If every')
    print('round sits at the null with a scattered winner, the aggregate')
    print('already accounts for the per-column signal.')


if __name__ == '__main__':
    main()
