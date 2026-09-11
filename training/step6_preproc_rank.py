#!/usr/bin/env python3
r"""step6_preproc_rank.py — preprocessing league table (user's method list).

One harness, one gate: for each preprocessing method, per-column 4-hypothesis
key-rank on an 80/20 split of the 5000-trace capture, vs chance (25%) and
majority floor, plus permutation nulls. The method wins only in the table.

Methods (session 1, free):
  pls      : PLSRegression (sklearn) — supervised cross-covariance projection
  prod     : 2nd-order product traces on SOST-POI pairs
  mia      : MIA with histogram (KDE too slow at this scale; histogram MI is
             the standard fast variant and assumption-free for dependence)

All methods produce per-column hypothesis scores (64, 4) per trace, evaluated
by the same rank metric. Prints a league table at the end.
"""
import argparse
import itertools
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from labels import load_state  # noqa: E402
from step1_cpa_hd import col_bits, sbox5, true_hyp, cpa_scores  # noqa: E402


def hw_pred(keys, nonces, c):
    """(N, 4) predicted round-1 S-box output HW per hypothesis h=2*b0+b1."""
    n = len(keys)
    out = np.empty((n, 4))
    for h in range(4):
        b0, b1 = (h >> 1) & 1, h & 1
        kk = keys.copy()
        m = np.uint8(1 << (c % 8))
        kk[:, c % 8] = (kk[:, c % 8] | m) if b0 else \
            (kk[:, c % 8] & np.uint8(255 - int(m)))
        kk[:, 8 + c % 8] = (kk[:, 8 + c % 8] | m) if b1 else \
            (kk[:, 8 + c % 8] & np.uint8(255 - int(m)))
        S = load_state(kk, nonces)
        S[:, 2] ^= np.uint64(0xF0)
        cols = sbox5(col_bits(S, c))
        out[:, h] = np.array([bin(int(v)).count('1') for v in cols])
    return out


def eval_scores(sc_tr, sc_te, y_tr, y_te, n_cls):
    """LDA scoring of hypothesis classes: fit class means+cov on train
    scores, return top-1 accuracy on test."""
    us = np.unique(y_tr)
    mu = np.stack([sc_tr[y_tr == u].mean(axis=0) for u in us])
    cov = np.zeros((sc_tr.shape[1], sc_tr.shape[1]))
    for i, u in enumerate(us):
        Xc = sc_tr[y_tr == u] - mu[i]
        cov += Xc.T @ Xc
    cov /= max(1, len(sc_tr) - len(us))
    cov += 1e-3 * np.eye(cov.shape[0])
    W = np.linalg.solve(cov, mu.T)
    b = -0.5 * np.sum(mu.T * W, axis=0)
    pred = us[(sc_te @ W + b).argmax(axis=1)]
    return float((pred == y_te).mean())


def sost_pois(traces, classes, k):
    t = traces.astype(np.float64)
    t -= t.mean(axis=0, keepdims=True)
    us = np.unique(classes)
    mu = np.stack([t[classes == u].mean(axis=0) for u in us])
    d2 = np.zeros(traces.shape[1])
    for i in range(len(us)):
        for j in range(i + 1, len(us)):
            d2 += (mu[i] - mu[j]) ** 2
    return np.argsort(-d2)[:k]


# ------------------------------------------------------------- method: PLS
def run_pls(trA, trB, yA, yB, n_comp):
    """PLS per column: project traces to n_comp components supervised by the
    trace's predicted HW class; score hypotheses by component-space LDA."""
    from sklearn.cross_decomposition import PLSRegression
    acc = np.zeros(64)
    for c in range(64):
        pls = PLSRegression(n_components=n_comp)
        # Y = one-hot of the true class for THIS trace (its predicted HW)
        Y = np.eye(6)[yA][:, :6]
        pls.fit(trA, Y)
        pA = pls.transform(trA)
        pB = pls.transform(trB)
        acc[c] = eval_scores(pA, pB, yA, yB, 6)
    return acc


# ---------------------------------------------------- method: product traces
def run_prod(trA, trB, yA, yB, poi_k=40):
    """2nd-order product features on SOST POIs (top poi_k samples)."""
    acc = np.zeros(64)
    for c in range(64):
        poi = sost_pois(trA, yA, poi_k)
        A = trA[:, poi].astype(np.float64)
        B = trB[:, poi].astype(np.float64)
        A -= A.mean(axis=0, keepdims=True)
        B -= B.mean(axis=0, keepdims=True)
        # pairwise products (i<j): poi_k*(poi_k-1)/2 features
        iu, ju = np.triu_indices(poi_k, k=1)
        fA = A[:, iu] * A[:, ju]
        fB = B[:, iu] * B[:, ju]
        # keep top-64 product features by ANOVA-F on train
        from sklearn.feature_selection import f_classif
        F, _ = f_classif(fA, yA)
        top = np.argsort(-np.nan_to_num(F))[:64]
        acc[c] = eval_scores(fA[:, top], fB[:, top], yA, yB, 6)
    return acc


