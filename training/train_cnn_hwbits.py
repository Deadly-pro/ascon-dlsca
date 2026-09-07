#!/usr/bin/env python3
r"""train_cnn_hwbits.py — multi-task CNN: 16 HW heads + 128 per-bit binary heads.

The key metric: per-bit held-out accuracy. HW classification is a secondary
output for the paper's record. If per-bit accuracy > 52-55% at M=32, the
attack is alive (M=1024 same-nonce averaging → expected ~80% per-bit).

Architecture:
  Conv trunk (cnn1 from train.py) -> shared features
  -> 16 × 9-class HW heads (cross-entropy)
  -> 16 × 8 binary bit heads (BCE) — each bit in the byte

Usage:
  python3 training/train_cnn_hwbits.py training/data/prof16sc_m32.npz \
    --epochs 40 --out training/models/cnn_hwbits.pt
"""
import argparse, sys, os, time, numpy as np
import torch, torch.nn as nn

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz')
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--window', type=int, default=2000)
    ap.add_argument('--out', default='training/models/cnn_hwbits.pt')
    args = ap.parse_args()

    dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('[+] device:', dev, flush=True)

    d = np.load(args.npz, allow_pickle=True)
    X = d['traces'].astype(np.float32)
    keys = d['keys']
    n = len(X); split = int(0.8 * n)
    X = X[:, :args.window]
    X = (X - X.mean(0)) / (X.std(0) + 1e-12)

    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], dtype=np.int64)
    B = np.zeros((n, 128), dtype=np.int64)
    for b in range(16):
        for j in range(8):
            B[:, b * 8 + j] = (keys[:, b] >> j) & 1

    Xt = torch.tensor(X[:split])[:, None]
    Xv = torch.tensor(X[split:])[:, None]
    Ht = torch.tensor(hw[:split])
    Hv = torch.tensor(hw[split:])
    Bt = torch.tensor(B[:split])
    Bv = torch.tensor(B[split:])

    # ---- CNN architecture ----
    trunk = nn.Sequential(
        nn.Conv1d(1, 16, 11, padding=5), nn.BatchNorm1d(16), nn.ReLU(), nn.MaxPool1d(2),
        nn.Conv1d(16, 32, 7, padding=3), nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(2),
        nn.Conv1d(32, 64, 5, padding=2), nn.BatchNorm1d(64), nn.ReLU(), nn.AdaptiveAvgPool1d(8),
        nn.Flatten(),
    )
    with torch.no_grad():
        flat_dim = trunk(torch.zeros(1, 1, args.window)).shape[1]
    embed = nn.Sequential(nn.Linear(flat_dim, 128), nn.ReLU(), nn.Dropout(0.3))

    hw_heads = nn.ModuleList([nn.Linear(128, 9) for _ in range(16)])
    bit_heads = nn.ModuleList([nn.Linear(128, 8) for _ in range(16)])

    model = nn.ModuleDict({'trunk': trunk, 'embed': embed,
                           'hw_heads': hw_heads, 'bit_heads': bit_heads}).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    hw_loss = nn.CrossEntropyLoss()
    bit_loss = nn.BCEWithLogitsLoss()

    best_bit_acc = 0.0
    best_state = None
    t0 = time.time()

    for ep in range(1, args.epochs + 1):
        model.train()
        perm = torch.randperm(split)
        tot_hw, tot_bit = 0.0, 0.0
        for i in range(0, split, args.batch):
            idx = perm[i:i + args.batch]
            x = Xt[idx].to(dev)
            f = model.embed(model.trunk(x))
            l_hw = sum(hw_loss(head(f), Ht[idx].to(dev)[:, b]) for b, head in enumerate(hw_heads))
            l_bit = sum(bit_loss(head(f), Bt[idx].to(dev)[:, b*8:(b+1)*8].float())
                        for b, head in enumerate(bit_heads))
            loss = l_hw + l_bit
            opt.zero_grad(); loss.backward(); opt.step()
            tot_hw += l_hw.item() * len(idx)
            tot_bit += l_bit.item() * len(idx)
        sched.step()

        # ---- held-out eval ----
        model.eval()
        with torch.no_grad():
            fv = model.embed(model.trunk(Xv.to(dev)))
            # HW accuracy
            hv_pred = torch.stack([head(fv).argmax(1) for head in hw_heads], 1).cpu()
            hw_exact = (hv_pred == Hv).float().mean().item()
            hw_plusminus1 = ((hv_pred - Hv).abs() <= 1).float().mean().item()
            # per-bit accuracy
            bv_pred = torch.cat([(head(fv) > 0).cpu() for head in bit_heads], 1)
            bit_acc = (bv_pred == Bv).float().mean().item()

        if bit_acc > best_bit_acc:
            best_bit_acc = bit_acc
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

        if ep % 5 == 0 or ep == 1:
            print(f'  ep {ep:2d}: HW exact {hw_exact*100:.1f}% ±1 {hw_plusminus1*100:.1f}% '
                  f'| per-bit {bit_acc*100:.2f}% (chance 50%) '
                  f'[{time.time()-t0:.0f}s]', flush=True)

    model.load_state_dict(best_state)
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    torch.save({'state_dict': best_state, 'window': args.window,
                'best_hw_exact': hw_exact, 'best_hw_plusminus1': hw_plusminus1,
                'best_bit_acc': best_bit_acc}, args.out)
    print(f'[+] wrote {args.out}', flush=True)
    print(f'[+] best per-bit held-out: {best_bit_acc*100:.2f}% (need > 52% to be alive)', flush=True)

if __name__ == '__main__':
    main()