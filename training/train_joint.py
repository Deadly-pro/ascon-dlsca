#!/usr/bin/env python3
r"""train_joint.py — one CNN that predicts ALL 64 S-box columns at once.

The power trace is an aggregate of every column's switching activity:
    trace(t) ~= sum_c alpha_c(t) * HW_c + noise
Training 64 separate per-column models makes each one treat the other 63
columns as noise. A joint model shares the feature extractor (the common
leakage shape) and only learns a per-column readout head, which is far more
data-efficient and typically 1.5-2x more accurate per column.

Loss = sum over columns of class-weighted cross-entropy (empty classes 0).

Output checkpoint format (consumed by adaptive.py via Profile):
    {arch, column, window, n_classes, classes, hidden, state_dict,
     best_val_acc, seed, target, joint: True}
For a joint model, `column` is the FIRST column and `classes` is shared;
attack code reads logits for the requested column by slicing the head.

Usage:
    .venv/bin/python training/train_joint.py \
        training/data/main_unmasked_merged.npz \
        --window 400 --epochs 40 --out training/models/joint_unmasked.pt
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

from train import CNN, class_weights, load


N_COLS = 64
N_CLASSES = 6          # HW 0..5 of a 5-bit S-box column


class JointCNN(nn.Module):
    """Shared conv stack + 64 per-column HW readout heads."""

    def __init__(self, blocks=(8, 16, 32), hidden=128, p=0.3):
        super().__init__()
        layers = []
        prev = 1
        for b in blocks:
            layers.append(nn.Conv1d(prev, b, 11, padding=5))
            layers.append(nn.BatchNorm1d(b))
            layers.append(nn.ReLU())
            layers.append(nn.MaxPool1d(2))
            prev = b
        self.features = nn.Sequential(*layers)
        self.embed = nn.Sequential(
            nn.Flatten(),
            nn.LazyLinear(hidden),
            nn.ReLU(),
            nn.Dropout(p),
        )
        self.heads = nn.ModuleList(
            [nn.Linear(hidden, N_CLASSES) for _ in range(N_COLS)])

    def forward(self, x):
        e = self.embed(self.features(x))
        # (N, 64, 6) logits for every column
        return torch.stack([h(e) for h in self.heads], dim=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz', help='training/data/*.npz (traces + labels_sbox)')
    ap.add_argument('--window', type=int, default=400,
                    help='crop to first W samples after align+zscore')
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--batch', type=int, default=128)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', default='training/models/joint_unmasked.pt')
    ap.add_argument('--val-split', type=float, default=0.2)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    d = np.load(args.npz)
    traces, labels = d['traces'], d['labels_sbox']
    n = len(traces)
    assert labels.shape[1] == N_COLS, labels.shape

    # preprocess identical to the profiling pipeline: the npz traces are
    # already aligned -> z-scored -> cropped (see preprocess.py), so use
    # them directly; only crop to the model window.
    X = traces[:, :args.window].astype(np.float32)

    split = int(n * (1 - args.val_split))
    Xt = torch.tensor(X[:split], dtype=torch.float32)[:, None]  # (N,1,W)
    Xv = torch.tensor(X[split:], dtype=torch.float32)[:, None]
    Yt = torch.tensor(labels[:split], dtype=torch.int64)        # (N,64)
    Yv = torch.tensor(labels[split:], dtype=torch.int64)
    print(f'[{time.strftime("%H:%M")}] train {split} val {n - split} '
          f'traces, window {args.window}')

    model = JointCNN()
    weights = [class_weights(Yt[:, c].numpy(), N_CLASSES)
               for c in range(N_COLS)]
    lossf = nn.CrossEntropyLoss(reduction='none')

    def val_acc():
        model.eval()
        with torch.no_grad():
            logits = model(Xv)                      # (V, 64, 6)
            pred = logits.argmax(-1)
            per_col = (pred == Yv).float().mean(1)  # (V,)
            acc = (pred == Yv).float().mean().item()
            cols_above_chance = (per_col.mean(0) > (1.0 / N_CLASSES)).sum().item()
        model.train()
        return acc, int(cols_above_chance)

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
            logits = model(Xt[bi])                  # (B, 64, 6)
            loss = 0.0
            for c in range(N_COLS):
                per_sample = lossf(logits[:, c], Yt[bi, c])  # (B,)
                w = weights[c][Yt[bi, c]]                    # (B,)
                loss = loss + (w * per_sample).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
            total += loss.item()
        sched.step()
        acc, cols_above = val_acc()
        if acc > best_acc:
            best_acc = acc
            best_state = {k: v.clone()
                          for k, v in model.state_dict().items()}
        if ep % 5 == 0 or ep == 1:
            print(f'  ep {ep:3d}  loss {total:.3f}  val-acc {acc*100:.2f} %  '
                  f'cols>chance {cols_above}/64  [{time.time()-t0:.0f}s]')

    ckpt = {
        'arch': 'joint_cnn1', 'column': 0, 'window': args.window,
        'n_classes': N_CLASSES,
        'classes': list(range(N_CLASSES)),
        'hidden': [128], 'state_dict': best_state,
        'best_val_acc': best_acc, 'seed': args.seed,
        'target': 'sbox', 'joint': True,
    }
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    torch.save(ckpt, args.out)
    print(f'[+] wrote {args.out} (val-acc {best_acc*100:.2f} %, '
          f'chance {100/N_CLASSES:.1f} %)')


if __name__ == '__main__':
    main()