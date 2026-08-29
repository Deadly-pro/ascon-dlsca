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
from scipy import signal, ndimage

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
    """Per-trace z-score (works for a single 1-D trace or a (N, W) batch)."""
    single = traces.ndim == 1
    if single:
        traces = traces[None]
    std = traces.std(axis=1, keepdims=True)
    out = (traces - traces.mean(axis=1, keepdims=True)) / np.maximum(std, 1e-9)
    return out[0] if single else out


def auto_center(traces, window, keys=None, nonces=None):
    """Find the crop offset that best covers the key-dependent leakage.

    Energy is a bad proxy (the trigger/initialization burst is high-energy
    but label-constant). The correct POI is where the trace correlates with
    an intermediate label — the CPA first pass. We score every candidate
    offset by the summed |corr| (over samples in the window) between the
    trace and the strongest available label:

      1. KADD word-3 byte HW (all 8 bytes summed) — the strongest leak
         on this board (SNR -4 dB vs -17 dB for sbox columns),
      2. fallback: sbox column 0 HW.

    Returns (offset, corr_profile).
    """
    from scipy.stats import pearsonr as _pr  # noqa: F401  (kept for clarity)
    T = traces.shape[1]
    n = min(len(traces), 2000)
    tr = traces[:n]
    if keys is not None and nonces is not None:
        kadd = lab.kadd_words_hw(keys[:n], nonces[:n]).sum(axis=1)
        lbl = kadd.astype(np.float64)
    else:
        sb = lab.round1_sbox_hw(np.zeros((n, 16), np.uint8),
                                np.zeros((n, 16), np.uint8))
        lbl = np.zeros(n)  # not usable without keys/nonces; energy fallback
    # single-sample Pearson correlation with the label (CPA first pass).
    # tr is (n, T): the label-correlation is computed PER SAMPLE (axis T),
    # so we contract the label (n,) against the trace axis (n) and keep the
    # sample axis -> 'ji,j->i' (j = trace index, i = sample index).
    lc = lbl - lbl.mean()
    denom = np.sqrt(((tr - tr.mean(1, keepdims=True)) ** 2).sum(0)) * \
        np.sqrt((lc ** 2).sum())
    corr = np.einsum('ji,j->i', tr, lc) / np.maximum(denom, 1e-12)
    corr = np.abs(corr)
    # smooth so a single sample does not dominate
    smooth = ndimage.uniform_filter1d(corr, size=max(1, window // 8))
    if smooth.max() < 1e-9:
        # fall back to energy
        std = traces.std(axis=0)
        smooth = ndimage.uniform_filter1d(std, size=max(1, window // 8))
    off = np.arange(T - window + 1)
    if len(off) == 0:
        return 0, smooth
    energy = np.array([smooth[o:o + window].sum() for o in off])
    offset = int(np.argmax(energy))
    return offset, smooth


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('h5', help='Dataset/*.h5 capture')
    ap.add_argument('--window', type=int, default=None,
                    help='crop to W samples (default: min(2000, len))')
    ap.add_argument('--offset', type=int, default=0,
                    help='crop start sample (default 0; --auto-center overrides)')
    ap.add_argument('--auto-center', action='store_true',
                    help='find the highest-energy window automatically and '
                         'crop there (the leakage location shifts with the '
                         'trigger path — CW-Lite peaked at sample 391, Husky '
                         'at ~1197)')
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
    traces, ref, shifts, lo, hi = align(traces, args.align_k)
    print(f'  alignment shifts {lo}..{hi} samples '
          f'({(hi - lo) / 40e6 * 1e6:.2f} us spread)')

    if args.auto_center:
        args.offset, _energy = auto_center(traces, win, keys, nonces)
        print(f'  auto-center: highest-leakage window starts at sample '
              f'{args.offset} ({(args.offset) / 40e6 * 1e6:.2f} us), '
              f'ends at {args.offset + win} '
              f'({(args.offset + win) / 40e6 * 1e6:.2f} us)')

    if args.offset + win > traces.shape[1]:
        sys.exit(f'offset {args.offset} + window {win} > trace length '
                 f'{traces.shape[1]}')
    traces = traces[:, args.offset:args.offset + win]
    print(f'{name}: {traces.shape[0]} traces x {traces.shape[1]} window '
          f'(offset {args.offset})')

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
                        ref=ref, offset=np.int64(args.offset))
    meta = {'dataset': args.h5, 'n_traces': int(len(traces)),
            'window': int(win), 'offset': int(args.offset),
            'shifts_lo': int(lo), 'shifts_hi': int(hi),
            'npz': npz}
    with open(os.path.join(out_dir, f'{name}.json'), 'w') as f:
        json.dump(meta, f, indent=2)
    print(f'  wrote {npz}')
    print(f'  wrote {os.path.join(out_dir, name + ".json")}')


if __name__ == '__main__':
    main()
