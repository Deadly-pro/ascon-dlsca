#!/usr/bin/env python3
r"""adaptive.py — closed-loop adaptive chosen-plaintext key recovery (ACPPA).

Attacks ONE round-1 S-box column at a time (the only factorable target on this
masked core: exactly 2 key bits, 4 hypotheses). Uses a trained per-column HW
profile from train.py and drives the query->classify->posterior->select loop.

Selection heuristic (simple, no Bayesian experimental design):
  column c's S-box input bits that depend on the nonce are exactly
  nonce[0:8] bit c and nonce[8:16] bit c. Enumerate all 4 (n0,n1) combos,
  compute the 4 predicted HW classes (one per key hypothesis) for each, and
  pick the combo that SEPARATES the hypotheses most (most distinct classes).
  Random nonces mostly map all 4 hypotheses to the same class -> zero info;
  a separating nonce makes a single trace discriminate the key bits.

Offline validation (--validate, no board needed):
  Uses the held-out 20% split (same as train.py) of an existing random-key npz.
  Per trace: score the 4 hypotheses with the profile, compute the rank of the
  TRUE hypothesis, and the nonce's separation. Checks the premise of the whole
  approach: do high-separation nonces correlate with rank-1 true hypothesis,
  and are random nonces mostly uninformative?

Live attack (--attack, needs the board):
  Calls live_query.capture(nonce, key, ad) per query, feeds the trace through
  the profile, accumulates log-probabilities over hypotheses, converges when
  the top hypothesis's posterior clears a threshold for N consecutive queries,
  then VERIFIES the recovered key against ciphertext/tag.

Usage:
    # offline premise check (no hardware)
    python3 training/adaptive.py --validate \
        --npz training/data/main2.npz \
        --model training/models/main2_c1_sbox_cnn2.pt --column 1
    # live closed loop (board required)
    python3 training/adaptive.py --attack \
        --model training/models/main2_c1_sbox_cnn2.pt --column 1 \
        --key 000102030405060708090a0b0c0d0e0f --max-queries 500
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import torch

import labels as lab
from train import CNN, MLP, load
from attack import build_input
from preprocess import align_trace, zscore


class Profile:
    """A trained per-column profile: model + reconstruction of its features."""

    def __init__(self, model_path, npz_path=None):
        ckpt = torch.load(model_path, map_location='cpu')
        self.arch = ckpt['arch']
        self.column = ckpt['column']
        self.window = ckpt['window']
        self.classes = list(ckpt['classes'])
        self.ymap = {c: i for i, c in enumerate(self.classes)}
        self.support = set(self.classes)
        n_out = len(self.classes)
        if self.arch == 'cnn2':
            self.model = CNN(3, n_out, [8, 16, 32, 32], 128)
        elif self.arch == 'cnn1':
            self.model = CNN(1, n_out, [8, 16, 32], 128)
        else:
            mlp_in = ckpt['state_dict']['net.0.weight'].shape[1]
            self.model = MLP(mlp_in, ckpt['hidden'], n_out)
        self.model.load_state_dict(ckpt['state_dict'])
        self.model.eval()
        self.ref = None
        if npz_path:
            d = np.load(npz_path, allow_pickle=True)
            self.ref = d.get('ref')
            if self.ref is None:
                self.ref = d['traces'].mean(axis=0).astype(np.float32)

    def log_probs(self, traces):
        """(N,W) -> (N, n_classes) log-softmax over the model's class support."""
        with torch.no_grad():
            X = build_input(traces, self.arch, self.window, self.model)
            return torch.log_softmax(self.model(X), dim=1).numpy()

    def preprocess(self, trace):
        """One raw capture -> aligned+z-scored window (identical to profiling)."""
        t = trace[:self.window]
        if self.ref is not None:
            t = align_trace(t, self.ref[:self.window])
        t = zscore(t).astype(np.float32)
        return t


def separation(nonce16, column, model_support):
    """#distinct predicted HW classes across the 4 hypotheses for this nonce."""
    hyps = lab.all_hypotheses()
    pred = lab.hypothesis_labels(column, np.array([nonce16]), hyps)[0]
    return len({int(v) for v in pred if int(v) in model_support})


