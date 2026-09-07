#!/usr/bin/env python3
r"""hd_cnn.py — whole-state Hamming Distance labels + CNN.

Instead of per-byte HW (which saturates at 8/16), model the round-to-round
Hamming Distance of the FULL 320-bit ASCON state. The full-state HD has
much larger swings (hundreds of bits flip per round) and may produce
stronger aggregate power features.

Labels: ascon_ref.py computes the state after each round. HD between
round i and i+1 across all 320 bits = the leakage model.

Usage: .venv/bin/python training/hd_cnn.py training/data/prof16sc_m32.npz
"""
import argparse, sys, os, time, numpy as np
import torch, torch.nn as nn
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def compute_hd_labels(keys, nonces, n_rounds=12):
    """Hamming Distance of full state between consecutive rounds.
    Returns (N, n_rounds) integer HD values (0-320)."""
    from ascon_ref import _round, _initialize_state
    N = len(keys)
    hd = np.zeros((N, n_rounds), dtype=np.float32)
    for i in range(N):
        # ASCON-128: state is 5 x 64-bit words
        K = int.from_bytes(bytes(keys[i]), 'big')
        N_ = int.from_bytes(bytes(nonces[i]), 'big')
        # IV for ASCON-128
        state = _initialize_state(K, N_)
        for r in range(n_rounds):
            new_state = _round(state)
            hd[i, r] = bin(new_state ^ state).count('1')
            state = new_state
    return hd

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz')
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--window', type=int, default=2000)
    ap.add_argument('--out', default='training/models/hd_cnn.pt')
    args = ap.parse_args()
    dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('[+] device:', dev, flush=True)

    d = np.load(args.npz, allow_pickle=True)
    X = d['traces'].astype(np.float32)
    keys = d['keys']; nonces = d['nonces']
    n = len(X); split = int(0.8 * n)
    X = X[:, :args.window]
    X = (X - X.mean(0)) / (X.std(0) + 1e-12)

    print('[+] computing HD labels for %d traces...' % n, flush=True)
    hd = compute_hd_labels(keys, nonces, n_rounds=12)
    print('[+] HD labels shape: %s' % str(hd.shape), flush=True)
    # distribution
    for r in range(min(6, 12)):
        print('  round %d: mean HD %.1f, std %.1f' % (r, hd[:split, r].mean(), hd[:split, r].std()))
    # correlation of each round HD with each sample (find POIs)
    Xz = (X - X.mean(0)) / (X.std(0) + 1e-12)
    print('\n=== HD per-round correlation peaks ===')
    for r in range(12):
        z = (hd[:split, r] - hd[:split, r].mean()) / (hd[:split, r].std() + 1e-12)
        r_vals = z @ Xz[:split] / split
        pk = int(np.abs(r_vals).argmax())
        r_va = abs(np.corrcoef(Xz[split:, pk], hd[split:, r])[0, 1])
        print('  round %2d: peak @ %4d, train r %.3f, held-out r %.3f' % (
            r, pk, r_vals[pk], r_va))

    # CNN: predict all 12 round HDs simultaneously (regression)
    # + per-bit heads (multi-task: HD teaches trunk the round structure)
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], dtype=np.int64)
    B = np.zeros((n, 128), dtype=np.int64)
    for b in range(16):
        for j in range(8): B[:, b*8+j] = (keys[:, b] >> j) & 1

    Xt = torch.tensor(X[:split])[:, None]
    Xv = torch.tensor(X[split:])[:, None]
    HDt = torch.tensor(hd[:split]); HDv = torch.tensor(hd[split:])
    Ht = torch.tensor(hw[:split]); Hv = torch.tensor(hw[split:])
    Bt = torch.tensor(B[:split]); Bv = torch.tensor(B[split:])

    trunk = nn.Sequential(
        nn.Conv1d(1, 16, 11, padding=5), nn.BatchNorm1d(16), nn.ReLU(), nn.MaxPool1d(2),
        nn.Conv1d(16, 32, 7, padding=3), nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(2),
        nn.Conv1d(32, 64, 5, padding=2), nn.BatchNorm1d(64), nn.ReLU(), nn.AdaptiveAvgPool1d(8),
        nn.Flatten(),
    )
    with torch.no_grad():
        flat = trunk(torch.zeros(1, 1, args.window)).shape[1]
    embed = nn.Sequential(nn.Linear(flat, 128), nn.ReLU(), nn.Dropout(0.3))
    hd_head = nn.Linear(128, 12)  # regression
    hw_heads = nn.ModuleList([nn.Linear(128, 9) for _ in range(16)])
    bit_heads = nn.ModuleList([nn.Linear(128, 8) for _ in range(16)])
    model = nn.ModuleDict({'trunk': trunk, 'embed': embed, 'hd_head': hd_head,
                           'hw_heads': hw_heads, 'bit_heads': bit_heads}).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    hw_loss = nn.CrossEntropyLoss()
    bit_loss = nn.BCEWithLogitsLoss()
    hd_loss = nn.MSELoss()
    best_bit = 0.0; best_hd = 0.0; best_state = None; t0 = time.time()

    for ep in range(1, args.epochs + 1):
        model.train()
        perm = torch.randperm(split)
        for i in range(0, split, args.batch):
            idx = perm[i:i + args.batch]
            x = Xt[idx].to(dev)
            f = model['embed'](model['trunk'](x))
            l_hd = hd_loss(model['hd_head'](f), HDt[idx].to(dev).float())
            l_hw = sum(hw_loss(h(f), Ht[idx].to(dev)[:, b]) for b, h in enumerate(hw_heads))
            l_bit = sum(bit_loss(h(f), Bt[idx].to(dev)[:, b*8:(b+1)*8].float())
                        for b, h in enumerate(bit_heads))
            loss = l_hd + 0.5 * l_hw + 0.5 * l_bit
            opt.zero_grad(); loss.backward(); opt.step()
        sched.step()
        model.eval()
        with torch.no_grad():
            fv = model['embed'](model['trunk'](Xv.to(dev)))
            hd_pred = model['hd_head'](f).cpu()
            hd_r = abs(np.corrcoef(hd_pred[:, 0].numpy(), HDv[:, 0].numpy())[0, 1])
            hv_pred = torch.stack([h(fv).argmax(1) for h in hw_heads], 1).cpu()
            hw_exact = (hv_pred == Hv).float().mean().item()
            bv_pred = torch.cat([(h(fv) > 0).cpu() for h in bit_heads], 1)
            bit_acc = (bv_pred == Bv).float().mean().item()
        if bit_acc > best_bit:
            best_bit = bit_acc
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        if ep % 5 == 0 or ep == 1:
            print(f'  ep {ep:2d}: HD r {hd_r:.3f} | HW {hw_exact*100:.1f}% | '
                  f'per-bit {bit_acc*100:.2f}% [{time.time()-t0:.0f}s]', flush=True)

    torch.save({'state_dict': best_state, 'best_bit_acc': best_bit,
                'best_hd_r': hd_r}, args.out)
    print(f'[+] wrote {args.out}', flush=True)
    print(f'[+] best per-bit: {best_bit*100:.2f}%, HD r: {hd_r:.3f}', flush=True)

if __name__ == '__main__':
    main()
