#!/usr/bin/env python3
r"""train.py — train DL-SCA profiles (CNN-1st-order, CNN-2nd-order, MLP).

Takes the npz produced by preprocess.py and trains a profile on a chosen
round-1 S-box output column (label = HW 0..5 of the 5-bit S-box output).

Splits: 80% train / 20% validation, random-key traces. This is ML-style
validation only — the final attack evaluation happens on a separate
fixed-key capture via attack.py (never touched here).

Loss: categorical cross-entropy with class weights (HW classes are imbalanced).
Optimizer: Adam 1e-3 + ReduceLROnPlateau.

Architectures (per training/README.md spec):
    cnn1  baseline first-order:  3 x Conv1D(8/16/32,k11)+BN+ReLU+AvgPool(2),
         Dense(128)+Dropout(0.3), Dense(6). Narrow single-leak window.
    cnn2  second-order-oriented: 4 x Conv1D(8/16/32/32,k11)+BN+ReLU+AvgPool(2),
         Dense(256)+Dropout(0.3), Dense(6). Wider window so the receptive field
         spans both mask-share leak points.
    mlp   cheap baseline: 3-layer MLP on the same input.

Usage:
    python3 training/train.py training/data/main2.npz --column 3 --arch cnn2
"""
import argparse
import json
import os
import time

import numpy as np
import torch
import torch.nn as nn

DEVICE = 'cpu'


def conv_block(n_in, n_out, k):
    return nn.Sequential(
        nn.Conv1d(n_in, n_out, k, padding=k // 2),
        nn.BatchNorm1d(n_out),
        nn.ReLU(),
        nn.AvgPool1d(2),
    )


class CNN(nn.Module):
    def __init__(self, n_in, n_out, blocks, hidden, p=0.3):
        super().__init__()
        layers = []
        prev = n_in
        for b in blocks:
            layers.append(conv_block(prev, b, 11))
            prev = b
        self.features = nn.Sequential(*layers)
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.LazyLinear(hidden),
            nn.ReLU(),
            nn.Dropout(p),
            nn.LazyLinear(n_out),
        )

    def forward(self, x):
        return self.head(self.features(x))


class MLP(nn.Module):
    def __init__(self, n_in, hidden, n_out, p=0.3):
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
    return d['traces'], d['labels_sbox'], d['labels_kadd']


