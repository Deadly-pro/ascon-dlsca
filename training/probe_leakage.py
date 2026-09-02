#!/usr/bin/env python3
r"""probe_leakage.py — decisive per-trace leakage probe on a profiling npz.

For S-box columns and KADD bytes: held-out logistic + KNN accuracy vs the
majority-class floor. A target is ONLY usable if accuracy beats the floor
by a clear margin (default +5 pts). Also runs the shortcut detector:
predicting the col-0 nonce bits from the trace — ~100% there while S-box
sits at floor means nonce-readout (public data), NOT secret leakage.

Run on M-averaged captures (--avg-m 64) where single-trace SNR is below
every probe floor.

Usage:
    .venv/bin/python training/probe_leakage.py training/data/avg64.npz
"""
import argparse
import os
import sys
import warnings

import numpy as np

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SBOX_COLS = [0, 1, 31, 63]
KADD_BYTES = [0, 3, 7]
MARGIN = 5.0  # pts above floor to call it real


def _floor(y):
    return 100.0 * np.bincount(y).max() / len(y)


def _probes(Xtr, ytr, Xva, yva):
    from sklearn.linear_model import LogisticRegression
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.metrics import accuracy_score
    lr = LogisticRegression(max_iter=300).fit(Xtr, ytr)
    knn = KNeighborsClassifier(15).fit(Xtr, ytr)
    return (100.0 * accuracy_score(yva, lr.predict(Xva)),
            100.0 * accuracy_score(yva, knn.predict(Xva)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz', help='training/data/*.npz from preprocess.py')
    args = ap.parse_args()

    d = np.load(args.npz, allow_pickle=True)
    X = d['traces'].astype(np.float32)
    sb = d['labels_sbox'] if 'labels_sbox' in d else d['labels']
    ka = d['labels_kadd']
    nonces = d['nonces']
    n = len(X)
    split = int(n * 0.8)
    Xtr, Xva = X[:split], X[split:]
    print(f'[+] {n} traces x {X.shape[1]} samples (train {split} / val {n-split})')
    if 'avg_m' in d:
        print(f'[+] capture averaging M={int(d["avg_m"])}')

    hits = []
    print('\nS-box round-1 HW (per column):')
    for c in SBOX_COLS:
        y = sb[:, c].astype(int)
        floor = _floor(y[:split])
        lr, knn = _probes(Xtr, y[:split], Xva, y[split:])
        ok = max(lr, knn) > floor + MARGIN
        hits.append(ok)
        print(f'  col {c:2d}: floor {floor:5.1f}%  logistic {lr:5.1f}%  KNN {knn:5.1f}%'
              f'  {"LEAKS" if ok else "floor"}')

    print('\nKADD byte HW:')
    for b in KADD_BYTES:
        y = ka[:, b].astype(int)
        floor = _floor(y[:split])
        lr, knn = _probes(Xtr, y[:split], Xva, y[split:])
        ok = max(lr, knn) > floor + MARGIN
        hits.append(ok)
        print(f'  byte {b}: floor {floor:5.1f}%  logistic {lr:5.1f}%  KNN {knn:5.1f}%'
              f'  {"LEAKS" if ok else "floor"}')

    print('\nShortcut detector (col-0 nonce bits from trace, chance 25%):')
    y = ((nonces[:, 0] & 1) | ((nonces[:, 8] & 1) << 1)).astype(int)
    lr, knn = _probes(Xtr, y[:split], Xva, y[split:])
    print(f'  (n0,n1): logistic {lr:5.1f}%  KNN {knn:5.1f}%'
          f'  {"<- nonce readable (public)" if max(lr, knn) > 60 else ""}')

    print('\nVERDICT:',
          'LEAKAGE PRESENT -> train a profile and attack' if any(hits)
          else 'NO per-trace leakage above floor -> negative result at this M')


if __name__ == '__main__':
    main()