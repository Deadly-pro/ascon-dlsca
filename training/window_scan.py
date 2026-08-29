#!/usr/bin/env python3
r"""Sliding-window LDA hypothesis edge scan on a flat traces/keys/nonces h5.

Finds where (if anywhere) the round-1 S-box leakage lives in time. Fits the
per-column linear template on disjoint fit-k traces, scores held-out traces,
reports mean per-trace edge over 64 columns per window. Pure CPU.
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import labels as lab
from preprocess import align_trace


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--h5', required=True)
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--fit-k', type=int, default=300)
    ap.add_argument('--win', type=int, default=60)
    ap.add_argument('--step', type=int, default=40)
    ap.add_argument('--cols', type=int, default=64)
    args = ap.parse_args()

    import h5py
    with h5py.File(args.h5, 'r', locking=False) as f:
        traces = f['traces'][:args.n].astype(np.float64)
        keys = f['keys'][:args.n]
        nonces = f['nonces'][:args.n]
    T = traces.shape[1]
    n_fit = min(args.fit_k, len(traces))

    # global alignment to the mean (preprocess order)
    ref = traces.mean(axis=0)
    aligned = np.stack([align_trace(t, ref) for t in traces])
    centered = aligned - aligned.mean(1, keepdims=True)

    bits = np.unpackbits(np.frombuffer(keys.tobytes(), np.uint8),
                         bitorder='little').reshape(-1, 128)
    truth = (bits[:, :64] << 1) | bits[:, 64:]            # (N,64)
    hyps = lab.all_hypotheses()
    hw = lab.round1_sbox_hw(keys, nonces)                 # (N,64)
    nb = nonces

    cols = range(args.cols)
    print(f'{"win":>6} {"edge":>9} {">0":>4} {"best":>7} '
          f'{"worst":>7}  {"pos":>5}')
    for w0 in range(0, T - args.win + 1, args.step):
        w = slice(w0, w0 + args.win)
        X = centered[:, w]
        edges = np.zeros(args.cols)
        for c in cols:
            hwc = hw[:n_fit, c].astype(np.float64)
            hwc = hwc - hwc.mean()
            f = hwc @ hwc
            if f <= 0:
                continue
            alph = (X[:n_fit].T @ hwc) / f               # (W,)
            a2 = (alph ** 2).sum()
            sig2 = float(X[:n_fit].var(axis=0).sum())
            if a2 <= 0 or sig2 <= 0:
                continue
            s = (X[n_fit:] @ alph) / np.sqrt(a2 * sig2)  # held-out scores
            m = np.zeros(6)
            v = np.ones(6)
            for vv in range(6):
                sel = hw[n_fit:, c] == vv
                if sel.any():
                    m[vv] = s[sel].mean()
                    v[vv] = max(s[sel].var(), 1e-3)
            pred = lab.hypothesis_labels(c, nb[n_fit:], hyps)
            tru = truth[n_fit:, c]
            edge = 0.0
            cnt = 0
            for i in range(len(s)):
                if np.ptp(pred[i]) == 0:
                    continue
                ll = -0.5 * (s[i] - m) ** 2 / v
                llh = ll[pred[i]]
                t = int(tru[i])
                edge += llh[t] - llh[np.arange(4) != t].mean()
                cnt += 1
            edges[c] = edge / max(cnt, 1)
        print(f'{w0:>5}-{w0+args.win:<5} {edges.mean():>+9.4f} '
              f'{int((edges>0).sum()):>4} {edges.max():>+7.4f} '
              f'{edges.min():>+7.4f}')

    print(f'\nT={T}, fit {n_fit}, held-out {len(traces)-n_fit}, '
          f'win {args.win} step {args.step}')


if __name__ == '__main__':
    main()