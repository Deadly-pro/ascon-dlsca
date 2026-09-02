#!/usr/bin/env python3
r"""train_byte_hw_cnn.py — GPU CNN for per-byte HW regression on M-averaged
captures. Replaces the linear template: the CNN reads the full window and
learns the multi-sample load-transient shape per byte (16 heads, shared
conv trunk). Held-out HW RMSE is the gate (linear template: 1.37).

Usage:
    python3 training/train_byte_hw_cnn.py training/data/avg32.npz \
        --out training/models/byte_hw_cnn.pt --epochs 60
"""
import argparse
import os
import sys
import time

import numpy as np
import torch
import torch.nn as nn

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'training'))

from byte_hw_attack import regress_drift, byte_hw_labels, find_peaks  # noqa


class ByteHWNet(nn.Module):
    """Shared conv trunk -> 16 per-byte HW regression heads."""

    def __init__(self, window=640, hidden=128):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(1, 16, 11, padding=5), nn.BatchNorm1d(16), nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 32, 7, padding=3), nn.BatchNorm1d(32), nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, 5, padding=2), nn.BatchNorm1d(64), nn.ReLU(),
            nn.AdaptiveAvgPool1d(8),
        )
        self.embed = nn.Sequential(nn.Flatten(), nn.LazyLinear(hidden),
                                   nn.ReLU(), nn.Dropout(0.3))
        self.heads = nn.ModuleList([nn.Linear(hidden, 1) for _ in range(16)])

    def forward(self, x):                      # x: (B, 1, W)
        e = self.embed(self.features(x))
        return torch.cat([h(e) for h in self.heads], dim=1)  # (B, 16)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz')
    ap.add_argument('--out', default='training/models/byte_hw_cnn.pt')
    ap.add_argument('--window', type=int, default=640)
    ap.add_argument('--epochs', type=int, default=60)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--lr', type=float, default=1e-3)
    args = ap.parse_args()

    dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'[+] device: {dev}')

    d = np.load(args.npz, allow_pickle=True)
    tr = d['traces'].astype(np.float64)
    ky = d['keys']
    n = len(tr)
    labels = byte_hw_labels(ky).astype(np.float32)
    Xres, _ = regress_drift(tr, return_model=True)
    X = Xres[:, :args.window].astype(np.float32)
    sp = int(0.75 * n)
    Xt = torch.tensor(X[:sp])[:, None]
    Xv = torch.tensor(X[sp:])[:, None]
    Yt = torch.tensor(labels[:sp])
    Yv = torch.tensor(labels[sp:])
    # per-byte normalization of targets (HW 0..8 -> zero-mean unit-var)
    mu = Yt.mean(0, keepdim=True)
    sd = Yt.std(0, keepdim=True).clamp_min(1e-3)
    Yt_n = (Yt - mu) / sd

    model = ByteHWNet(window=args.window).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    lossf = nn.MSELoss()
    best = 1e9
    best_state = None
    t0 = time.time()
    for ep in range(1, args.epochs + 1):
        model.train()
        perm = torch.randperm(sp)
        tot = 0.0
        for i in range(0, sp, args.batch):
            bi = perm[i:i + args.batch]
            x = Xt[bi].to(dev)
            y = Yt_n[bi].to(dev)
            out = model(x)
            loss = lossf(out, y)
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += loss.item() * len(bi)
        sched.step()
        model.eval()
        with torch.no_grad():
            pv = model(Xv.to(dev)).cpu()
        pred = pv * sd + mu
        rmse = torch.sqrt(((pred - Yv) ** 2).mean(0))
        m = rmse.mean().item()
        if m < best:
            best = m
            best_state = {k: v.detach().cpu().clone()
                          for k, v in model.state_dict().items()}
        if ep % 5 == 0 or ep == 1:
            print(f'  ep {ep:3d}  loss {tot/sp:.4f}  val HW-RMSE {m:.3f} '
                  f'(linear ref 1.37)  [{time.time()-t0:.0f}s]')
    model.load_state_dict(best_state)
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    torch.save({'state_dict': best_state, 'window': args.window,
                'mu': mu, 'sd': sd, 'val_rmse': best}, args.out)
    print(f'[+] wrote {args.out} (best val HW-RMSE {best:.3f})')
    print(f'[+] at M=100 live captures: expected RMSE '
          f'~{best/np.sqrt(100/32):.2f} (class-ID needs <0.5)')


if __name__ == '__main__':
    main()