#!/usr/bin/env python3
r"""preprocess.py — build trainable features + labels from a Dataset/*.h5.

Pipeline (matches the conclusions in training/README.md):

    1. load oracle-verified traces
    2. align every trace to the mean trace (cross-correlation)
    3. crop to the crypto-op window (0..--window samples)
    4. per-trace z-score normalization
    5. optional second-order centered-product features (adjacent / one-crypto-clock
       lags), the standard countermeasure for masked d=1 cores whose first-order
       leakage is weak
    6. labels: Hamming weight of each byte of S[3] after ASCON init + KADD
       (computed with the NIST SP 800-232 reference), 9 classes per byte

Output: training/data/<name>.npz with
    features (N, F), labels (N, 8), keys (N,16), nonces (N,16)
    and attributes in <name>.json

Usage:
    python3 training/preprocess.py Dataset/main2.h5
    python3 training/preprocess.py Dataset/main.h5 --window 2000 --order 2
"""
import argparse
import json
import os
import sys

import h5py
import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ascon_ref  # noqa: E402


def align(traces, k=200):
    ref = traces.mean(axis=0)
    shifts = np.empty(len(traces), dtype=np.int64)
    for i in range(len(traces)):
        c = signal.correlate(traces[i], ref, mode='same', method='fft')
        shifts[i] = int(np.argmax(c) - traces.shape[1] // 2)
    lo, hi = shifts.min(), shifts.max()
    out = np.empty_like(traces)
    for i, s in enumerate(shifts):
        out[i] = np.roll(traces[i], -int(s))
    return out, shifts, lo, hi


def zscore(traces):
    std = traces.std(axis=1, keepdims=True)
    return (traces - traces.mean(axis=1, keepdims=True)) / np.maximum(std, 1e-9)


def centered_products(traces, lags=(1, 4)):
    c = traces - traces.mean(axis=1, keepdims=True)
    cols = [c]
    for lag in lags:
        cols.append(c[:, lag:] * c[:, :-lag])
    return np.concatenate(cols, axis=1)


def byte_labels(keys_bytes, nonces_bytes):
    labels = np.empty((len(keys_bytes), 8), dtype=np.uint8)
    for i, (key, nonce) in enumerate(zip(keys_bytes, nonces_bytes)):
        S = [0, 0, 0, 0, 0]
        ascon_ref.ascon_initialize(S, 128, 16, 12, 8, 1, key, nonce)
        w3 = S[3]
        for b in range(8):
            labels[i, b] = (w3 & 0xFF).bit_count()
            w3 >>= 8
    return labels


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('h5', help='Dataset/*.h5 capture')
    ap.add_argument('--window', type=int, default=None,
                    help='crop to first W samples (default: min(2000, len))')
    ap.add_argument('--order', type=int, default=2, choices=(1, 2),
                    help='1 = raw z-scored traces, 2 = + centered products')
    ap.add_argument('--lags', type=int, nargs='*', default=(1, 4),
                    help='centered-product lags in samples (default 1 4)')
    ap.add_argument('--align-k', type=int, default=200,
                    help='traces used to estimate alignment reference')
    args = ap.parse_args()

    name = os.path.splitext(os.path.basename(args.h5))[0]
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(out_dir, exist_ok=True)

    with h5py.File(args.h5, 'r') as f:
        traces = f['traces'][:]
        keys = f['keys'][:]
        nonces = f['nonces'][:]

    win = args.window if args.window else min(2000, traces.shape[1])
    traces = traces[:, :win]
    print(f'{name}: {traces.shape[0]} traces x {traces.shape[1]} window '
          f'(aligned, z-scored)')

    traces, shifts, lo, hi = align(traces, args.align_k)
    print(f'  alignment shifts {lo}..{hi} samples '
          f'({(hi - lo) / 40e6 * 1e6:.2f} us spread)')

    traces = zscore(traces)
    features = centered_products(traces, args.lags) if args.order == 2 else traces
    print(f'  features {features.shape} (order={args.order})')

    labels = byte_labels([bytes(k) for k in keys], [bytes(n) for n in nonces])
    print(f'  labels HW(S[3] byte) per trace {labels.shape}, '
          f'classes {[len(np.unique(labels[:, b])) for b in range(8)]}')

    npz = os.path.join(out_dir, f'{name}.npz')
    np.savez_compressed(npz, features=features, labels=labels,
                        keys=keys, nonces=nonces)
    meta = {'dataset': args.h5, 'n_traces': int(len(traces)),
            'window': int(win), 'order': args.order, 'lags': list(args.lags),
            'shifts_lo': int(lo), 'shifts_hi': int(hi), 'npz': npz}
    with open(os.path.join(out_dir, f'{name}.json'), 'w') as f:
        json.dump(meta, f, indent=2)
    print(f'  wrote {npz}')
    print(f'  wrote {os.path.join(out_dir, name + ".json")}')


if __name__ == '__main__':
    main()
