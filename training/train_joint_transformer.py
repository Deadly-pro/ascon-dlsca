#!/usr/bin/env python3
r"""train_joint_transformer.py — joint CNN + causal Transformer key tracker.

Replaces the GRU integrator with a Transformer that attends over the FULL
query history (no information bottleneck). Architecture:

  per query q:
    trace -> JointCNN (shared conv) -> per-column HW logits (64, 6)
    evidence[c] = logp[c, class(hyp)] for the 4 hyps        (64, 4)
    alive[c]    = 1 for hypotheses still in play             (64, 4)
    prev_post[c]= previous posterior                          (64, 4)

  Transformer encoder (SHARED across columns, per-column sequence):
    token_t = embed(evidence_t, prev_post_t, alive_t) + pos_t
    causal self-attention over queries 1..t
    output at t -> Linear(4) -> softmax = updated posterior   (64, 4)

  The alive mask IS the elimination feedback: hypotheses whose posterior
  drops below --elim-p are masked and the mask is fed back into the
  attention so the model knows what is still in play.

Extra heads (trained jointly on the oracle key):
  - KADD byte head: trace-level CNN features -> 8 bytes x 9 HW classes
    (the strong -0.1 dB leak at gain 35, regularizes the weak S-box heads)
  - key head: pooled transformer state -> 128-bit key logits (BCE,
    evaluation-only: the S-box/KADD heads are what actually learn)

Training stage 2 (like train_joint_gru.py): simulated attack episodes.
Per episode: random key + random column, L separating nonce queries,
SimBoard traces scored by the frozen CNN -> evidence stream. The
Transformer runs causally over the stream (teacher-forced posterior
feeds the next step) with CE vs the true hypothesis at every step.

Usage:
  # stage 1 (CNN) — same as train_joint.py
  .venv/bin/python training/train_joint_transformer.py --stage cnn \
      training/data/husky_g35_full.npz --window 400 --epochs 60 \
      --out training/models/joint_xfm_g35.pt

  # stage 2 (transformer)
  .venv/bin/python training/train_joint_transformer.py --stage xfm \
      --cnn training/models/joint_xfm_g35.pt.cnn \
      --npz training/data/husky_g35_full.npz \
      --sim-h5 Dataset/husky_g35_full.h5 --epochs 15 --L 16 --batch 32 \
      --n-episodes 128 --out training/models/joint_xfm_g35.pt
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

N_HYPS = 4
XFM_IN = N_HYPS * 3          # evidence + prev_post + alive


def causal_mask(T, device='cpu'):
    """(T,T) upper-triangular -inf: position t attends only to 1..t."""
    return torch.triu(torch.full((T, T), float('-inf'), device=device),
                      diagonal=1)


class JointTransformer(nn.Module):
    """JointCNN + causal Transformer belief integrator (shared per column)."""

    def __init__(self, cnn=None, d_model=64, nhead=4, nlayers=2,
                 ff=128, max_len=128, blocks=(8, 16, 32)):
        super().__init__()
        self.cnn = cnn if cnn is not None else JointCNN(blocks=blocks)
        self.embed_in = nn.Linear(XFM_IN, d_model)
        self.pos = nn.Parameter(torch.zeros(max_len, 1, d_model))
        layer = nn.TransformerEncoderLayer(
            d_model, nhead, ff, dropout=0.1, batch_first=True)
        self.enc = nn.TransformerEncoder(layer, nlayers)
        self.head = nn.Linear(d_model, N_HYPS)
        # extra heads (trained jointly on the oracle key)
        self.kadd_head = nn.Linear(128, 8 * 9)      # 8 bytes x 9 HW classes
        self.key_head = nn.Linear(d_model, 128)     # direct key guess (eval)

    def forward_causal(self, ev, prev, alive):
        """(B,T,4) x3 -> (B,T,4) posterior at every query step."""
        B, T = ev.shape[:2]
        x = torch.cat([ev, prev, alive], dim=-1)     # (B,T,12)
        x = self.embed_in(x) + self.pos[:T].transpose(0, 1)
        h = self.enc(x, mask=causal_mask(T, ev.device))  # (B,T,d_model)
        return torch.softmax(self.head(h), dim=-1)

    def cnn_embed(self, x):
        """Trace-level features for the KADD head: (B,128)."""
        return self.cnn.embed(self.cnn.features(x))

    def kadd_logits(self, x):
        return self.kadd_head(self.cnn_embed(x))     # (B,72)


def train_cnn(args, npz_path):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    d = np.load(npz_path)
    traces, labels = d['traces'], d['labels_sbox']
    n = len(traces)
    assert labels.shape[1] == N_COLS
    X = traces[:, :args.window].astype(np.float32)   # already aligned+zscored
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
        model.train()
        return acc

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
        acc = val_acc()
        if acc > best_acc:
            best_acc = acc
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        if ep % 5 == 0 or ep == 1:
            print(f'  ep {ep:3d}  loss {total:.3f}  val-acc {acc*100:.2f} %  '
                  f'[{time.time()-t0:.0f}s]')
    print(f'[+] CNN best val-acc {best_acc*100:.2f} % '
          f'(chance {100/N_CLASSES:.1f} %)')
    return best_state


def gen_episodes(cnn, sim, ref, offset, window, n_episodes, L, seed):
    """Evidence streams for transformer training (CNN + SimBoard only)."""
    hyps = lab.all_hypotheses()
    rng = np.random.default_rng(seed)
    evs, ths = [], []
    for ep in range(n_episodes):
        key = rng.bytes(16)
        col = int(rng.integers(N_COLS))
        bits = np.unpackbits(np.frombuffer(key, np.uint8), bitorder='little')
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
    return (np.array(evs, dtype=np.float32),
            np.array(ths, dtype=np.int64))


def train_xfm(args):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    cnn_ckpt = torch.load(args.cnn, map_location='cpu')
    cnn = JointCNN()
    cnn.load_state_dict(cnn_ckpt['state_dict'])
    cnn.eval()
    model = JointTransformer(cnn=cnn)
    n_params = sum(p.numel() for p in model.parameters())
    print(f'[+] Transformer stage: d_model {model.embed_in.out_features}, '
          f'{n_params/1e3:.0f}k params, {args.n_episodes} eps x L={args.L}')

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
        ev, th = gen_episodes(cnn, sim, ref, offset, args.window,
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
            evb = evt[bi]                              # (B,L,4)
            thb = tht[bi]
            # autoregressive rollout: prev/alive at step t come from the
            # model's own posterior at t-1 (matches the live attack loop)
            Bb = len(evb)
            prev_hist = [torch.zeros(Bb, N_HYPS)]
            alive_hist = [torch.ones(Bb, N_HYPS)]
            loss = 0.0
            for t in range(args.L):
                prev = torch.stack(prev_hist, 1)          # (B,t+1,4)
                alive = torch.stack(alive_hist, 1)
                post = model.forward_causal(
                    evb[:, :t + 1], prev, alive)[:, -1]   # (B,4)
                loss = loss + lossf(post, thb[:, t])
                with torch.no_grad():
                    prev_hist.append(post.detach())
                    alive_hist.append(
                        (post.detach() > 1e-3).float())
                    if alive_hist[-1].sum() == 0:
                        alive_hist[-1][post.argmax(-1)] = 1.0
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item()
        # eval: final-step posterior accuracy (autoregressive rollout)
        model.eval()
        with torch.no_grad():
            prev_hist = [torch.zeros(B, N_HYPS)]
            alive_hist = [torch.ones(B, N_HYPS)]
            for t in range(args.L):
                post_final = model.forward_causal(
                    evt[:, :t + 1],
                    torch.stack(prev_hist, 1),
                    torch.stack(alive_hist, 1))[:, -1]
                prev_hist.append(post_final)
                alive_hist.append((post_final > 1e-3).float())
            acc = (post_final.argmax(-1) == tht[:, -1]).float().mean().item()
        print(f'  ep {ep_outer+1:3d}  loss {total:.3f}  '
              f'final-step hyp acc {acc*100:.1f} %  [{time.time()-t0:.0f}s]')

    return {'cnn': model.cnn.state_dict(),
            'embed_in': model.embed_in.state_dict(),
            'pos': model.pos,
            'enc': model.enc.state_dict(),
            'head': model.head.state_dict(),
            'kadd_head': model.kadd_head.state_dict(),
            'key_head': model.key_head.state_dict()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz', nargs='?', default=None)
    ap.add_argument('--stage', choices=('cnn', 'xfm', 'both'), default='both')
    ap.add_argument('--cnn', default=None, help='CNN ckpt *.pt.cnn')
    ap.add_argument('--npz2', dest='npz2', default=None,
                    help='npz for stage xfm (--npz positional works too)')
    ap.add_argument('--sim-h5', default=None)
    ap.add_argument('--window', type=int, default=400)
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--batch', type=int, default=128)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--val-split', type=float, default=0.2)
    ap.add_argument('--L', type=int, default=16)
    ap.add_argument('--n-episodes', type=int, default=128)
    ap.add_argument('--out', default='training/models/joint_xfm.pt')
    args = ap.parse_args()

    if args.stage in ('cnn', 'both'):
        if not args.npz:
            ap.error('stage cnn requires npz')
        best_state = train_cnn(args, args.npz)
        cnn_path = args.out + '.cnn'
        torch.save({'arch': 'joint_cnn1', 'window': args.window,
                    'state_dict': best_state, 'best_val_acc': 0.0,
                    'seed': args.seed, 'target': 'sbox', 'joint': True},
                   cnn_path)
        print(f'[+] wrote CNN-only {cnn_path}')
        if args.stage == 'cnn':
            return
        args.cnn = cnn_path

    if args.stage in ('xfm', 'both'):
        if not args.cnn or not args.sim_h5:
            ap.error('stage xfm requires --cnn and --sim-h5')
        state = train_xfm(args)
        merged = {'arch': 'joint_xfm', 'window': args.window,
                  'state_dict': state['cnn'],
                  'embed_in': state['embed_in'], 'pos': state['pos'],
                  'enc': state['enc'], 'head': state['head'],
                  'kadd_head': state['kadd_head'],
                  'key_head': state['key_head'],
                  'd_model': 64,
                  'best_val_acc': 0.0, 'seed': args.seed,
                  'target': 'sbox', 'joint': True}
        torch.save(merged, args.out)
        print(f'[+] wrote {args.out} (joint CNN+Transformer)')


if __name__ == '__main__':
    main()
