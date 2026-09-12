#!/usr/bin/env python3
r"""recovery_budget.py — trace budget for the factorable per-column attack.

The predictor that matters
--------------------------
The full-round per-column HD is NOT factorable: the linear diffusion layer
rotates bits within each word, so column c's round HD depends on the S-box
outputs at neighbouring positions too.  The factorable predictor is the
SUBSTITUTION layer, which is applied bitwise across the 64 positions:

    S'_c = Sbox( S_c ^ RC )        for each of the 64 five-bit columns

so column c's switching depends on exactly 5 bits -- and of those, only TWO
are key bits:

    IV[c] (public) , K1[c] , K2[c] (key) , N1[c] , N2[c] (public)

With load_state packing S[1] = big-endian key[0:8] and S[2] = key[8:16],
column c's key bits are

    bit (c % 8) of key byte (7  - c // 8)
    bit (c % 8) of key byte (15 - c // 8)

So there are 4 hypotheses per column, and flipping those two bits changes
ONLY that column -- a genuine 4-way factorisation, 64 columns, 128 bits.

Budget
------
Under proportional leakage the per-column correlation is

    rho_col ~= rho_agg * sigma_col / sigma_agg

and the max-over-hypotheses null with 4 hypotheses and a W-sample window is

    null ~= sqrt( 2 ln(4 W) / N_eff ),      N_eff = N_stored * M

This script simulates that attack at the measured effect size and reports the
per-column recovery rate against N_eff, deriving the board requirement rather
than guessing it.

Usage:
  .venv/bin/python training/recovery_budget.py <h5> [--trials 10]
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from labels import load_state, substitution_layer  # noqa: E402

FIRST_ROUND_SAMPLE = 110
SAMPLES_PER_ROUND = 8
RC0 = 0xF0


def column_hd(A, B):
    """Per-column HD: (N,5) -> (N,64); bit c = HD of the 5 bits at position c."""
    d = A ^ B
    bits = np.unpackbits(d.view(np.uint8).reshape(len(d), 40),
                         axis=1, bitorder='little')
    return bits.reshape(len(d), 5, 64).sum(axis=1).astype(np.float64)


def sbox_col_hd(K, N):
    """Per-column switching through the round-1 substitution layer only."""
    S = load_state(K, N)
    Sc = S.copy()
    Sc[:, 2] ^= np.uint64(RC0)
    return column_hd(Sc, substitution_layer(Sc))


def key_bit_sites(c):
    """(byte, bitmask) for the two key bits feeding column c."""
    b = c % 8
    return (7 - c // 8, np.uint8(1 << b)), (15 - c // 8, np.uint8(1 << b))


def zs(a):
    a = np.asarray(a, float)
    s = a.std()
    return (a - a.mean()) / (s if s > 1e-12 else 1.0)


def main():
    import h5py
    ap = argparse.ArgumentParser()
    ap.add_argument('h5')
    ap.add_argument('--rho-agg', type=float, default=0.41)
    ap.add_argument('--trials', type=int, default=10)
    ap.add_argument('--n-eff', type=int, nargs='+',
                    default=[2138, 20000, 50000, 131000, 500000])
    ap.add_argument('--win', type=int, default=12)
    args = ap.parse_args()

    with h5py.File(args.h5, 'r') as f:
        N = f['nonces'][:]
        K0 = f['keys'][0]
    base = len(N)
    Kt = np.tile(K0, (base, 1))

    H = sbox_col_hd(Kt, N)                    # (base, 64) factorable predictor
    agg_scale = H.sum(1).std()
    print(f'[+] {base} real nonces, fixed key {bytes(K0).hex()}')
    print(f'[+] per-column HD std {H.std(0).mean():.3f}, '
          f'sum std {agg_scale:.3f}')
    rho_col = args.rho_agg * H.std(0).mean() / agg_scale
    print(f'[+] implied rho_col = {rho_col:.4f} '
          f'(rho_agg {args.rho_agg} x {H.std(0).mean()/agg_scale:.3f})\n')

    rng = np.random.default_rng(0)
    W = 2 * args.win + 1
    print('  N_eff      null      margin   cols recovered')
    for neff in args.n_eff:
        got = tot = 0
        for _ in range(args.trials):
            # fresh nonces: the predictor is a deterministic function of
            # (key, nonce), so a budget curve needs genuine nonce diversity,
            # not resampling of the 223 available ones.
            n = neff
            Ns = rng.integers(0, 256, (n, 16), dtype=np.uint8)
            Hs = sbox_col_hd(np.tile(K0, (n, 1)), Ns)
            x = zs(Hs.sum(1)) + np.sqrt(1.0/args.rho_agg**2 - 1.0) \
                * rng.standard_normal(n)
            xz = zs(x)
            ok = 0
            for c in range(64):
                (b1, m1), (b2, m2) = key_bit_sites(c)
                cands = []
                for hyp in range(4):
                    kk = K0.copy()
                    if hyp & 1:
                        kk[b1] ^= m1
                    if hyp & 2:
                        kk[b2] ^= m2
                    h = sbox_col_hd(np.tile(kk, (n, 1)), Ns)[:, c]
                    cands.append(np.abs(zs(h) @ xz) / n)
                if int(np.argmax(cands)) == 0:
                    ok += 1
            got += ok
            tot += 64
        null = np.sqrt(2 * np.log(4 * W) / neff)
        print(f'  {neff:7d}   {null:.4f}   {rho_col/null:5.2f}x   '
              f'{got}/{tot} ({100*got/max(tot,1):.1f}%)')

    print('\n64/64 per trial = the full 128-bit key recovered.')
    print('Trials reuse the real nonces (resampled when N_eff > capture).')


if __name__ == '__main__':
    main()
