#!/usr/bin/env python3
r"""Honest LDA per-column recovery on a flat traces/keys/nonces h5.

Fits per-column alpha + class-score moments on a disjoint fit subset, scores
held-out traces, and reports how many of the 64 columns are recovered (argmax
LL over the 4 S-box key-bit hypotheses = 2 key bits each).

The template_edge.py "edge" metric is NOT used: it only checks true-hyp vs the
MEAN of alternatives, which stays positive while argmax recovery is at chance
(that quirk is why every time window looked leaky). Recovery is the only
metric that matters for key cracking. Chance = 16/64 columns (25%).
"""
import argparse
import numpy as np
import h5py
import sys

sys.path.insert(0, 'training')
sys.path.insert(0, '.')
from lda_attack import fit_template, score_traces


def recover(ll, key):
    """ll: (n_tr, 64, 4) hypothesis LLs -> per-column argmax vs truth."""
    bits = np.unpackbits(np.frombuffer(key, np.uint8), bitorder='little')
    truth = (bits[:64].astype(int) << 1) | bits[64:].astype(int)
    hyp = ll.sum(axis=0).argmax(axis=1)
    ok = hyp == truth
    # rank of truth in the summed LL (1 = best)
    L = ll.sum(axis=0)
    ranks = (L > L[np.arange(64), truth][:, None]).sum(axis=1) + 1
    return ok, ranks, truth, hyp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--profile', default='Dataset/cfgD.h5')
    ap.add_argument('--fit-k', type=int, default=300)
    ap.add_argument('--n-score', type=int, default=30,
                    help='held-out traces scored (LL summed over them)')
    args = ap.parse_args()

    with h5py.File(args.profile, 'r', locking=False) as f:
        tr = f['traces'][:].astype(np.float64)
        kk = f['keys'][:]
        nn = f['nonces'][:]

    nf = min(args.fit_k, len(tr) // 2)
    n = min(args.n_score, len(tr) - nf)
    for w0, ww in [(0, 60), (60, 120), (186, 120), (0, 1600)]:
        if w0 + ww > tr.shape[1]:
            continue
        win = slice(w0, w0 + ww)
        model = fit_template(tr, kk, nn, nf, win)
        ll = score_traces(tr[nf:nf + n], nn[nf:nf + n], model, win)
        r = recover(ll, kk[nf])
        print(f'win {w0:>4}-{w0+ww:<4} | {n} held-out traces | '
              f'{int(r[0].sum()):2d}/64 cols (rank1 {int((r[1]==1).sum())}, '
              f'mean rank {r[1].mean():.2f})   [chance: 16/64, rank 2.5]')


if __name__ == '__main__':
    main()