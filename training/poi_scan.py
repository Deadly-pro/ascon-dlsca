#!/usr/bin/env python3
r"""poi_scan.py — TVLA-style per-sample SNR scan for byte HW and per-bit leakage.

Finds which samples carry key-byte HW signal and per-bit signal.
Prints top-3 sample regions per byte for the CNN crop window.

Usage:
  .venv/bin/python training/poi_scan.py training/data/prof16sc_m32.npz
"""
import numpy as np, sys
sys.path.insert(0, 'training')
import argparse

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz')
    args = ap.parse_args()

    d = np.load(args.npz, allow_pickle=True)
    X = d['traces'].astype(np.float64)
    keys = d['keys']
    n = len(X); split = int(0.8 * n)
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], float)
    B = np.zeros((n, 128))
    for b in range(16):
        for j in range(8): B[:, b * 8 + j] = (keys[:, b] >> j) & 1

    Xz = (X - X.mean(0)) / (X.std(0) + 1e-12)
    Xtr, Xva = Xz[:split], Xz[split:]

    # ---- Byte-HW SNR per sample ----
    # SNR = between-HW-class variance / within-HW-class variance
    print('=== BYTE-HW SNR (top-3 windows per byte) ===')
    for b in range(16):
        y = hw[:split, b].astype(int)
        classes = np.unique(y)
        class_means = np.array([Xtr[y == c].mean(0) for c in classes])
        grand_mean = Xtr.mean(0)
        between = ((class_means - grand_mean) ** 2).sum(0) / len(classes)
        within = np.array([Xtr[y == c].var(0).mean() for c in classes]).mean(0)
        snr = between / (within + 1e-12)
        # find top-3 windows
        smooth = np.convolve(snr, np.ones(21) / 21, mode='same')
        peaks = []
        for _ in range(3):
            pk = smooth.argmax()
            if smooth[pk] < 0.01:
                break
            lo, hi = max(0, pk - 10), min(len(snr), pk + 11)
            peaks.append((pk, smooth[pk]))
            smooth[lo:hi] = 0
        print(f'  byte {b:2d}: top-3 peaks: {", ".join(f"@{pk} (SNR={v:.2f})" for pk, v in peaks)}', flush=True)

    # ---- Per-bit correlation (held-out) ----
    print('\n=== PER-BIT HELD-OUT |r| (top-3 samples per bit) ===')
    for b in range(2):
        for j in range(8):
            c = b * 8 + j
            y = B[:split, c]
            z = (y - y.mean()) / (y.std() + 1e-12)
            r_tr = z @ Xtr / split
            r_va = np.array([np.corrcoef(Xva[:, pk], B[split:, c])[0, 1] for pk in [np.abs(r_tr).argmax()]])
            pk = np.abs(r_tr).argmax()
            r_va = abs(np.corrcoef(Xva[:, pk], B[split:, c])[0, 1])
            print(f'  byte {b} bit {j}: peak @ {pk}, held-out r = {r_va:.3f}', flush=True)

    # ---- Full per-bit summary (all bits) ----
    print('\n=== PER-BIT SUMMARY (all 128 bits) ===')
    r_all = np.zeros(128)
    for c in range(128):
        y = B[:split, c]
        z = (y - y.mean()) / (y.std() + 1e-12)
        pk = int(np.abs(z @ Xtr / split).argmax())
        r_all[c] = abs(np.corrcoef(Xva[:, pk], B[split:, c])[0, 1])
    print(f'  mean r = {r_all.mean():.3f}, max r = {r_all.max():.3f}, bits > 0.1: {(r_all > 0.1).sum()}/128', flush=True)

if __name__ == '__main__':
    main()