#!/usr/bin/env python3
r"""train.py — train a small MLP to classify HW(S[3] byte) from power traces.

Takes the npz produced by preprocess.py and, for a chosen target byte,
trains a profile on 70 % of traces, validates on 15 %, and tests on the
remaining 15 %. Because every trace in these captures has a unique random key,
accuracy meaningfully above chance (1/9 = 11.1 %) on the test split shows the
model generalizes key-dependent leakage to unseen keys — the prerequisite for a
real DL-SCA key-recovery attack.

Usage:
    python3 training/train.py training/data/main2.npz --byte 0
    python3 training/train.py training/data/main2.npz --byte 3 --hidden 128 256

Metrics printed per epoch and saved to training/results/<name>_b<byte>.json
"""
import argparse
import json
import os
import time

import numpy as np
import torch
import torch.nn as nn

DEVICE = 'cpu'


class MLP(nn.Module):
    def __init__(self, n_in, hidden, n_out, p=0.2):
        super().__init__()
        layers = []
        prev = n_in
        for h in hidden:
            layers += [nn.Linear(prev, h), nn.ReLU(), nn.Dropout(p)]
            prev = h
        layers += [nn.Linear(prev, n_out)]
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def load(npz):
    d = np.load(npz)
    return d['features'], d['labels'], d['keys'], d['nonces']


def split_by_trace(n, seed=0):
    rng = np.random.default_rng(seed)
    idx = rng.permutation(n)
    a, b = int(0.70 * n), int(0.85 * n)
    return idx[:a], idx[a:b], idx[b:]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz', help='training/data/*.npz from preprocess.py')
    ap.add_argument('--byte', type=int, default=0, help='S[3] byte to attack')
    ap.add_argument('--hidden', type=int, nargs='*', default=(128, 256, 256))
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--batch', type=int, default=512)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    features, labels, _, _ = load(args.npz)
    n, f_in = features.shape
    y = labels[:, args.byte].astype(np.int64)
    n_classes = len(np.unique(y))
    name = os.path.splitext(os.path.basename(args.npz))[0]

    X = torch.tensor(features, dtype=torch.float32)
    Y = torch.tensor(y)
    tr, va, te = split_by_trace(n, args.seed)
    X_tr, Y_tr = X[tr], Y[tr]
    X_va, Y_va = X[va], Y[va]
    X_te, Y_te = X[te], Y[te]
    print(f'{name}: {n} traces, byte {args.byte}, {n_classes} HW classes, '
          f'{f_in} features, train {len(tr)} / val {len(va)} / test {len(te)}')
    print(f'  chance accuracy = {100.0 / n_classes:.1f} %')

    model = MLP(f_in, args.hidden, n_classes)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    lossf = nn.CrossEntropyLoss()

    def acc(x_, y_):
        with torch.no_grad():
            return (model(x_).argmax(1) == y_).float().mean().item()

    best_val, best_state = 0.0, None
    t0 = time.time()
    for ep in range(1, args.epochs + 1):
        model.train()
        perm = torch.randperm(len(X_tr))
        for i in range(0, len(perm), args.batch):
            bi = perm[i:i + args.batch]
            opt.zero_grad()
            loss = lossf(model(X_tr[bi]), Y_tr[bi])
            loss.backward()
            opt.step()
        va_acc = acc(X_va, Y_va)
        if va_acc > best_val:
            best_val = va_acc
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        if ep == 1 or ep % 5 == 0 or ep == args.epochs:
            print(f'  ep {ep:3d}  loss {loss.item():.4f}  '
                  f'val-acc {va_acc*100:.2f} %  [{time.time()-t0:.0f}s]')

    model.load_state_dict(best_state)
    te_acc = acc(X_te, Y_te)
    print(f'  BEST val {best_val*100:.2f} %   TEST {te_acc*100:.2f} % '
          f'(chance {100.0/n_classes:.1f} %)')

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f'{name}_b{args.byte}.json')
    with open(out, 'w') as f:
        json.dump({'npz': args.npz, 'byte': args.byte, 'n': int(n),
                   'n_classes': int(n_classes), 'features': int(f_in),
                   'hidden': list(args.hidden), 'epochs': args.epochs,
                   'seed': args.seed, 'best_val_acc': float(best_val),
                   'test_acc': float(te_acc),
                   'chance': float(1.0 / n_classes),
                   'seconds': float(time.time() - t0)}, f, indent=2)
    print(f'  wrote {out}')


if __name__ == '__main__':
    main()
