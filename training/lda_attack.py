#!/usr/bin/env python3
r"""Per-column LDA template attack on M-averaged fixed-key traces.

Fits the honest per-column linear template (alpha, class moments from a disjoint
fit subset) on the profiling h5, then scores the M-averaged traces of a single
fixed key, sums per-column hypothesis log-likelihood over all nonces and reports
the recovered 2 key bits per column vs the true key.

Usage:
    .venv/bin/python training/lda_attack.py \
        --profile Dataset/cfgD.h5 --avg Dataset/edge_vs_m.h5 \
        --fit-k 300 [--win0 0 --win 60] [--sum-window full]
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


def fit_template(traces, keys, nonces, n_fit, win):
    """Per-column LDA: alpha, per-class score moments from the fit subset.

    Returns dict with alpha (64, W), class means/variances (64, 6), mu (T,),
    sigma (T,), whitened fit scores for moment estimation.
    """
    T = traces.shape[1]
    ref = traces[:n_fit].mean(axis=0)
    aligned = np.stack([align_trace(t, ref) for t in traces])
    centered = aligned - aligned.mean(1, keepdims=True)
    sigma = aligned.std(0) + 1e-9
    hw = lab.round1_sbox_hw(keys, nonces).astype(np.float64)  # (N,64)
    W = win.stop - win.start if isinstance(win, slice) else win[1] - win[0]
    alphas = np.zeros((64, W))
    m = np.zeros((64, 6))
    v = np.ones((64, 6))
    for c in range(64):
        hwc = hw[:n_fit, c]
        hwc = hwc - hwc.mean()
        f = hwc @ hwc
        if f <= 0:
            alphas[c] = 0
            m[c] = 0
            v[c] = 1.0
            continue
        # noise-whitened projection of the fit window
        Xw = centered[:n_fit, win] / sigma[win]
        alph = (Xw.T @ hwc) / f
        denom = float(np.sqrt((alph ** 2).sum()))
        alph = alph / max(denom, 1e-12)
        sc = Xw @ alph
        alphas[c] = alph
        for hh in range(6):
            sel = hw[:n_fit, c] == hh
            if sel.any():
                m[c, hh] = sc[sel].mean()
                v[c, hh] = max(sc[sel].var(), 1e-3)
    return dict(alpha=alphas, mean=m, var=v, mu=ref, sigma=sigma)


def score_traces(tr_avg, nonces, model, win):
    """Per-trace per-column projection scores (64, n_traces, 4 hyp LL)."""
    alpha, m, v, ref, sigma = (model['alpha'], model['mean'],
                               model['var'], model['mu'], model['sigma'])
    n_tr = len(tr_avg)
    aligned = np.stack([align_trace(t, ref) for t in tr_avg])
    centered = aligned - aligned.mean(1, keepdims=True)
    Xw = centered[:, win] / sigma[win]                    # (n_tr, W)
    sc = Xw @ alpha.T                                     # (n_tr, 64)
    hyps = lab.all_hypotheses()
    ll = np.empty((n_tr, 64, 4))
    for i in range(n_tr):
        for c in range(64):
            pred = lab.hypothesis_labels(c, nonces[i][None], hyps)[0]  # (4,)
            ll[i, c] = (-0.5 * (sc[i, c] - m[c]) ** 2 / v[c]
                        - 0.5 * np.log(2 * np.pi * v[c]))[pred]
    return ll


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--profile', default='Dataset/cfgD.h5')
    ap.add_argument('--avg', default='Dataset/edge_vs_m.h5')
    ap.add_argument('--fit-k', type=int, default=300)
    ap.add_argument('--win0', type=int, default=0)
    ap.add_argument('--win', type=int, default=1200)
    args = ap.parse_args()

    import h5py
    with h5py.File(args.profile, 'r', locking=False) as f:
        tr = f['traces'][:].astype(np.float64)
        kk = f['keys'][:]
        nn = f['nonces'][:]
    with h5py.File(args.avg, 'r', locking=False) as f:
        tavg = f['traces'][:].astype(np.float64)          # (30,64,T)
        navg = f['nonces'][:]
    key = np.frombuffer(
        np.asarray(h5py.File(args.avg, 'r').attrs['key'], dtype=np.uint8),
        np.uint8)

    win = slice(args.win0, args.win0 + args.win)
    model = fit_template(tr, kk, nn, args.fit_k, win)
    Xa = tavg.mean(axis=1)                                 # (30,T) M=64 avg
    ll = score_traces(Xa, navg, model, win)                # (30,64,4)
    L = ll.sum(axis=0)                                     # (64,4)
    hyp = L.argmax(axis=1)

    # truth: 2-bit hypothesis index per column, same convention as edge_vs_m
    bits = np.unpackbits(key, bitorder='little')
    truth = (bits[:64].astype(int) << 1) | bits[64:].astype(int)
    ok = hyp == truth
    print(f'window {args.win0}-{args.win0+args.win}, fit {args.fit_k}, '
          f'{len(Xa)} nonces x M={tavg.shape[1]}')
    print(f'per-column recovery: {int(ok.sum())}/64 columns, '
          f'{int(ok.sum())*2}/128 bits')
    print(f'mean edge/trace/col: {float((ll[np.arange(len(Xa))][:, np.arange(64), truth]).mean() - ll.mean()):+.4f}')
    for c in range(64):
        mark = 'OK' if ok[c] else 'XX'
        print(f'  col {c:2d}: hyp {hyp[c]} truth {truth[c]} {mark} '
              f'(LL true {L[c, truth[c]]:+.2f} best {L[c, hyp[c]]:+.2f})')


if __name__ == '__main__':
    main()