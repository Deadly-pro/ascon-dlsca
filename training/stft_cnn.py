#!/usr/bin/env python3
r"""stft_cnn.py — STFT spectrogram + 2D-CNN for per-bit leakage.

Converts each 1D trace to a 2D spectrogram (frequency x time), then trains
a 2D-CNN with per-bit + HW multi-task heads. The hypothesis: time-domain
CNN sees 50% (no signal), but frequency-domain features might separate
the key-load transient (broadband) from the round computation (narrowband).

Usage: .venv/bin/python training/stft_cnn.py training/data/prof16sc_m32.npz
"""
import argparse, sys, os, time, numpy as np
import torch, torch.nn as nn
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))

def traces_to_stft(traces, n_fft=64, hop=16):
    """(N, T) -> (N, F, T_frames) magnitude spectrograms."""
    from scipy.signal import stft
    f, t_seg, Z = stft(traces, fs=1.0, nperseg=n_fft, noverlap=n_fft-hop)
    return np.abs(Z)  # (N, F, T_frames)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz')
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--n-fft', type=int, default=64)
    ap.add_argument('--hop', type=int, default=16)
    ap.add_argument('--out', default='training/models/stft_cnn.pt')
    args = ap.parse_args()
    dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('[+] device:', dev, flush=True)

    d = np.load(args.npz, allow_pickle=True)
    X = d['traces'].astype(np.float32)
    keys = d['keys']
    n = len(X); split = int(0.8 * n)
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], dtype=np.int64)
    B = np.zeros((n, 128), dtype=np.int64)
    for b in range(16):
        for j in range(8): B[:, b*8+j] = (keys[:, b] >> j) & 1

    print('[+] STFT: n_fft=%d, hop=%d' % (args.n_fft, args.hop), flush=True)
    X_stft = traces_to_stft(X, n_fft=args.n_fft, hop=args.hop)
    X_stft = np.log1p(X_stft)  # log-magnitude
    X_stft = (X_stft - X_stft.mean()) / (X_stft.std() + 1e-12)
    print('[+] STFT shape: %s' % str(X_stft.shape), flush=True)

    Xt = torch.tensor(X_stft[:split])[:, None]
    Xv = torch.tensor(X_stft[split:])[:, None]
    Ht = torch.tensor(hw[:split]); Hv = torch.tensor(hw[split:])
    Bt = torch.tensor(B[:split]); Bv = torch.tensor(B[split:])

    F_dim, T_dim = X_stft.shape[1], X_stft.shape[2]
    trunk = nn.Sequential(
        nn.Conv2d(1, 16, (3, 3), padding=1), nn.BatchNorm2d(16), nn.ReLU(),
        nn.MaxPool2d((2, 2)),
        nn.Conv2d(16, 32, (3, 3), padding=1), nn.BatchNorm2d(32), nn.ReLU(),
        nn.MaxPool2d((2, 2)),
        nn.Conv2d(32, 64, (3, 3), padding=1), nn.BatchNorm2d(64), nn.ReLU(),
        nn.AdaptiveAvgPool2d((4, 4)),
        nn.Flatten(),
    )
    with torch.no_grad():
        flat = trunk(torch.zeros(1, 1, F_dim, T_dim)).shape[1]
    embed = nn.Sequential(nn.Linear(flat, 128), nn.ReLU(), nn.Dropout(0.3))
    hw_heads = nn.ModuleList([nn.Linear(128, 9) for _ in range(16)])
    bit_heads = nn.ModuleList([nn.Linear(128, 8) for _ in range(16)])
    model = nn.ModuleDict({'trunk': trunk, 'embed': embed,
                           'hw_heads': hw_heads, 'bit_heads': bit_heads}).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    hw_loss = nn.CrossEntropyLoss()
    bit_loss = nn.BCEWithLogitsLoss()
    best_bit = 0.0; best_state = None; t0 = time.time()

    for ep in range(1, args.epochs + 1):
        model.train()
        perm = torch.randperm(split)
        for i in range(0, split, args.batch):
            idx = perm[i:i + args.batch]
            x = Xt[idx].to(dev)
            f = model['embed'](model['trunk'](x))
            l_hw = sum(hw_loss(h(f), Ht[idx].to(dev)[:, b]) for b, h in enumerate(hw_heads))
            l_bit = sum(bit_loss(h(f), Bt[idx].to(dev)[:, b*8:(b+1)*8].float())
                        for b, h in enumerate(bit_heads))
            loss = l_hw + l_bit
            opt.zero_grad(); loss.backward(); opt.step()
        sched.step()
        model.eval()
        with torch.no_grad():
            fv = model['embed'](model['trunk'](Xv.to(dev)))
            hv_pred = torch.stack([h(fv).argmax(1) for h in hw_heads], 1).cpu()
            hw_exact = (hv_pred == Hv).float().mean().item()
            hw_pm1 = ((hv_pred - Hv).abs() <= 1).float().mean().item()
            bv_pred = torch.cat([(h(fv) > 0).cpu() for h in bit_heads], 1)
            bit_acc = (bv_pred == Bv).float().mean().item()
        if bit_acc > best_bit:
            best_bit = bit_acc
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        if ep % 5 == 0 or ep == 1:
            print(f'  ep {ep:2d}: HW {hw_exact*100:.1f}% ±1 {hw_pm1*100:.1f}% | '
                  f'per-bit {bit_acc*100:.2f}% (chance 50%) [{time.time()-t0:.0f}s]', flush=True)

    torch.save({'state_dict': best_state, 'best_bit_acc': best_bit,
                'stft_n_fft': args.n_fft, 'stft_hop': args.hop}, args.out)
    print(f'[+] wrote {args.out}', flush=True)
    print(f'[+] best per-bit: {best_bit*100:.2f}% (need > 52%)', flush=True)

if __name__ == '__main__':
    main()
