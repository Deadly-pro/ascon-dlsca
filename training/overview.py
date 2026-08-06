#!/usr/bin/env python3
r"""overview.py — side-by-side comparison of all captured datasets.

Prints one row per Dataset/*.h5 with the metrics that decide whether a
capture is usable for training:

    size / verified / clip-rate / flat-rate / alignment jitter / KADD-SNR in
    the crypto-op window (first 50 us).

Usage:
    python3 training/overview.py
    python3 training/overview.py Dataset/*.h5
"""
import glob
import os
import sys

import h5py
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ascon_ref import kadd_labels

OP_WINDOW = 2000   # samples 0..2000 == 0..50 us @ 40 MHz


def hw_bits(x):
    return np.unpackbits(np.asarray(x, dtype=np.uint8)[:, None], axis=1,
                         bitorder='little').sum(axis=1)


def snr(traces, labels):
    classes = np.unique(labels)
    if len(classes) < 2:
        return np.zeros(traces.shape[1])
    means = np.array([traces[labels == c].mean(0) for c in classes])
    vars_ = np.array([traces[labels == c].var(0) for c in classes])
    return means.var(0) / np.maximum(vars_.mean(0), 1e-12)


def analyze(path):
    with h5py.File(path, 'r') as f:
        attrs = dict(f.attrs)
        tr = f['traces'][:]
        keys = f['keys'][:]
        nonces = f['nonces'][:]
    n, samples = tr.shape
    clip = (np.abs(tr).max(1) > 0.49).mean() * 100
    flat = (tr.std(1) < 0.01).mean() * 100
    kadd = 10 * np.log10(snr(tr[:, :OP_WINDOW],
                             kadd_labels([bytes(x) for x in keys],
                                         [bytes(x) for x in nonces])).max())
    return (f'{n:5d}x{samples:<6d}', clip, flat,
            f'{attrs.get("gain_db", "?")} dB', kadd)


def main():
    paths = sys.argv[1:] or sorted(glob.glob('Dataset/*.h5'))
    if not paths:
        sys.exit('no Dataset/*.h5 found (run from repo root)')
    print(f'{"file":<14} {"shape":<14} {"clip":>6} {"flat":>6} {"gain":>6} '
          f'{"KADD-SNR(0-50us)":>16}  note')
    for p in paths:
        base = os.path.basename(p)
        shape, clip, flat, gain, kadd = analyze(p)
        note = ''
        if flat > 5:
            note = '<- high flat rate, drop'
        elif clip > 10:
            note = '<- high clip rate'
        elif kadd > 5:
            note = '<- strongest signal'
        print(f'{base:<14} {shape:<14} {clip:6.1f}% {flat:6.1f}% {gain:>6} '
              f'{kadd:13.1f} dB  {note}')


if __name__ == '__main__':
    main()
