#!/usr/bin/env python3
r"""train_joint_gru.py — joint CNN + GRU belief integrator for parallel key breaking.

Two-stage architecture:
  Stage 1 (CNN): the JointCNN from train_joint.py — shared conv feature
  extractor + 64 per-column HW readout heads. One forward pass gives
  (N, 64, 6) log-probs for all 64 columns.

  Stage 2 (GRU): ONE GRU cell shared by all 64 columns learns the general
  belief-update rule. Per query, per column:
      evidence_c   = logp_c[class(hyp)] for each of the 4 key hypotheses  (4,)
      prev_post    = previous GRU posterior over the 4 hypotheses          (4,)
      alive        = 1 for hypotheses still alive (elimination feedback)   (4,)
      x = concat(evidence, prev_post, alive)  ->  GRUCell  ->  Linear(4)
      post = softmax(logits)  =  updated posterior

  This replaces the hand-coded `log_acc += logp` accumulation in
  adaptive_parallel.py with a LEARNED integrator that can capture
  cross-query dependencies, and the alive mask gives the model explicit
  feedback about which hypotheses have been eliminated.

Training stage 2: simulated attack episodes. For each episode:
  - random key + random column
  - L queries: pick a separating (n0,n1) for the column (all 4 hyps alive),
    query SimBoard (amp=1, target='sbox64' — the physically correct
    aggregate), score the trace with the frozen CNN -> evidence stream.
  The training loop then runs the GRU over the episode with BPTT and CE
  loss vs the true hypothesis at every step, evolving the alive mask from
  the model's own posterior (teacher-forced elimination feedback).

Usage:
  # Stage 1 (CNN) — same as train_joint.py
  .venv/bin/python training/train_joint_gru.py --stage cnn \
      training/data/husky_g25.npz --window 400 --epochs 60 \
      --out training/models/joint_husky_g25.pt

  # Stage 2 (GRU) — needs the CNN checkpoint + the real capture for SimBoard
  .venv/bin/python training/train_joint_gru.py --stage gru \
      --cnn training/models/joint_husky_g25.pt.cnn \
      --npz training/data/husky_g25.npz \
      --sim-h5 Dataset/husky_g25.h5 --epochs 8 --L 12 --batch 32 \
      --out training/models/joint_husky_g25.pt

  # Both
  .venv/bin/python training/train_joint_gru.py \
      training/data/husky_g25.npz --window 400 --epochs 60 \
      --sim-h5 Dataset/husky_g25.h5 --out training/models/joint_husky_g25.pt
"""
import argparse
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import labels as lab
from train import class_weights
from train_joint import JointCNN, N_COLS, N_CLASSES
from preprocess import align_trace, zscore

N_HYPS = 4
GRU_IN = N_HYPS * 3          # evidence + prev_post + alive


class JointGRU(nn.Module):
    """JointCNN feature extractor + one shared GRU belief integrator.

    All 64 columns share the GRU cell (each keeps its own hidden state);
    the cell learns the general rule 'evidence + previous belief -> belief'.
    """

    def __init__(self, cnn=None, hidden=64, blocks=(8, 16, 32)):
        super().__init__()
        self.cnn = cnn if cnn is not None else JointCNN(blocks=blocks)
        self.gru = nn.GRUCell(GRU_IN, hidden)
        self.head = nn.Linear(hidden, N_HYPS)

    def step(self, evidence, prev_post, alive, h=None):
        """One belief update for a batch of (column, query) pairs.

        evidence  (B,4) log-prob of each hyp's predicted class
        prev_post (B,4) previous posterior (zeros on first query)
        alive     (B,4) 0/1 elimination mask
        h         (B,hidden) hidden state or None
        returns (post (B,4), h)
        """
        x = torch.cat([evidence, prev_post, alive], dim=-1)
        if h is None:
            h = torch.zeros(len(x), self.gru.hidden_size)
        h = self.gru(x, h)
        return torch.softmax(self.head(h), dim=-1), h


# ---------------------------------------------------------------- stage 1 ----

