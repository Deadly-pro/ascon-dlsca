#!/usr/bin/env python3
r"""synthetic_landscape.py — can ANY search recover a key from the round-HD objective?

Why this must be synthetic (for now)
------------------------------------
A key search needs many traces under ONE key, so that

    score(K) = corr over traces( HD_r(K, N_i) , measured_i )

is meaningful.  Our captures do not allow that:

  * sprint A/B/C/D/E2  -> single key, but the window is blind (offset 700)
  * run_pa_20260909    -> valid window, but RANDOM keys (one nonce per key)

So there is currently no fixed-key, valid-window dataset, and score(K) cannot
be evaluated on real data at all.  This script answers the geometry question
anyway, using nonces taken from a real capture and noise calibrated so the
simulated correlation matches the MEASURED 0.41.  If the objective has no
gradient at the measured SNR, no real capture will fix that.

What it measures
----------------
score(K) as a function of the number of wrong key bits.  Specifically the
basin width: how many bits can be wrong before the score collapses to the
random-key baseline.  That number decides which algorithms are even eligible:

  basin ~1 bit   -> flat landscape. Coordinate descent, SA, GA, beam search
                    are ALL dead (none can move without a gradient).
  basin >= 8     -> local search is viable; the basin width says how much of
                    the key one descent can recover.

Usage:
  .venv/bin/python training/synthetic_landscape.py <h5> [--reps 20]
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


def round_hd(K, N, r):
    S = load_state(K, N)
    for i in range(r + 1):
        nxt = permutation_round(S.copy(), i)
        if i == r:
            return popcount64(S ^ nxt).sum(1).astype(np.float64)
        S = nxt
    raise AssertionError


def zs(a):
    a = np.asarray(a, float)
    s = a.std()
    return (a - a.mean()) / (s if s > 1e-12 else 1.0)


def main():
    import h5py
    ap = argparse.ArgumentParser()
    ap.add_argument('h5')
    ap.add_argument('--target-r', type=float, default=0.41,
                    help='measured aggregate correlation to reproduce')
    ap.add_argument('--reps', type=int, default=20)
    ap.add_argument('--flips', type=int, nargs='+',
                    default=[0, 1, 2, 4, 8, 16, 32, 64, 128])
    args = ap.parse_args()

    with h5py.File(args.h5, 'r') as f:
        N = f['nonces'][:]
        K0 = f['keys'][0]
    Ntr = len(N)
    print(f'[+] {Ntr} nonces from {os.path.basename(args.h5)}')
    print(f'[+] simulating leakage proportional to the 320-bit round HD,')
    print(f'    noise scaled to reproduce |r| = {args.target_r}\n')

    # ground-truth predictor and the noise level that yields the target rho
    hd_true = round_hd(np.tile(K0, (Ntr, 1)), N, 0)
    z = zs(hd_true)
    rho = args.target_r
    noise = np.random.default_rng(0).standard_normal(Ntr)
    # corr(z, z + s*noise) = 1/sqrt(1+s^2) = rho  ->  s = sqrt(1/rho^2 - 1)
    s = np.sqrt(1.0 / rho**2 - 1.0)
    x = z + s * noise
    print(f'[+] sanity: corr(predictor, simulated trace) = '
          f'{np.corrcoef(z, x)[0,1]:.4f}\n')

    def score(K):
        return float(np.abs(zs(round_hd(K, N, 0)) @ zs(x)) / Ntr)

    s_true = score(np.tile(K0, (Ntr, 1)))
    rng = np.random.default_rng(1)
    rand = np.array([score(np.tile(rng.integers(0, 256, 16, dtype=np.uint8),
                                   (Ntr, 1))) for _ in range(40)])
    print(f'[+] score(true key)    = {s_true:.4f}')
    print(f'[+] score(random key)  = {rand.mean():.4f} +- {rand.std():.4f}\n')

    print('  wrong bits   score      sigma above random')
    for nf in args.flips:
        vals = []
        for _ in range(args.reps):
            kk = K0.copy()
            for b in rng.choice(128, size=nf, replace=False):
                kk[b // 8] ^= (1 << (b % 8))
            vals.append(score(np.tile(kk, (Ntr, 1))))
        v = float(np.mean(vals))
        sig = (v - rand.mean()) / (rand.std() + 1e-12)
        print(f'    {nf:4d}       {v:.4f}     {sig:+.2f}')

    print('\nRead the 1-bit row: if it is already inside the random spread,')
    print('the objective is flat and no hill-climbing search can work on it.')


if __name__ == '__main__':
    main()
