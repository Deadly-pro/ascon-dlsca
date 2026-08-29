#!/usr/bin/env python3
r"""Cross-era leakage audit: model-free SNR scan of every dataset.

For each Dataset/*.h5: align+zscore (pipeline order), compute round-1
S-box HW labels and KADD labels from stored keys/nonces, measure max
per-column / per-byte SNR. Answers: does ANY captured era contain
first-order key-dependent leakage?
"""
import sys
import glob
import os

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import h5py
import labels as lab
from preprocess import align_trace, zscore


def snr_scan(X, y, min_class=30):
    mu_all = X.mean(0)
    betw = np.zeros(X.shape[1])
    within = np.zeros(X.shape[1])
    for cl in np.unique(y):
        m = y == cl
        if m.sum() < min_class:
            continue
        xc = X[m]
        betw += m.sum() * (xc.mean(0) - mu_all) ** 2
        within += ((xc - xc.mean(0)) ** 2).sum(0)
    snr = 10 * np.log10((betw / len(X)) / (within / len(X)))
    return float(np.nanmax(snr))


def audit(path, n_max=4000):
    f = h5py.File(path, 'r')
    n = f['traces'].shape[0]
    idx = np.linspace(0, n - 1, min(n, n_max), dtype=int)
    tr = f['traces'][idx].astype(np.float64)
    ks = f['keys'][idx]
    ns = f['nonces'][idx]
    w = tr.shape[1]
    # pipeline order: align -> zscore
    ref = tr.mean(0)
    Z = np.array([zscore(align_trace(t, ref)) for t in tr])
    kb = np.frombuffer(b''.join(k.tobytes() for k in ks), np.uint8)
    kb = kb.reshape(len(idx), 16)
    nb = ns.reshape(len(idx), 16)
    lsbox = lab.round1_sbox_hw(kb, nb)
    lkadd = lab.kadd_words_hw(kb, nb)
    sbox_best = max(snr_scan(Z[:, :w], lsbox[:, c]) for c in range(64))
    kadd_best = max(snr_scan(Z[:, :w], lkadd[:, b]) for b in range(8))
    # majority-class baseline for context
    maj = max(np.bincount(lsbox[:, c]).max() for c in range(64)) / len(idx)
    return n, f.attrs.get('gain_db', '?'), sbox_best, kadd_best, maj


if __name__ == '__main__':
    print(f'{"dataset":34s} {"n":>5} {"gain":>4} {"sboxSNR":>8} '
          f'{"kaddSNR":>8} {"majClass":>8}')
    for p in sorted(glob.glob(os.path.join(ROOT, 'Dataset', '*.h5'))):
        try:
            n, g, s, k, mj = audit(p)
            print(f'{os.path.basename(p):34s} {n:5d} {str(g):>4} '
                  f'{s:+8.1f} {k:+8.1f} {mj*100:7.1f}%')
        except Exception as e:
            print(f'{os.path.basename(p):34s} SKIP: {e}')