def train_cnn(args, npz_path):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    d = np.load(npz_path)
    traces, labels = d['traces'], d['labels_sbox']
    n = len(traces)
    assert labels.shape[1] == N_COLS
    # npz traces are already aligned -> z-scored -> cropped (preprocess.py);
    # only crop to the model window.
    X = traces[:, :args.window].astype(np.float32)
    split = int(n * (1 - args.val_split))
    Xt = torch.tensor(X[:split], dtype=torch.float32)[:, None]
    Xv = torch.tensor(X[split:], dtype=torch.float32)[:, None]
    Yt = torch.tensor(labels[:split], dtype=torch.int64)
    Yv = torch.tensor(labels[split:], dtype=torch.int64)
    print(f'[{time.strftime("%H:%M")}] CNN stage: train {split} '
          f'val {n - split} traces, window {args.window}')

    model = JointCNN()
    weights = [class_weights(Yt[:, c].numpy(), N_CLASSES)
               for c in range(N_COLS)]
    lossf = nn.CrossEntropyLoss(reduction='none')

    def val_acc():
        model.eval()
        with torch.no_grad():
            logits = model(Xv)
            pred = logits.argmax(-1)
            acc = (pred == Yv).float().mean().item()
            per_col = (pred == Yv).float().mean(1)
            cols = (per_col.mean(0) > 1.0 / N_CLASSES).sum().item()
        model.train()
        return acc, cols

    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    best_acc, best_state = 0.0, None
    t0 = time.time()
    for ep in range(1, args.epochs + 1):
        model.train()
        perm = torch.randperm(len(Xt))
        total = 0.0
        for i in range(0, len(perm), args.batch):
            bi = perm[i:i + args.batch]
            logits = model(Xt[bi])
            loss = 0.0
            for c in range(N_COLS):
                per_sample = lossf(logits[:, c], Yt[bi, c])
                w = weights[c][Yt[bi, c]]
                loss = loss + (w * per_sample).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item()
        sched.step()
        acc, cols = val_acc()
        if acc > best_acc:
            best_acc = acc
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        if ep % 5 == 0 or ep == 1:
            print(f'  ep {ep:3d}  loss {total:.3f}  val-acc {acc*100:.2f} %  '
                  f'cols>chance {cols}/64  [{time.time()-t0:.0f}s]')
    print(f'[+] CNN best val-acc {best_acc*100:.2f} % '
          f'(chance {100/N_CLASSES:.1f} %)')
    return best_state


# ---------------------------------------------------------------- stage 2 ----

