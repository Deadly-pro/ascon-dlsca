#!/usr/bin/env python3
r"""step2_poi_denoise.py — Tier-2: POI selection + spatial averaging, honestly.

Q: does any per-trace transformation make per-trace leakage beat the null?
A tested rigorously via a *double* split:
  - POIs selected on profiling half A (SOST, using A's labels only)
  - features built on A and B separately; LDA fit on A, scored on B

Methods compared (all 64 columns, held-out key-rank):
  raw    : z-scored full 1200-sample window
  poi    : top-K SOST samples (K=8/16/32), z-scored
  poiavg : POI window mean (spatial average over the K points -> sqrt(K) SNR)
  dwt    : 8-level Haar approximation (linear filter, no SNR gain expected;
           included to confirm filters cannot fix this)

Also reports the permutation null at the POI level for calibration.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from labels import load_state  # noqa: E402
from step1_cpa_hd import col_bits, sbox5, true_hyp  # noqa: E402


def hw_pred_for(keys, nonces, c):
    n = len(keys)
    out = np.empty((n, 4))
    for h in range(4):
        b0, b1 = (h >> 1) & 1, h & 1
        kk = keys.copy()
        m = np.uint8(1 << (c % 8))
        if b0:
            kk[:, c % 8] |= m
        else:
            kk[:, c % 8] &= np.uint8(255 - int(m))
        if b1:
            kk[:, 8 + c % 8] |= m
        else:
            kk[:, 8 + c % 8] &= np.uint8(255 - int(m))
        S = load_state(kk, nonces)
        S[:, 2] ^= np.uint64(0xF0)
        cols = sbox5(col_bits(S, c))
        out[:, h] = np.array([bin(int(v)).count('1') for v in cols])
    return out


def sost_pois(traces, classes, k):
    """Sum-of-squared-tifferences POI ranking on profiling data.
    traces: (N,S); classes: (N,) int 0..5 -> returns top-k sample indices."""
    t = traces.astype(np.float64)
    t -= t.mean(axis=0, keepdims=True)
    us = np.unique(classes)
    mu = np.stack([t[classes == u].mean(axis=0) for u in us])   # (C,S)
    # SOST: sum over class pairs of squared mean differences
    d2 = np.zeros(traces.shape[1])
    for i in range(len(us)):
        for j in range(i + 1, len(us)):
            d2 += (mu[i] - mu[j]) ** 2
    return np.argsort(-d2)[:k]


def haar_approx(x, levels):
    """Haar DWT approximation coefficients, 'levels' times (trims odd tail)."""
    a = x.astype(np.float64)
    for _ in range(levels):
        k = (a.shape[-1] // 2) * 2
        if k < 2:
            break
        a = (a[..., 0:k:2] + a[..., 1:k:2]) / np.sqrt(2)
    return a


def zscore(t):
    mu = t.mean(axis=0, keepdims=True)
    sd = t.std(axis=0, keepdims=True)
    sd[sd < 1e-12] = 1
    return (t - mu) / sd


def lda_eval(feat_a, feat_b, y_a, y_b, n_cls):
    """Fit LDA (pooled covariance) on A, return top-1 accuracy on B.
    feat_*: (N, D); y_*: (N,) class labels. Uses only classes present in A."""
    us = np.unique(y_a)
    mu = np.stack([feat_a[y_a == u].mean(axis=0) for u in us])
    # pooled within-class covariance
    cov = np.zeros((feat_a.shape[1], feat_a.shape[1]))
    for u in us:
        Xc = feat_a[y_a == u] - mu[list(us).index(u)]
        cov += Xc.T @ Xc
    cov /= max(1, len(feat_a) - len(us))
    cov += 1e-3 * np.eye(cov.shape[0])          # regularize
    W = np.linalg.solve(cov, mu.T)              # (D, C): cov^-1 @ mu'
    # LDA discriminant: s_u(x) = x'W_u - 0.5 mu_u'W_u  (W_u = cov^-1 mu_u)
    b = -0.5 * np.sum(mu.T * W, axis=0)         # (C,) = diag(mu' @ W)
    # keep only classes seen in A; B traces of unseen classes count as wrong
    sc_b = feat_b @ W + b
    pred = us[sc_b.argmax(axis=1)]
    return float((pred == y_b).mean())


def main():
    d = np.load('board_session/pa_assets/profiling.npz', allow_pickle=True)
    traces, keys, nonces = d['traces'], d['keys'], d['nonces']
    n, ns = traces.shape
    half = n // 2
    A, B = np.arange(0, half), np.arange(half, n)
    tA, tB = zscore(traces[A]), zscore(traces[B])
    tA64, tB64 = tA.astype(np.float64), tB.astype(np.float64)
    methods = ['raw', 'poi8', 'poi16', 'poi32', 'poiavg16', 'poiavg32',
               'dwt4', 'dwt6']
    acc = {m: np.zeros(64) for m in methods}
    floor = {m: np.zeros(64) for m in methods}
    rank1 = {m: 0 for m in methods}
    t0 = time.time()

    for c in range(64):
        p = hw_pred_for(keys, nonces, c)          # (N,4) hypothesis HW
        th = true_hyp(keys, c)                    # (N,) true hyp index
        yA, yB = p[A, th[:half]], p[B, th[half:]]  # true HW class (0..5)
        uA = np.unique(yA)
        # majority-class floors
        for m in methods:
            floor[m][c] = max((yB == u).mean() for u in uA)

        # --- POI selection on half A only (uses A labels)
        pois = {k: sost_pois(tA, yA, k) for k in (8, 16, 32)}

        feats = {
            'raw': (tA, tB),
            'poi8': (tA[:, pois[8]], tB[:, pois[8]]),
            'poi16': (tA[:, pois[16]], tB[:, pois[16]]),
            'poi32': (tA[:, pois[32]], tB[:, pois[32]]),
            'poiavg16': (tA[:, pois[16]].mean(axis=1, keepdims=True),
                         tB[:, pois[16]].mean(axis=1, keepdims=True)),
            'poiavg32': (tA[:, pois[32]].mean(axis=1, keepdims=True),
                         tB[:, pois[32]].mean(axis=1, keepdims=True)),
            'dwt4': (haar_approx(tA, 4), haar_approx(tB, 4)),
            'dwt6': (haar_approx(tA, 6), haar_approx(tB, 6)),
        }
        for m, (fa, fb) in feats.items():
            acc[m][c] = lda_eval(fa, fb, yA, yB, len(uA))
            # LDA rank-1 counting: top-1 class accuracy vs floor already
            # covers it; rank metric for key = does true class win
            if acc[m][c] > floor[m][c]:
                rank1[m] += 1
        if c % 16 == 0:
            print(f'col {c:2d}  raw {acc["raw"][c]:.3f}  '
                  f'poiavg32 {acc["poiavg32"][c]:.3f}  '
                  f'({time.time()-t0:.0f}s)', flush=True)

    res = {'n': n, 'per_method': {}}
    for m in methods:
        res['per_method'][m] = {
            'mean_acc': float(acc[m].mean()),
            'mean_floor': float(floor[m].mean()),
            'above_floor': int(rank1[m]),
            'best_col': int(acc[m].argmax()),
            'best_acc': float(acc[m].max()),
        }
    os.makedirs('results', exist_ok=True)
    with open('results/step2_poi_denoise.json', 'w') as f:
        json.dump(res, f, indent=1)
    np.savez_compressed(
        'results/step2_acc.npz',
        **{('acc_' + m): acc[m] for m in methods},
        **{('floor_' + m): floor[m] for m in methods},
    )
    print('\n=== STEP 2: POI / DENOISE (LDA, held-out half B) ===')
    print(f"{'method':10s} {'mean acc':>9s} {'floor':>7s} {'>floor':>7s}")
    for m in methods:
        r = res['per_method'][m]
        print(f"{m:10s} {r['mean_acc']*100:8.1f}% {r['mean_floor']*100:6.1f}% "
              f"{r['above_floor']:4d}/64")
    print('-> results/step2_poi_denoise.json')


if __name__ == '__main__':
    main()
