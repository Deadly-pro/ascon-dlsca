#!/usr/bin/env python3
r"""template_edge.py — measure the hypothesis-vs-hypothesis evidence edge of
the linear template attack (LDA) on held-out real traces, vs the CNN edge.

Leakage model: trace(t) ~ mu + alpha_c * (HW_c - E[HW_c]) + N(0, sigma^2).
For each column c the template attack scores a trace by the standardized
projection onto alpha_c, then maps each hypothesis's predicted HW class to a
Gaussian log-likelihood. The reported edge is E[LL(true hyp) - mean(LL(alt))].

If this is >> the CNN edge (+0.003 nats), the linear statistic is the
one-shot path at this SNR — no board time needed to decide.

Usage:
    OMP_NUM_THREADS=12 .venv/bin/python training/template_edge.py \
        --h5 /tmp/split_simfit.h5  # or any flat traces/keys/nonces h5
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))
sys.path.insert(0, ROOT)

import labels as lab
from sim_board import _fit_from_h5


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h5', required=True)
    ap.add_argument('--n', type=int, default=1000, help='traces to score')
    ap.add_argument('--column', type=int, default=None,
                    help='score a single column (default: all 64)')
    ap.add_argument('--fit-k', type=int, default=300)
    args = ap.parse_args()

    import h5py
    with h5py.File(args.h5, 'r', locking=False) as f:
        traces = f['traces'][:args.n].astype(np.float64)
        keys = f['keys'][:args.n]
        nonces = f['nonces'][:args.n]
    T = traces.shape[1]
    print(f'[+] {len(traces)} traces x {T} samples')

    # 1. fit the per-column linear template on a DISJOINT subset (fit-k)
    n_fit = min(args.fit_k, len(traces))
    fit = _fit_from_h5(args.h5, 0, n_fit, target='sbox64')
    alphas = fit['alpha']            # (64, T)
    mu = fit['mu']                   # (T,)
    sigma = fit['sigma']             # (T,) residual std per sample
    print(f'[+] alpha energy per col: '
          f'{[f"{np.abs(a).max():.3f}" for a in alphas[:5]]}...')

    # 2. align + center held-out traces, project onto each column template
    ref = mu
    aligned = np.stack([lab.align_trace(t, ref) for t in traces]) if hasattr(
        lab, 'align_trace') else None
    if aligned is None:
        from preprocess import align_trace
        aligned = np.stack([align_trace(t, ref) for t in traces])
    # center each trace by its own mean (removes DC)
    centered = aligned - aligned.mean(1, keepdims=True)

    # standardized projection per column
    denom = np.sqrt(np.sum((alphas / sigma) ** 2, axis=1))  # (64,)
    scores = (centered / sigma) @ alphas.T                  # (N,64)
    scores /= denom[None, :]

    # 3. per-column class model: for each column, the score distribution per
    # HW class (Gaussian, from the same fit subset)
    hw_fit = lab.round1_sbox_hw(keys[:n_fit], nonces[:n_fit])  # (fit,64)
    sc_fit = (np.stack([align_trace(t, mu) for t in traces[:n_fit]]) \
              - traces[:n_fit].mean(1, keepdims=True)) / sigma
    sc_fit = (sc_fit @ alphas.T) / denom[None, :]             # (fit,64)

    cols = range(64) if args.column is None else [args.column]
    hyps = lab.all_hypotheses()
    bits = np.unpackbits(np.frombuffer(keys.tobytes(), np.uint8),
                         bitorder='little').reshape(-1, 128)
    truth = (bits[:, :64] << 1) | bits[:, 64:]              # (N,64)
    nb = np.frombuffer(nonces.tobytes(), np.uint8).reshape(-1, 16)

    edges = []
    for c in cols:
        # class means/variances from the FIT subset (honest)
        m = np.array([sc_fit[:n_fit, c][hw_fit[:n_fit, c] == v].mean()
                      if (hw_fit[:n_fit, c] == v).any() else 0.0
                      for v in range(6)])
        v = np.array([sc_fit[:n_fit, c][hw_fit[:n_fit, c] == v].var()
                      if (hw_fit[:n_fit, c] == v).sum() > 1 else 1.0
                      for v in range(6)])
        v = np.maximum(v, 1e-3)
        pred = lab.hypothesis_labels(c, nb[n_fit:], hyps)    # (N-fit,4)
        edge_col, cnt = 0.0, 0
        for i in range(n_fit, len(traces)):                  # held-out only
            s = scores[i, c]
            ll = -0.5 * (s - m) ** 2 / v - 0.5 * np.log(2 * np.pi * v)
            llh = ll[pred[i - n_fit]]                        # (4,)
            t = int(truth[i, c])
            if np.ptp(pred[i - n_fit]) == 0:
                continue
            edge_col += llh[t] - llh[np.arange(4) != t].mean()
            cnt += 1
        edges.append(edge_col / max(cnt, 1))
    edges = np.array(edges)
    print(f'\n[+] template (LDA) per-trace hypothesis edge over {len(cols)} '
          f'cols: mean {edges.mean():+.4f} nats  '
          f'(held-out: fit {n_fit}, scored {len(traces) - n_fit})')
    print(f'[+] cols with edge>0: {int((edges>0).sum())}/{len(cols)}')
    print(f'[+] edge range: [{edges.min():+.4f}, {edges.max():+.4f}]')
    print(f'\n    CNN reference edge: +0.003 nats (64 cols)')
    print(f'    => LDA/CNN ratio: {edges.mean()/0.003:.1f}x')


if __name__ == '__main__':
    main()
