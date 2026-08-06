#!/usr/bin/env python3
r"""attack.py — guessing-entropy / key-rank evaluation of a trained DL-SCA profile.

Two target classes, matching training/README.md:

  kadd  (default)  intermediate recovery. The model predicts HW(0..8) of one
        byte of state word S[3] after init+KADD. This depends on the FULL
        128-bit key (not factorable per byte), so we score GUESSING ENTROPY
        of the intermediate HW class — how many fresh traces until the true
        intermediate is top-ranked. This is the honest metric for a
        non-factorable target and is what the masked core is expected to
        degrade.

  sbox  key-recovery control. Per column the round-1 S-box output depends on
        only 2 key bits -> 4 key hypotheses, ranked by accumulated log-prob
        over the attack set. On this masked capture the round-1 S-box does
        NOT leak (SNR ~ -23 dB), so this control should stay at chance and
        demonstrates the naive first-order target is defeated.

The attack set is the SAME 20% held-out split train.py used (same npz +
seed), so no trace used for the profile is ever scored.

Usage:
    python3 training/attack.py training/data/main2.npz \
        --model training/models/main2_c3_kadd_mlp.pt --target kadd --column 3
"""
import argparse
import json
import os

import numpy as np
import torch

import labels as lab
from train import CNN, MLP, load


def build_input(traces, arch, window, model):
    n, _ = traces.shape
    traces = traces[:, :window]
    if arch == 'mlp':
        mlp_in = model.net[0].in_features
        if mlp_in > window + 1:                 # product features (raw + 2 lags)
            c = traces - traces.mean(axis=1, keepdims=True)
            cols = [traces]
            for lag in (1, 4):
                cols.append((c[:, lag:] * c[:, :-lag])[:, :window])
            X = np.concatenate(cols, axis=1)
        else:
            X = traces.reshape(n, -1)
        X = torch.tensor(X, dtype=torch.float32)
    elif arch == 'cnn1':
        X = torch.tensor(traces[:, None, :], dtype=torch.float32)
    else:
        c = traces - traces.mean(axis=1, keepdims=True)
        ch = [c[:, None, :],
              (c[:, :-1] * c[:, 1:])[:, None, :],
              (c[:, :-4] * c[:, 4:])[:, None, :]]
        W = min(window, min(x.shape[-1] for x in ch))
        X = np.concatenate([x[..., :W] for x in ch], axis=1)
        X = torch.tensor(X, dtype=torch.float32)
    return X


def ge_curve(logp, true_idx, orderings=20, rng_seed=0):
    """Guessing entropy of `true_idx` over cumulative traces.

    logp: (N, H) per-trace log-probability of each hypothesis.
    true_idx: (N,) index of the true hypothesis.
    Returns mean GE per trace count (1..N).
    """
    rng = np.random.default_rng(rng_seed)
    n = len(logp)
    ge = np.zeros(n)
    for _ in range(orderings):
        perm = rng.permutation(n)
        cum = np.zeros(logp.shape[1])
        for t, i in enumerate(perm):
            cum += logp[i]
            ge[t] += np.count_nonzero(cum > cum[true_idx[i]]) + 1
    return ge / orderings