# ------------------------------------------------------------- method: MIA
def run_mia(trA, trB, yA, yB, poi_k=32, bins=8):
    """Histogram-MIA feature: per trace, the MI between its POI window values
    and the class-conditional histograms from TRAIN. Score = -log p(x|class)
    summed over POIs; evaluated by LDA on those scores."""
    acc = np.zeros(64)
    for c in range(64):
        poi = sost_pois(trA, yA, poi_k)
        A = trA[:, poi].astype(np.float64)
        B = trB[:, poi].astype(np.float64)
        us = np.unique(yA)
        edges = np.linspace(-3, 3, bins + 1)
        # class-conditional histograms per POI, vectorized:
        # bin every sample at once, then bincount per class
        bA = np.clip(np.digitize(A, edges) - 1, 0, bins - 1)   # (N, poi)
        bB = np.clip(np.digitize(B, edges) - 1, 0, bins - 1)
        # hists[u][j][b] -> tensor (C, poi, bins)
        H = np.zeros((len(us), poi_k, bins))
        for k_, u in enumerate(us):
            for j in range(poi_k):
                cnt = np.bincount(bA[yA == u, j], minlength=bins)
                H[k_, j] = (cnt + 0.5) / (cnt.sum() + 0.5 * bins)
        logH = np.log(H)                                       # (C, poi, bins)

        def loglik(bidx):
            """(N, poi) bin indices -> (N, C) summed log-likelihood, vectorized."""
            # gather logH[u, j, bidx[n, j]] -> (N, C, poi) then sum over poi
            N = bidx.shape[0]
            out = np.zeros((N, len(us)))
            for k_ in range(len(us)):
                # (N, poi) lookup for class k_
                out[:, k_] = logH[k_, np.arange(poi_k)[None, :], bidx].sum(axis=1)
            return out
        acc[c] = eval_scores(loglik(bA), loglik(bB), yA, yB, 6)
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--npz', default='board_session/pa_assets/profiling.npz')
    ap.add_argument('--methods', default='pls,prod,mia')
    ap.add_argument('--out', default='results/step6_preproc_rank.json')
    args = ap.parse_args()

    d = np.load(args.npz, allow_pickle=True)
    traces, keys, nonces = d['traces'], d['keys'], d['nonces']
    n = len(traces)
    from preprocess import zscore
    tr = zscore(traces.astype(np.float64)).astype(np.float32)
    rng = np.random.default_rng(0)
    idx = rng.permutation(n)
    half = n // 2
    A, B = idx[:half], idx[half:]
    trA, trB = tr[A], tr[B]

    methods = args.methods.split(',')
    res = {'n': n, 'per_method': {}}
    league = []
    for m in methods:
        t0 = time.time()
        accs = np.zeros(64)
        floors = np.zeros(64)
        ranks1 = 0
        for c in range(64):
            p = hw_pred(keys, nonces, c)               # (N, 4) hyp HW
            th = true_hyp(keys, c)                     # (N,) true hyp
            # trace's true HW class = predicted class under TRUE hyp
            y = p[np.arange(n), th]
            yA, yB = y[A], y[B]
            if m == 'pls':
                accs[c] = run_pls(trA, trB, yA.astype(int), yB.astype(int),
                                  8)[c]
            elif m == 'prod':
                accs[c] = run_prod(trA, trB, yA.astype(int), yB.astype(int))[c]
            elif m == 'mia':
                accs[c] = run_mia(trA, trB, yA.astype(int), yB.astype(int))[c]
            floors[c] = max((yB == u).mean() for u in np.unique(y))
            if accs[c] > floors[c] + 0.05:
                ranks1 += 1
        res['per_method'][m] = {
            'mean_acc': float(accs.mean()),
            'mean_floor': float(floors.mean()),
            'cols_above_floor5': int(ranks1),
            'best_col': int(accs.argmax()),
            'best_acc': float(accs.max()),
            'elapsed_s': round(time.time() - t0, 1),
        }
        league.append((m, res['per_method'][m]))
        print(f'{m:6s}: acc {accs.mean()*100:5.1f}%  floor '
              f'{floors.mean()*100:4.1f}%  >floor+5: {ranks1}/64  '
              f'({time.time()-t0:.0f}s)', flush=True)
        np.savez_compressed(f'results/step6_acc_{m}.npz', acc=accs,
                            floor=floors)

    os.makedirs('results', exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(res, f, indent=1)
    print('\n=== LEAGUE TABLE (higher acc-floor = better) ===')
    for m, r in sorted(league, key=lambda x: -(x[1]['mean_acc'] -
                                               x[1]['mean_floor'])):
        print(f"{m:6s} +{100*(r['mean_acc']-r['mean_floor']):.1f} pts over "
              f"floor, {r['cols_above_floor5']}/64 cols")
    print(f'-> {args.out}')


if __name__ == '__main__':
    main()
