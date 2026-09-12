#!/usr/bin/env python3
r"""confidence_audit.py — what is the round-HD correlation actually made of?

Before building an attack on the round-HD signal, three threats have to be
tested, not asserted:

T1. INTERFACE CONFOUND.  The round HD is a function of (key, nonce).  The
    nonce and key are written over the host interface, and we know that
    interface traffic leaks (|r| = 0.48-0.54 for key HW).  So a correlation
    between round HD and trace could be the NONCE/KEY BUS rather than the
    crypto.  Test: partial the interface predictors out of BOTH sides and see
    whether the round-HD correlation survives.

T2. WHICH LAYER?  The attack decomposes the SUBSTITUTION layer, which is
    bitwise across columns (and therefore factorable).  But we have only ever
    correlated the FULL round (substitution + diffusion).  If the substitution
    layer carries little of the correlation, the factorable decomposition is
    weak even if the full-round signal is strong.  Test: correlate
    substitution-layer HD and diffusion-layer HD separately.

T3. TIMING SEPARATION.  If the round-HD peak sits at the same samples as the
    interface activity, T1 is confirmed regardless of partialling.  Report the
    peak sample of every predictor.

Usage:
  .venv/bin/python training/confidence_audit.py <h5> [<h5> ...]
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from labels import (load_state, permutation_round,  # noqa: E402
                    substitution_layer, linear_diffusion)

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


def hd(A, B):
    return popcount64(A ^ B).sum(1).astype(np.float64)


def zs(a):
    a = np.asarray(a, float)
    s = a.std()
    return (a - a.mean()) / (s if s > 1e-12 else 1.0)


def resid_on(Y, Z):
    """Column-wise residual of Y on covariate Z (Z: (N,) or (N,K))."""
    Z = np.asarray(Z, float)
    if Z.ndim == 1:
        Z = Z[:, None]
    A = np.column_stack([np.ones(len(Z)), Z])
    coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
    return Y - A @ coef


def main():
    import h5py
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', nargs='+')
    ap.add_argument('--rounds', type=int, default=12)
    ap.add_argument('--win', type=int, default=12)
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
    print(f'[+] {Ntr} traces, boxcar {sm}, T={T}\n')

    pc = np.array([bin(v).count('1') for v in range(256)], dtype=np.float64)
    nonce_hw = pc[N].sum(1)
    key_hw = pc[K].sum(1)
    print(f'[+] interface covariates: nonce_hw std {nonce_hw.std():.2f}, '
          f'key_hw std {key_hw.std():.2f}')

    # residualise the traces on the interface covariates (per sample)
    Xr = resid_on(Xz, np.column_stack([nonce_hw, key_hw]))
    Xrz = (Xr - Xr.mean(0)) / np.where(Xr.std(0) > 0, Xr.std(0), 1.0)

    def peak(pred, traces):
        C = np.abs(zs(pred) @ traces / Ntr)
        return float(C.max()), int(C.argmax())

    print('\n  round  full-HD      sbox-layer    diff-layer    '
          'full | nonce/key partialled out')
    S = load_state(K, N)
    for r in range(args.rounds):
        Sc = S.copy()
        Sc[:, 2] ^= np.uint64(0xF0 - r * 0x10 + r)
        S1 = substitution_layer(Sc)
        S2 = linear_diffusion(S1)
        c = FIRST_ROUND_SAMPLE + SAMPLES_PER_ROUND * r
        lo, hi = max(0, c - args.win), min(T, c + args.win + 1)

        f_full = hd(Sc, S2)
        f_sbox = hd(Sc, S1)
        f_diff = hd(S1, S2)

        vf, pf = peak(f_full, Xz[:, lo:hi])
        vs, ps = peak(f_sbox, Xz[:, lo:hi])
        vd, pd = peak(f_diff, Xz[:, lo:hi])
        vr, pr = peak(f_full, Xrz[:, lo:hi])
        S = S2
        print(f'   {r+1:2d}    {vf:.4f}@{pf+lo:4d}  {vs:.4f}@{ps+lo:4d}  '
              f'{vd:.4f}@{pd+lo:4d}   {vr:.4f}@{pr+lo:4d}')

    print('\nT3: compare these peak samples with the interface controls:')
    for nm, v in (('nonce_hw', nonce_hw), ('key_hw', key_hw)):
        val, pk = peak(v, Xz)
        print(f'    {nm:9s} peaks at sample {pk:4d} ({pk/fs*1e6:5.2f} us) '
              f'|r| {val:.4f}')
    print(f'    (round 1 peaks near sample {FIRST_ROUND_SAMPLE})')


if __name__ == '__main__':
    main()
