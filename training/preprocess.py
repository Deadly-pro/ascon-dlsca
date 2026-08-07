#!/usr/bin/env python3
r"""preprocess.py — build trainable features + labels from a Dataset/*.h5.

Pipeline (matches the conclusions in training/README.md):

    1. load oracle-verified traces
    2. align every trace to the mean trace (cross-correlation)
    3. crop to the crypto-op window (0..--window samples)
    4. per-trace z-score normalization
    5. labels: Hamming weight (0..5) of the round-1 ASCON S-box output, one
       column per class index (64 columns, computed with the NIST SP 800-232
       reference — exact ground truth, independent of hardware masking).
    6. labels_kadd: Hamming weight (0..8) of each of the 8 bytes of state word
       S[3] after the full initialization permutation + key XOR (the leaky
       intermediate — HW is invariant to bit order, so the byte-level labels
       are exact even where the bit-sliced column packing differs from the
       published S-box table).

Output: training/data/<name>.npz with
    traces (N, W) float32 aligned+z-scored
    labels_sbox (N, 64) uint8
    labels_kadd (N, 8) uint8
    keys (N,16), nonces (N,16)
    and attributes in <name>.json

Usage:
    python3 training/preprocess.py Dataset/main2.h5
    python3 training/preprocess.py Dataset/main.h5 --window 2000
"""
import argparse
import json
import os

import h5py
import numpy as np
from scipy import signal

import labels as lab


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
    return out, ref, shifts, lo, hi


def align_trace(trace, ref):
    """Align a single live trace against a stored reference (adaptive loop)."""
    c = signal.correlate(trace, ref, mode='same', method='fft')
    return np.roll(trace, -int(np.argmax(c) - len(trace) // 2))


def zscore(traces):
    std = traces.std(axis=1, keepdims=True)
    return (traces - traces.mean(axis=1, keepdims=True)) / np.maximum(std, 1e-9)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('h5', help='Dataset/*.h5 capture')
    ap.add_argument('--window', type=int, default=None,
                    help='crop to first W samples (default: min(2000, len))')
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
    print(f'{name}: {traces.shape[0]} traces x {traces.shape[1]} window')

    traces, ref, shifts, lo, hi = align(traces, args.align_k)
    print(f'  alignment shifts {lo}..{hi} samples '
          f'({(hi - lo) / 40e6 * 1e6:.2f} us spread)')

    traces = zscore(traces).astype(np.float32)
    ref = ref.astype(np.float32)
    print(f'  aligned + z-scored traces {traces.shape}')

    labels = lab.round1_sbox_hw(keys, nonces)
    print(f'  round-1 S-box HW labels {labels.shape}, '
          f'class balance column 0: '
          f'{np.bincount(labels[:, 0], minlength=6)}')

    kadd = lab.kadd_words_hw(keys, nonces)
    print(f'  KADD byte-HW labels {kadd.shape}, '
          f'class balance byte 3: '
          f'{np.bincount(kadd[:, 3], minlength=9)}')

    npz = os.path.join(out_dir, f'{name}.npz')
    np.savez_compressed(npz, traces=traces, labels_sbox=labels,
                        labels_kadd=kadd, keys=keys, nonces=nonces,
                        ref=ref)
    meta = {'dataset': args.h5, 'n_traces': int(len(traces)),
            'window': int(win), 'shifts_lo': int(lo), 'shifts_hi': int(hi),
            'npz': npz}
    with open(os.path.join(out_dir, f'{name}.json'), 'w') as f:
        json.dump(meta, f, indent=2)
    print(f'  wrote {npz}')
    print(f'  wrote {os.path.join(out_dir, name + ".json")}')


if __name__ == '__main__':
    main()