def pick_separating_nonce(column, model_support, rng=None):
    """Choose the 2 nonce bits (of column c) that separate the hypotheses best.

    Returns a 16-byte nonce. Other nonce bytes are random (they affect the
    trace but not this column's label). Ties broken by wider class spread.
    """
    if rng is None:
        rng = np.random.default_rng()
    hyps = lab.all_hypotheses()
    best = None
    for n0 in (0, 1):
        for n1 in (0, 1):
            nonce = np.zeros(16, dtype=np.uint8)
            nonce[column // 8] |= np.uint8(n0 << (column % 8))
            nonce[8 + column // 8] |= np.uint8(n1 << (column % 8))
            pred = lab.hypothesis_labels(column, nonce[None], hyps)[0]
            s = {int(v) for v in pred if int(v) in model_support}
            score = (len(s), sum(int(a) != int(b)
                                 for a in s for b in s if a != b))
            if best is None or score > best[0]:
                best = (score, nonce)
    nonce = best[1].copy()
    rest = rng.integers(0, 256, size=16, dtype=np.uint8)
    mask = np.zeros(16, dtype=np.uint8)
    mask[column // 8] |= 1 << (column % 8)
    mask[8 + column // 8] |= 1 << (column % 8)
    nonce = np.where(mask != 0, nonce, rest)
    return nonce


def score_trace(logp_row, nonce16, column, classes):
    """Per-hypothesis log-score for one trace: (4,) with -inf for impossible."""
    hyps = lab.all_hypotheses()
    pred = lab.hypothesis_labels(column, np.array([nonce16]), hyps)[0]
    scores = np.full(len(hyps), -np.inf)
    for h, v in enumerate(pred):
        v = int(v)
        if v in classes:
            scores[h] = logp_row[classes.index(v)]
    return scores


def best_nonce_bits(column):
    """(n0, n1) bit setting that separates the 4 hypotheses the most."""
    hyps = lab.all_hypotheses()
    best = None
    for n0 in (0, 1):
        for n1 in (0, 1):
            nonce = np.zeros(16, dtype=np.uint8)
            nonce[column // 8] |= np.uint8(n0 << (column % 8))
            nonce[8 + column // 8] |= np.uint8(n1 << (column % 8))
            pred = lab.hypothesis_labels(column, nonce[None], hyps)[0]
            s = len({int(v) for v in pred})
            if best is None or s > best[0]:
                best = (s, (n0, n1), pred)
    return best


def validate_offline(args):
    d = np.load(args.npz)
    traces, labels = d['traces'], d['labels_sbox']
    nonces = d['nonces']
    keys = d['keys']
    n = len(traces)
    col = args.column
    prof = Profile(args.model, args.npz)

    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(n)
    ntr = int(0.8 * n)
    attack = idx[ntr:]
    print(f'validate col {col}: {len(attack)} held-out attack traces '
          f'({prof.arch}, support {prof.classes})')

    logp = prof.log_probs(traces[attack])
    kbit0 = ((keys[attack, col // 8] >> (col % 8)) & 1) * 1
    kbit1 = ((keys[attack, 8 + col // 8] >> (col % 8)) & 1) * 1
    hyps = lab.all_hypotheses()
    true = np.array([np.flatnonzero((hyps[:, 0] == a) & (hyps[:, 1] == b))[0]
                     for a, b in zip(kbit0, kbit1)])

    ranks = np.empty(len(attack), dtype=int)      # strict: count strictly-better
    ranks_tie = np.empty(len(attack), dtype=int)  # conservative: ties count against
    seps = np.empty(len(attack), dtype=int)
    for i, ti in enumerate(attack):
        sc = score_trace(logp[i], nonces[ti], col, prof.classes)
        ranks[i] = np.count_nonzero(sc > sc[true[i]]) + 1
        ranks_tie[i] = np.count_nonzero(sc >= sc[true[i]])
        seps[i] = separation(nonces[ti], col, prof.support)

    mean_rank = ranks_tie.mean()
    chance_rank = (len(hyps) + 1) / 2
    top1 = (ranks == 1).mean()
    top1_conservative = (ranks_tie == 1).mean()
    print(f'  per-trace true-hyp rank: mean {mean_rank:.2f} '
          f'(chance {chance_rank}), top-1 {top1*100:.1f} % '
          f'(ties-count-against {top1_conservative*100:.1f} %)')

    # model's own HW-class accuracy on the same traces (the raw signal)
    model_top1 = 0
    for i, ti in enumerate(attack):
        pred = lab.hypothesis_labels(col, nonces[ti][None], hyps)[0]
        true_cls = int(pred[true[i]])
        if true_cls in prof.classes and np.argmax(logp[i]) == prof.classes.index(true_cls):
            model_top1 += 1
    print(f'  model HW-class top-1 accuracy: {model_top1/len(attack)*100:.1f} % '
          f'(chance {100/len(prof.classes):.1f} %)')

    # collision structure: does the true hyp share its class with another hyp?
    n_collide = 0
    for i, ti in enumerate(attack):
        pred = lab.hypothesis_labels(col, nonces[ti][None], hyps)[0]
        v = int(pred[true[i]])
        others = [int(pred[h]) for h in range(4) if h != true[i]]
        if v in others:
            n_collide += 1
    print(f'  true hyp collides with another hyp (same class): '
          f'{n_collide/len(attack)*100:.1f} % of traces')

    # per-class reliability: how often is each class the model's argmax
    # and how often is it the TRUE class?
    print(f'  nonce separation distribution (random nonces):')
    for s in range(1, 5):
        sub = ranks_tie[seps == s]
        if len(sub):
            print(f'    sep={s}: {len(sub):4d} traces, mean rank {sub.mean():.2f}, '
                  f'top-1 {(sub == 1).mean()*100:.1f} %')
        else:
            print(f'    sep={s}: none')

    hi = seps >= 3
    if hi.sum():
        print(f'  high-sep (>=3) nonces: {hi.sum()} traces, '
              f'mean rank {ranks_tie[hi].mean():.2f}, '
              f'top-1 {(ranks_tie[hi] == 1).mean()*100:.1f} % '
              f'vs all {top1_conservative*100:.1f} %')

    # achievable separation for this column (adaptive selection's ceiling)
    _, (n0, n1), pred = best_nonce_bits(col)
    print(f'  best achievable separation: {len({int(v) for v in pred})} '
          f'(n0={n0}, n1={n1}, pred {[int(v) for v in pred]})')

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(out, exist_ok=True)
    name = os.path.splitext(os.path.basename(args.npz))[0]
    path = os.path.join(out, f'{name}_c{col}_sbox_{prof.arch}_adaptive_validate.json')
    with open(path, 'w') as f:
        json.dump({'column': col, 'arch': prof.arch, 'n_attack': int(len(attack)),
                   'support': prof.classes, 'mean_rank': float(mean_rank),
                   'chance_rank': float(chance_rank), 'top1': float(top1),
                   'top1_conservative': float(top1_conservative),
                   'n_queries_rank1': int((ranks == 1).sum()),
                   'separation_dist': {int(s): int((seps == s).sum())
                                       for s in range(1, 5)}}, f, indent=2)
    print(f'  wrote {path}')


def live_attack(args):
    try:
        import live_query
    except ImportError as e:
        sys.exit(f'live_query not importable (board session required): {e}')
    prof = Profile(args.model, args.npz)
    col = args.column
    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('--key must be 16 bytes hex')
    lq = live_query.LiveQuery(args.bitstream, key)

    hyps = lab.all_hypotheses()
    log_acc = np.full(len(hyps), 0.0)
    stable = 0
    rng = np.random.default_rng(0)
    print(f'[+] adaptive attack col {col}, 4 hyps, profile {prof.arch} '
          f'(support {prof.classes})')
    t0 = time.time()
    n_captured = 0
    for q in range(1, args.max_queries + 1):
        nonce = pick_separating_nonce(col, prof.support, rng)
        trace, ct = lq.query(nonce)
        if trace is None:            # trigger timeout — retry same nonce
            continue
        n_captured += 1
        trace = prof.preprocess(trace)
        logp_row = prof.log_probs(trace[None])[0]
        sc = score_trace(logp_row, nonce, col, prof.classes)
        log_acc += np.where(np.isfinite(sc), sc, -1e3)
        post = np.exp(log_acc - log_acc.max())
        post /= post.sum()
        top = int(post.argmax())
        stable = stable + 1 if post[top] > args.converge_p else 0
        if n_captured <= 5 or n_captured % 25 == 0 or stable >= args.stable_n:
            print(f'  q {n_captured:4d}  top hyp {top}  post {post[top]:.3f}  '
                  f'[{time.time()-t0:.0f}s]')
        if stable >= args.stable_n:
            k0, k1 = int(hyps[top, 0]), int(hyps[top, 1])
            print(f'[+] converged at query {n_captured}: hyp {top} '
                  f'(key bits k[{col}%8]={k0}, k[8+col%8]={k1})')
            print(f'[+] NOTE: 2-bit column recovery is not verifiable alone; '
                  f'assemble all 64 columns then check via lq.verify_key()')
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'results', f'adaptive_c{col}_q{n_captured}.json')
            with open(path, 'w') as f:
                json.dump({'column': col, 'queries': n_captured, 'hyp': int(top),
                           'k0': k0, 'k1': k1,
                           'posterior': float(post[top]),
                           'seconds': float(time.time() - t0)}, f, indent=2)
            lq.close()
            return
    print(f'[!] no convergence after {n_captured} queries — '
          f'top hyp {int(log_acc.argmax())}, posterior {post.max():.3f}')
    lq.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--validate', action='store_true',
                    help='offline premise check on held-out npz (no board)')
    ap.add_argument('--attack', action='store_true',
                    help='live closed loop (board required)')
    ap.add_argument('--npz', default='training/data/main2.npz')
    ap.add_argument('--model', required=True)
    ap.add_argument('--column', type=int, default=1)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--key', default=None, help='16-byte target key hex (attack)')
    ap.add_argument('--max-queries', type=int, default=500)
    ap.add_argument('--converge-p', type=float, default=0.99)
    ap.add_argument('--stable-n', type=int, default=5)
    ap.add_argument('--bitstream',
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         '..', 'vivado_ascon', 'ascon_cw305_top.bit'))
    args = ap.parse_args()

    if args.validate:
        validate_offline(args)
    elif args.attack:
        if not args.key:
            sys.exit('--attack requires --key <16-byte hex>')
        live_attack(args)
    else:
        ap.error('choose --validate or --attack')


if __name__ == '__main__':
    main()