def class_weights(y, n_classes):
    counts = np.bincount(y, minlength=n_classes)
    total = len(y)
    w = total / (n_classes * counts.astype(np.float64))
    w[counts == 0] = 0.0
    return torch.tensor(w, dtype=torch.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz', help='training/data/*.npz from preprocess.py')
    ap.add_argument('--target', choices=('sbox', 'kadd'), default='sbox',
                    help='label source: round-1 S-box column (6 classes) or '
                         'KADD byte HW (9 classes)')
    ap.add_argument('--column', type=int, default=0,
                    help='S-box column (target=sbox) or S[3] byte (target=kadd)')
    ap.add_argument('--arch', choices=('cnn1', 'cnn2', 'mlp'), default='cnn2')
    ap.add_argument('--features', choices=('raw', 'products', 'auto'), default='auto',
                    help='mlp input features: raw traces, or raw + centered '
                         'products (lags 1,4) as in the original 5995-dim MLP. '
                         'auto = products for mlp, raw otherwise')
    ap.add_argument('--window', type=int, default=None,
                    help='crop to first W samples (cnn1 default 400, cnn2/mlp default all)')
    ap.add_argument('--hidden', type=int, nargs='*',
                    help='dense sizes (cnn default 128; mlp default 128 256 256)')
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--batch', type=int, default=256)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    traces, labels_sbox, labels_kadd = load(args.npz)
    labels = labels_kadd if args.target == 'kadd' else labels_sbox
    n, w_full = traces.shape
    if args.window is None:
        args.window = w_full if args.arch in ('cnn2', 'mlp') else min(400, w_full)
    traces = traces[:, :args.window]
    y = labels[:, args.column].astype(np.int64)
    # S-box labels live in 0..5, KADD byte HW in 0..8. Restrict the class
    # space to the target so softmax capacity and the chance baseline are
    # both correct (empty classes get weight 0 within the real space).
    if args.target == 'sbox':
        classes = np.arange(6)
    else:
        classes = np.arange(9)
    n_classes = len(classes)
    name = os.path.splitext(os.path.basename(args.npz))[0]
    hidden = args.hidden or ([128] if args.arch in ('cnn1', 'cnn2') else [128, 256, 256])

    y = y.copy()
    print(f'{name} col{args.column} [{args.arch}] ({args.target}): {n} traces x {args.window} '
          f'window, {n_classes} classes {classes.tolist()}, '
          f'train {int(0.8*n)} / val {n-int(0.8*n)}')
    print(f'  chance accuracy = {100.0/n_classes:.1f} %')

    if args.arch == 'mlp':
        feats = args.features
        if feats == 'auto':
            feats = 'products'
        if feats == 'products':
            c = traces - traces.mean(axis=1, keepdims=True)
            cols = [traces[:, :args.window]]
            for lag in (1, 4):
                cc = (c[:, lag:] * c[:, :-lag])[:, :args.window]
                cols.append(cc)
            X = torch.tensor(np.concatenate(cols, axis=1), dtype=torch.float32)
            model = MLP(X.shape[1], hidden, n_classes)
        else:
            X = torch.tensor(traces.reshape(n, -1), dtype=torch.float32)
            model = MLP(args.window, hidden, n_classes)
        print(f'  mlp input {X.shape[1]} dims ({feats})')
    elif args.arch == 'cnn1':
        X = torch.tensor(traces[:, None, :], dtype=torch.float32)      # (N,1,W)
        model = CNN(1, n_classes, [8, 16, 32], hidden[0])
    else:
        c = traces - traces.mean(axis=1, keepdims=True)                # centered
        ch = [c[:, None, :],
              (c[:, :-1] * c[:, 1:])[:, None, :],                      # lag 1
              (c[:, :-4] * c[:, 4:])[:, None, :]]                      # lag 4
        W = min(args.window, min(ch_.shape[-1] for ch_ in ch))
        X = np.concatenate([ch_[..., :W] for ch_ in ch], axis=1)       # (N,3,W)
        X = torch.tensor(X, dtype=torch.float32)
        model = CNN(3, n_classes, [8, 16, 32, 32], hidden[0])

    Y = torch.tensor(y)
    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(n)
    ntr = int(0.8 * n)
    tr, va = idx[:ntr], idx[ntr:]
    X_tr, Y_tr, X_va, Y_va = X[tr], Y[tr], X[va], Y[va]

    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, factor=0.5,
                                                       patience=5, min_lr=1e-6)
    w = class_weights(y[tr], n_classes)
    lossf = nn.CrossEntropyLoss(weight=w)

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
            lossf(model(X_tr[bi]), Y_tr[bi]).backward()
            opt.step()
        va_acc = acc(X_va, Y_va)
        sched.step(va_acc)
        if va_acc > best_val:
            best_val = va_acc
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        if ep == 1 or ep % 5 == 0 or ep == args.epochs:
            print(f'  ep {ep:3d}  loss {lossf(model(X_tr[:args.batch]), Y_tr[:args.batch]).item():.4f}  '
                  f'val-acc {va_acc*100:.2f} %  lr {opt.param_groups[0]["lr"]:.0e}  [{time.time()-t0:.0f}s]')

    model.load_state_dict(best_state)
    te_acc = acc(X_va, Y_va)
    print(f'  BEST val {best_val*100:.2f} %  (chance {100.0/n_classes:.1f} %)')

    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(out_dir,
                              f'{name}_c{args.column}_{args.target}_{args.arch}.pt')
    torch.save({'arch': args.arch, 'column': args.column, 'target': args.target,
                'window': args.window,
                'n_classes': n_classes, 'classes': classes.tolist(),
                'hidden': hidden, 'state_dict': best_state,
                'best_val_acc': float(best_val), 'seed': args.seed}, model_path)

    res_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(res_dir, exist_ok=True)
    out = os.path.join(res_dir, f'{name}_c{args.column}_{args.target}_{args.arch}.json')
    with open(out, 'w') as f:
        json.dump({'npz': args.npz, 'target': args.target, 'column': args.column,
                   'arch': args.arch,
                   'n': int(n), 'n_classes': int(n_classes),
                   'classes': classes.tolist(), 'window': args.window,
                   'hidden': list(hidden), 'epochs': args.epochs, 'seed': args.seed,
                   'best_val_acc': float(best_val),
                   'chance': float(1.0 / n_classes),
                   'model': model_path,
                   'seconds': float(time.time() - t0)}, f, indent=2)
    print(f'  wrote {out}')
    print(f'  wrote {model_path}')


if __name__ == '__main__':
    main()
