#!/usr/bin/env python3
r"""Recover fixed-key bits via per-bit linear regression from M-averaged traces.

Profiles a ridge regression W: trace -> 128 key bits on the random-key set
(cfgD.h5), then applies W to M=64-averaged traces of a single fixed key
(edge_vs_m.h5) and reports per-bit recovery accuracy vs the true key.
"""
import argparse
import numpy as np
import h5py


def zscore(X):
    mu = X.mean(axis=1, keepdims=True)
    sd = X.std(axis=1, keepdims=True)
    return (X - mu) / sd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--profile', default='Dataset/cfgD.h5')
    ap.add_argument('--avg', default='Dataset/edge_vs_m.h5')
    ap.add_argument('--key', default='1ea88515a053f3937860a1b2e247063b')
    ap.add_argument('--no-zscore', action='store_true')
    args = ap.parse_args()

    with h5py.File(args.profile, 'r') as fh:
        trp = np.asarray(fh['traces'][:], dtype=np.float32)
        kp = np.asarray(fh['keys'][:], dtype=np.uint8)
    n = len(trp)
    if not args.no_zscore:
        trp = zscore(trp)
    Y = np.unpackbits(kp, axis=1).astype(np.float64)  # (n, 128)

    X = trp.astype(np.float64)
    XtX = X.T @ X + 1e-3 * np.eye(X.shape[1])
    W = np.linalg.solve(XtX, X.T @ Y)  # (n_samp, 128)

    pred_in = X @ W
    acc_in = ((pred_in > 0) == (Y > 0)).mean(axis=0)
    print(f'profile n={n} in-sample bit acc: mean {acc_in.mean():.4f} '
          f'best {acc_in.max():.4f}  # of >=0.6: {(acc_in>0.6).sum()}/128')

    with h5py.File(args.avg, 'r') as fh:
        tavg = np.asarray(fh['traces'][:], dtype=np.float32)  # (30,64,n_samp)
    M = tavg.shape[1]
    Xa = tavg.mean(axis=1)
    if not args.no_zscore:
        Xa = zscore(Xa)
    Xa = Xa.astype(np.float64)

    true_bits = np.unpackbits(np.frombuffer(bytes.fromhex(args.key),
                                            dtype=np.uint8)) > 0
    pred_a = Xa @ W
    bits = pred_a > 0
    per_trace = (bits == true_bits).mean(axis=1)
    per_bit = (bits == true_bits).mean(axis=0)

    print(f'M={M} averaged traces (30 nonces), key {args.key}')
    print(f'per-trace bit acc: mean {per_trace.mean():.4f} +/- {per_trace.std():.4f}'
          f' (chance 0.5)')
    print(f'  min {per_trace.min():.4f} max {per_trace.max():.4f}')
    print(f'per-bit acc: mean {per_bit.mean():.4f}; bits>0.6: {(per_bit>0.6).sum()}/128; '
          f'bits<0.4: {(per_bit<0.4).sum()}/128')
    n_half = max(1, int(round(bits.shape[1] / 2)))
    # score the whole 128-bit key (chance of exact match = 2^-128, so just best-trace Hamming-ish)
    best = per_trace.max()
    print(f'best single averaged nonce recovers {best*128:.0f}/128 bits '
          f'({best*100:.1f}%)')


if __name__ == '__main__':
    main()