def first_recovery(ge):
    """First trace count where GE drops to 1 (perfect intermediate/key)."""
    for t, g in enumerate(ge):
        if g <= 1.0 + 1e-9:
            return t + 1
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz', help='training/data/*.npz (same one used for the profile)')
    ap.add_argument('--model', required=True, help='*.pt checkpoint from train.py')
    ap.add_argument('--target', choices=('kadd', 'sbox'), default='kadd')
    ap.add_argument('--column', type=int, default=3,
                    help='S[3] byte (kadd) or round-1 S-box column (sbox)')
    ap.add_argument('--orderings', type=int, default=20,
                    help='random attack-trace orderings averaged for the GE curve')
    ap.add_argument('--seed', type=int, default=None,
                    help='split seed (default: from checkpoint)')
    args = ap.parse_args()

    ckpt = torch.load(args.model, map_location='cpu')
    arch = ckpt['arch']
    window = ckpt['window']
    n_classes = ckpt['n_classes']
    classes = ckpt['classes']
    seed = args.seed if args.seed is not None else ckpt['seed']

    traces, labels_sbox, labels_kadd = load(args.npz)
    n, _ = traces.shape
    if arch == 'cnn2':
        model = CNN(3, n_classes, [8, 16, 32, 32], 128)
    elif arch == 'cnn1':
        model = CNN(1, n_classes, [8, 16, 32], 128)
    else:
        mlp_in = ckpt['state_dict']['net.0.weight'].shape[1]
        model = MLP(mlp_in, ckpt['hidden'], n_classes)
    model.load_state_dict(ckpt['state_dict'])
    model.eval()

    # same held-out split as train.py
    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    ntr = int(0.8 * n)
    attack_idx = idx[ntr:]

    with torch.no_grad():
        Xa = build_input(traces[attack_idx], arch, window, model)
        logp = torch.log_softmax(model(Xa), dim=1).numpy()

    name = os.path.splitext(os.path.basename(args.npz))[0]
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')

    if args.target == 'kadd':
        y = labels_kadd[attack_idx, args.column].astype(np.int64)
        ymap = {c: i for i, c in enumerate(classes)}
        true = np.array([ymap[v] for v in y])
        # per-trace rank of the true intermediate HW class. This is the honest
        # metric for a non-factorable target (each trace carries a different
        # random key, so there is no global hypothesis to accumulate over).
        ranks = (logp > logp[np.arange(len(true)), true][:, None]).sum(axis=1) + 1
        top1 = float((ranks == 1).mean())
        mean_rank = float(ranks.mean())
        print(f'KADD byte {args.column} ({arch}, seed {seed}): '
              f'{len(attack_idx)} attack traces, intermediate rank '
              f'mean {mean_rank:.2f} / chance {logp.shape[1]} '
              f'(median {np.median(ranks):.0f}), top-1 {top1*100:.1f} %')
        out = os.path.join(out_dir,
                           f'{name}_c{args.column}_kadd_{arch}_ge.json')
        with open(out, 'w') as f:
            json.dump({'target': 'kadd', 'column': args.column, 'arch': arch,
                       'n_attack': int(len(attack_idx)),
                       'n_classes': int(logp.shape[1]),
                       'chance_rank': float((logp.shape[1] + 1) / 2),
                       'mean_rank': mean_rank, 'median_rank': float(np.median(ranks)),
                       'top1_acc': top1,
                       'model': args.model}, f, indent=2)
        print(f'  wrote {out}')
        return

    # sbox control: rank 4 two-bit key hypotheses per column
    hyps = lab.all_hypotheses()
    pred = lab.hypothesis_labels(args.column,
                                 np.load(args.npz)['nonces'][attack_idx],
                                 hyps)
    keys = np.load(args.npz)['keys'][attack_idx]
    kbit0 = ((keys[:, args.column // 8] >> (args.column % 8)) & 1) * 1
    kbit1 = ((keys[:, 8 + args.column // 8] >> (args.column % 8)) & 1) * 1
    true = np.array([np.flatnonzero((hyps[:, 0] == a) & (hyps[:, 1] == b))[0]
                     for a, b in zip(kbit0, kbit1)])
    h_logp = np.empty_like(pred, dtype=np.float64)
    for h in range(len(hyps)):
        ymap = {c: i for i, c in enumerate(classes)}
        hc = np.array([ymap[v] for v in pred[:, h]])
        h_logp[:, h] = logp[np.arange(len(hc)), hc]
    ge = ge_curve(h_logp, true, args.orderings, seed)
    rec = first_recovery(ge)
    print(f'S-box col {args.column} key-bits ({arch}, seed {seed}): '
          f'{len(attack_idx)} attack traces, key-bits GE '
          f'{ge[0]:.2f} -> {ge[-1]:.2f} (chance {len(hyps)})')
    print(f'  GE=1 reached after {rec if rec else "never"} traces — '
          f'expected: round-1 S-box does not leak on this masked capture')
    out = os.path.join(out_dir,
                       f'{name}_c{args.column}_sbox_{arch}_ge.json')
    with open(out, 'w') as f:
        json.dump({'target': 'sbox', 'column': args.column, 'arch': arch,
                   'n_attack': int(len(attack_idx)),
                   'chance': float(len(hyps)),
                   'ge_first': float(ge[0]), 'ge_final': float(ge[-1]),
                   'traces_to_ge1': rec, 'model': args.model}, f, indent=2)
    print(f'  wrote {out}')


if __name__ == '__main__':
    main()
