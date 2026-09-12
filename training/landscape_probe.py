#!/usr/bin/env python3
r"""landscape_probe.py — is the round-HD objective usable for key recovery?

The round-HD signal is real: the 320-bit state Hamming distance per round
correlates with the trace at |r| = 0.32-0.43 inside a known window, R^2 =
0.9987 against the predicted round spacing.  The obvious next move is to use
it as an objective for key recovery:

    score(K) = corr( measured trace in round r's window ,
                     HD_r(K, nonces) )

The question this script answers is whether that objective has ANY usable
geometry.  Two things are measured:

 1. DISCRIMINATION — how far above random does the true key sit?  If the true
    key is 1 sigma above the pack, no search will ever find it.

 2. BASIN WIDTH — score as a function of the number of wrong key bits.  If
    flipping 1 bit drops the score to random, the landscape is flat and every
    hill-climbing family (coordinate descent, SA, GA, beam) is dead on
    arrival, because none of them can make progress without a gradient.

This is the feasibility gate for the whole recovery plan.  It is cheap and
runs entirely offline.

Usage:
  .venv/bin/python training/landscape_probe.py <h5> [<h5> ...]
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
    """320-bit HD for round r (0-indexed) given key bytes K and nonces N."""
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
    ap.add_argument('h5', nargs='+')
    ap.add_argument('--rounds', type=int, default=12)
    ap.add_argument('--n-random', type=int, default=400)
    ap.add_argument('--flips', type=int, nargs='+',
                    default=[1, 2, 4, 8, 16, 32, 64])
    args = ap.parse_args()

    X, K, N = [], [], []
    fs = None
    for p in args.h5:
        with h5py.File(p, 'r') as f:
            a = dict(f.attrs)
            X.append(f['traces'][:].astype(np.float64))
            K.append(f['keys'][:])
            N.append(f['nonces'][:])
            fs = fs or a.get('fs_hz')
            crypto = a.get('crypto_clk_hz')
    T = min(x.shape[1] for x in X)
    X = np.vstack([x[:, :T] for x in X])
    K, N = np.vstack(K), np.vstack(N)
    Ntr = len(X)
    sm = int(round(fs / crypto))
    if sm > 1:
        k = np.ones(sm) / sm
        X = np.apply_along_axis(lambda r: np.convolve(r, k, mode='same'), 1, X)
    Xz = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1.0)
    print(f'[+] {Ntr} traces, boxcar {sm}\n')

    # pooled score over all rounds: mean |r| across the 12 round windows
    def score(Ktest):
        tot = 0.0
        for r in range(args.rounds):
            hd = round_hd(Ktest, N, r)
            c = FIRST_ROUND_SAMPLE + SAMPLES_PER_ROUND * r
            lo, hi = max(0, c - 12), min(T, c + 12 + 1)
            tot += float(np.abs(zs(hd) @ Xz[:, lo:hi] / Ntr).max())
        return tot / args.rounds

    true_key = K[0].copy()          # fixed-key captures: one key for all traces
    n_unique = len(np.unique(K.view([('', K.dtype)] * K.shape[1])))
    print(f'[+] distinct keys in capture: {n_unique}')
    s_true = score(np.tile(true_key, (Ntr, 1)))
    print(f'[+] score(true key)          = {s_true:.4f}')

    rng = np.random.default_rng(0)
    rand = [score(np.tile(rng.integers(0, 256, 16, dtype=np.uint8), (Ntr, 1)))
            for _ in range(30)]
    rand = np.array(rand)
    print(f'[+] score(random keys)       = {rand.mean():.4f} '
          f'+- {rand.std():.4f}  (max {rand.max():.4f})')
    z = (s_true - rand.mean()) / (rand.std() + 1e-12)
    print(f'[+] true key sits {z:.2f} sigma above random\n')

    print('  wrong bits   score     delta vs true   sigma above random')
    for f in args.flips:
        vals = []
        for _ in range(12):
            kk = true_key.copy()
            pos = rng.choice(128, size=f, replace=False)
            for b in pos:
                kk[b // 8] ^= (1 << (b % 8))
            vals.append(score(np.tile(kk, (Ntr, 1))))
        v = np.mean(vals)
        print(f'    {f:4d}      {v:.4f}    {v - s_true:+.4f}        '
              f'{(v - rand.mean())/rand.std():+.2f}')

    print('\nIf the 1-bit-flip row is already at random, the objective has no')
    print('gradient and no hill-climbing search can work on it. If it degrades')
    print('smoothly, a local search is viable and the basin width tells you')
    print('how much of the key a single descent can recover.')


if __name__ == '__main__':
    main()