def _pick_separating(col, rng):
    """Separating (n0,n1) for one column over ALL 4 hyps (training picker)."""
    hyps = lab.all_hypotheses()
    best = None
    ties = []
    for n0 in (0, 1):
        for n1 in (0, 1):
            nn = np.zeros(16, dtype=np.uint8)
            nn[col // 8] |= np.uint8(n0 << (col % 8))
            nn[8 + col // 8] |= np.uint8(n1 << (col % 8))
            pred = lab.hypothesis_labels(col, nn[None], hyps)[0]
            s = {int(v) for v in pred}
            score = (len(s), sum(int(a) != int(b)
                                 for a in s for b in s if a != b))
            if best is None or score > best[0]:
                best = (score, n0, n1)
                ties = [(n0, n1)]
            elif score == best[0]:
                ties.append((n0, n1))
    return ties[int(rng.integers(len(ties)))]


def gen_episodes(cnn, sim, ref, offset, window, n_episodes, L, seed):
    """Evidence streams for GRU training. CNN + SimBoard only, no GRU.

    Returns (ev (N,4), th (N,), col (N,)) with N = n_episodes * L (minus
    flat-trace skips). Evidence = log-prob of each hyp's predicted class.
    """
    hyps = lab.all_hypotheses()
    rng = np.random.default_rng(seed)
    evs, ths, cols = [], [], []
    for ep in range(n_episodes):
        key = rng.bytes(16)
        col = int(rng.integers(N_COLS))
        bits = np.unpackbits(np.frombuffer(key, np.uint8), bitorder='little')
        # hyps = [[0,0],[0,1],[1,0],[1,1]] -> index = (k0 << 1) | k1
        true_hyp = int((bits[col] << 1) | bits[64 + col])
        for t in range(L):
            n0, n1 = _pick_separating(col, rng)
            nonce = bytearray(rng.bytes(16))
            nonce[col // 8] = (nonce[col // 8] & ~(1 << (col % 8))) | \
                (n0 << (col % 8))
            nonce[8 + col // 8] = (nonce[8 + col // 8] & ~(1 << (col % 8))) | \
                (n1 << (col % 8))
            trace, _ct = sim.query(bytes(nonce))
            if trace is None:
                continue
            tr = trace.astype(np.float64)
            if ref is not None:
                tr = align_trace(tr, ref)
            tr = zscore(tr).astype(np.float32)
            tr = tr[offset:offset + window]
            if tr.size < window:
                continue
            with torch.no_grad():
                lp = torch.log_softmax(cnn(torch.tensor(
                    tr[None, None], dtype=torch.float32)), dim=-1)[0, col]
            pred = lab.hypothesis_labels(
                col, np.frombuffer(bytes(nonce), np.uint8)[None], hyps)[0]
            ev = np.full(N_HYPS, -1e3, dtype=np.float32)
            for hh, v in enumerate(pred):
                v = int(v)
                if v in range(N_CLASSES):
                    ev[hh] = lp[v].item()
            evs.append(ev)
            ths.append(true_hyp)
            cols.append(col)
    return (np.array(evs, dtype=np.float32),
            np.array(ths, dtype=np.int64),
            np.array(cols, dtype=np.int64))


def train_gru(args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    cnn_ckpt = torch.load(args.cnn, map_location='cpu')
    cnn = JointCNN()
    cnn.load_state_dict(cnn_ckpt['state_dict'])
    cnn.eval()
    model = JointGRU(cnn=cnn, hidden=args.gru_hidden)
    print(f'[+] GRU stage: {args.n_episodes} episodes x L={args.L}, '
          f'hidden {model.gru.hidden_size}')

    from sim_board import SimBoard
    sim = SimBoard(args.sim_h5, b'\0' * 16, amp=1.0, seed=args.seed,
                   target='sbox64')
    ref = None
    offset = 0
    if args.npz and os.path.exists(args.npz):
        d = np.load(args.npz)
        ref = d.get('ref')
        offset = int(d.get('offset', 0)) if 'offset' in d else 0

    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    lossf = nn.CrossEntropyLoss()
    t0 = time.time()
    for ep_outer in range(args.epochs):
        ev, th, col = gen_episodes(cnn, sim, ref, offset, args.window,
                                   args.n_episodes, args.L,
                                   seed=args.seed * 1000 + ep_outer)
        B = len(ev) // args.L
        ev = ev[:B * args.L].reshape(B, args.L, N_HYPS)
        th = th[:B * args.L].reshape(B, args.L)
        evt = torch.tensor(ev, dtype=torch.float32)
        tht = torch.tensor(th, dtype=torch.int64)
        model.train()
        total = 0.0
        for b0 in range(0, B, args.batch):
            bi = slice(b0, b0 + args.batch)
            h = None
            loss = 0.0
            for t in range(args.L):
                if t == 0:
                    prev_post = torch.zeros(len(evt[bi]), N_HYPS)
                    alive = torch.ones(len(evt[bi]), N_HYPS)
                else:
                    prev_post = post.detach()
                    alive = (post.detach() > 1e-3).float()
                post, h = model.step(evt[bi, t], prev_post, alive, h)
                loss = loss + lossf(post, tht[bi, t])
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item()
        # eval: final-step posterior accuracy over the same episodes
        model.eval()
        with torch.no_grad():
            h = None
            post = None
            for t in range(args.L):
                if t == 0:
                    prev_post = torch.zeros(B, N_HYPS)
                    alive = torch.ones(B, N_HYPS)
                else:
                    prev_post = post
                    alive = (post > 1e-3).float()
                post, h = model.step(evt[:, t], prev_post, alive, h)
            acc = (post.argmax(-1) == tht[:, -1]).float().mean().item()
        print(f'  ep {ep_outer+1:3d}  loss {total:.3f}  '
              f'final-step hyp acc {acc*100:.1f} %  [{time.time()-t0:.0f}s]')

    return {'cnn': model.cnn.state_dict(),
            'gru': model.gru.state_dict(),
            'head': model.head.state_dict()}


# ------------------------------------------------------------------ main ----

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz', nargs='?', default=None,
                    help='training/data/*.npz (stage cnn)')
    ap.add_argument('--stage', choices=('cnn', 'gru', 'both'), default='both')
    ap.add_argument('--cnn', default=None,
                    help='CNN checkpoint *.pt.cnn for --stage gru')
    ap.add_argument('--npz', default=None,
                    help='training/data/*.npz (ref for GRU evidence)')
    ap.add_argument('--sim-h5', default=None,
                    help='real capture for SimBoard (stage gru)')
    ap.add_argument('--window', type=int, default=400)
    ap.add_argument('--epochs', type=int, default=40,
                    help='CNN epochs (stage cnn)')
    ap.add_argument('--batch', type=int, default=128)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--val-split', type=float, default=0.2)
    ap.add_argument('--L', type=int, default=12, help='episode length (gru)')
    ap.add_argument('--n-episodes', type=int, default=64,
                    help='episodes per epoch (gru)')
    ap.add_argument('--gru-hidden', type=int, default=64)
    ap.add_argument('--out', default='training/models/joint_gru.pt')
    args = ap.parse_args()

    if args.stage in ('cnn', 'both'):
        if not args.npz:
            ap.error('stage cnn requires npz')
        best_state = train_cnn(args, args.npz)
        cnn_path = args.out + '.cnn'
        torch.save({'arch': 'joint_cnn1', 'window': args.window,
                    'state_dict': best_state,
                    'best_val_acc': 0.0, 'seed': args.seed,
                    'target': 'sbox', 'joint': True}, cnn_path)
        print(f'[+] wrote CNN-only {cnn_path}')
        if args.stage == 'cnn':
            return
        args.cnn = cnn_path

    if args.stage in ('gru', 'both'):
        if not args.cnn or not args.sim_h5:
            ap.error('stage gru requires --cnn and --sim-h5')
        state = train_gru(args)
        merged = {'arch': 'joint_gru', 'window': args.window,
                  'state_dict': state['cnn'], 'gru_state_dict': state['gru'],
                  'head_state_dict': state['head'],
                  'gru_hidden': args.gru_hidden,
                  'best_val_acc': 0.0, 'seed': args.seed,
                  'target': 'sbox', 'joint': True}
        torch.save(merged, args.out)
        print(f'[+] wrote {args.out} (joint CNN+GRU)')


if __name__ == '__main__':
    main()
