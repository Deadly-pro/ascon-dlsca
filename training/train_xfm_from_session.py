#!/usr/bin/env python3
r"""train_xfm_from_session.py — build a full joint XFM checkpoint from
recorded live-session HDF5 files (real board traces, oracle-labelled).

Pipeline:
  1. Load every ep_* group from one or more session H5s
     (traces/nonces/cts + key attr, written by live_loop_transformer.py).
  2. Derive S-box HW + KADD labels from each episode's key via labels.py.
  3. Preprocess exactly like the live loop: align to mean-ref -> zscore ->
     crop [offset : offset+window]; offset/window chosen from the ref's
     active region if not given.
  4. Supervised-train the JointCNN (64 S-box heads + KADD byte head).
  5. Stage-2: replay each episode's evidence stream through the causal
     Transformer toward the true hypothesis (same loss as the live
     fine_tune), so --integrator xfm works immediately.
  6. Save in the FULL checkpoint format XfmEngine loads.

Usage:
    .venv/bin/python training/train_xfm_from_session.py \
        --h5 Dataset/live_xfm_session_20260824_163112.h5 \
        --out training/models/joint_xfm_unmasked_s1.pt \
        --epochs 30 --stage2-epochs 3
"""
import argparse
import glob
import os
import sys

import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import labels as lab
from train_joint import JointCNN, N_COLS, N_CLASSES
from train_joint_transformer import JointTransformer, N_HYPS
from preprocess import align_trace, zscore


def load_sessions(paths):
    """-> list of episodes: dict(key=bytes, nonces=[bytes], traces=[f8])"""
    import h5py
    eps = []
    for path in paths:
        f = h5py.File(path, 'r', locking=False)
        # flat format (traces/keys/nonces at top level, e.g. /tmp/split_*.h5)
        if 'traces' in f and 'nonces' in f:
            keys = f['keys'][:]
            nonces = f['nonces'][:]
            # treat each 16-byte key as a separate pseudo-episode so the
            # per-key grouping semantics hold
            for i in range(len(keys)):
                eps.append({
                    'key': bytes(keys[i].tobytes()),
                    'nonces': [bytes(nonces[i].tobytes())],
                    'traces': [f['traces'][i].astype(np.float64)],
                })
            f.close()
            continue
        for name in sorted(f.keys()):
            g = f[name]
            if 'traces' not in g:
                continue
            eps.append({
                'key': bytes(np.asarray(g.attrs['key']).tobytes()),
                'nonces': [bytes(n) for n in g['nonces'][:]],
                'traces': [t.astype(np.float64) for t in g['traces'][:]],
            })
        f.close()
    return eps


def pick_window(eps, window):
    """Choose crop offset from the peak-activity region of the mean |dev|."""
    n = min(len(t) for t in eps[0]['traces'])
    acc = None
    for ep in eps[:50]:
        for t in ep['traces'][:20]:
            a = np.abs(t[:n] - np.median(t[:n]))
            acc = a if acc is None else acc + a
    smooth = np.convolve(acc / acc.max(), np.ones(64) / 64, mode='same')
    peak = int(np.argmax(smooth))
    return max(0, peak - window // 2), window


def preprocess_all(eps, ref, offset, window):
    X = []
    for ep in eps:
        for tr in ep['traces']:
            t = tr.astype(np.float64)
            if ref is not None:
                t = align_trace(t, ref)
            t = zscore(t).astype(np.float32)
            if t.size < offset + window:
                continue
            X.append(t[offset:offset + window])
    return np.array(X, dtype=np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h5', required=True, nargs='+',
                    help='session h5 paths/globs')
    ap.add_argument('--out', default='training/models/joint_xfm_unmasked_s1.pt')
    ap.add_argument('--epochs', type=int, default=30)
    ap.add_argument('--stage2-epochs', type=int, default=3)
    ap.add_argument('--window', type=int, default=256)
    ap.add_argument('--offset', type=int, default=-1,
                    help='-1 = auto from activity peak')
    ap.add_argument('--batch', type=int, default=128)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--val-frac', type=float, default=0.15)
    ap.add_argument('--val-h5', default=None,
                    help='key-disjoint h5 used ONLY for validation (traces/'
                         'keys/nonces flat format); overrides --val-frac')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--cnn-checkpoint', default=None,
                    help='pretrained joint CNN .cnn file: skip stage 1')
    ap.add_argument('--device', default=None)
    args = ap.parse_args()

    device = torch.device(args.device or
                          ('cuda' if torch.cuda.is_available() else 'cpu'))
    torch.manual_seed(args.seed)

    paths = sorted(p for pat in args.h5 for p in glob.glob(pat))
    print(f'[+] sessions: {paths}')
    eps = load_sessions(paths)
    n_tr = sum(len(e['traces']) for e in eps)
    assert n_tr > 0, 'no traces found'
    print(f'[+] {len(eps)} episodes, {n_tr} traces')

    # ---- preprocessing ----
    ref = None
    all_len = min(min(len(t) for t in e['traces']) for e in eps)
    ref = np.mean([t[:all_len] for e in eps[:40] for t in e['traces'][:10]],
                  axis=0).astype(np.float64)
    if args.offset < 0:
        offset, window = pick_window(eps, args.window)
    else:
        offset, window = args.offset, args.window
    print(f'[+] crop offset {offset}, window {window}')
    X = preprocess_all(eps, ref, offset, window)
    print(f'[+] dataset: {X.shape}')

    # ---- labels ----
    keys, nonces = [], []
    for e in eps:
        keys += [e['key']] * len(e['nonces'])
        nonces += e['nonces']
    kb = np.stack([np.frombuffer(k, np.uint8) for k in keys])
    nb = np.stack([np.frombuffer(n, np.uint8) for n in nonces])
    Y = lab.round1_sbox_hw(kb, nb)          # (N,64) s-box HW
    K = lab.kadd_words_hw(kb, nb)           # (N,8) kadd HW

    # ---- split ----
    if args.val_h5:
        import h5py
        with h5py.File(args.val_h5, 'r', locking=False) as vf:
            vtr = vf['traces'][:].astype(np.float64)
            vkeys = vf['keys'][:]
            vnonces = vf['nonces'][:]
        Xv = preprocess_all([{'traces': vtr}], ref, offset, window)
        Yv = lab.round1_sbox_hw(vkeys, vnonces)
        Kv = lab.kadd_words_hw(vkeys, vnonces)
        Xv = torch.tensor(Xv); Yv = torch.tensor(Yv, dtype=torch.int64)
        Kv = torch.tensor(Kv, dtype=torch.int64)
        idx = np.random.default_rng(args.seed).permutation(len(X))
        tr = idx
        va = None
        print(f'[+] train {len(tr)} / val {len(Xv)} (key-disjoint: '
              f'{args.val_h5})')
    else:
        idx = np.random.default_rng(args.seed).permutation(len(X))
        n_val = max(1, int(len(X) * args.val_frac))
        va, tr = idx[:n_val], idx[n_val:]
        Xv = Yv = Kv = None
        print(f'[+] train {len(tr)} / val {len(va)}')

    X = torch.tensor(X); Y = torch.tensor(Y, dtype=torch.int64)
    K = torch.tensor(K, dtype=torch.int64)
    dev = device
    cnn = JointCNN().to(dev)
    opt = torch.optim.Adam(cnn.parameters(), lr=args.lr)
    lossf = torch.nn.CrossEntropyLoss()

    # class-weight empty classes out of the loss (per gotcha)
    def col_loss(logits, yt, cols):
        l = 0.0
        for c in cols:
            l = l + lossf(logits[:, c], yt[:, c])
        return l

    best = 0.0
    if args.cnn_checkpoint:
        ck = torch.load(args.cnn_checkpoint, map_location='cpu')
        cnn.load_state_dict(ck['state_dict'])
        cnn.eval()
        with torch.no_grad():
            vx = (Xv if Xv is not None else X[va]).to(dev)[:, None]
            vy = (Yv if Yv is not None else Y[va])
            logits = cnn(vx)
            acc = (logits.argmax(-1).cpu() == vy).float().mean().item()
        print(f'[+] loaded CNN from {args.cnn_checkpoint} '
              f'(val top1 {acc*100:.1f}%) -- skipping stage 1')
        best = acc
    for ep_i in range(1, args.epochs + 1 if not args.cnn_checkpoint else 0):
        cnn.train()
        perm = tr[torch.randperm(len(tr))]
        tot = 0.0
        for i in range(0, len(perm), args.batch):
            b = perm[i:i + args.batch]
            xb, yb, kb_ = X[b].to(dev)[:, None], Y[b].to(dev), K[b].to(dev)
            opt.zero_grad()
            logits = cnn(xb)
            loss = col_loss(logits, yb, range(N_COLS))
            loss.backward()
            opt.step()
            tot += float(loss.detach())
        # val (key-disjoint if --val-h5 given)
        cnn.eval()
        with torch.no_grad():
            vx = (Xv if Xv is not None else X[va]).to(dev)[:, None]
            vy = (Yv if Yv is not None else Y[va])
            logits = cnn(vx)
            pred = logits.argmax(-1).cpu()          # (V,64)
            acc = (pred == vy).float().mean().item()
        print(f'  epoch {ep_i:3d}  loss {tot:.1f}  val top1 {acc*100:.1f}% '
              f'(chance ~{100/N_CLASSES:.1f}%)', flush=True)
        if acc > best:
            best = acc
            torch.save({'arch': 'joint_cnn', 'window': window,
                        'state_dict': cnn.state_dict(),
                        'best_val_acc': best, 'seed': args.seed},
                       args.out + '.cnn')

    # ---- merge into full xfm checkpoint (fresh transformer heads) ----
    model = JointTransformer(cnn=cnn).to(dev)
    model.eval()
    state = {'arch': 'joint_xfm', 'window': window,
             'state_dict': cnn.state_dict(),
             'embed_in': model.embed_in.state_dict(),
             'pos': model.pos.detach().cpu(),
             'enc': model.enc.state_dict(),
             'head': model.head.state_dict(),
             'kadd_head': model.kadd_head.state_dict(),
             'key_head': model.key_head.state_dict(),
             'd_model': 64, 'best_val_acc': best, 'seed': args.seed,
             'target': 'sbox', 'joint': True}
    torch.save(state, args.out)
    print(f'[+] wrote {args.out} (best val top1 {best*100:.1f}%)')

    # ---- stage 2: transformer trajectory replay on real evidence ----
    if args.stage2_epochs <= 0:
        return

    def prep(t):
        t = t.astype(np.float64)
        if ref is not None:
            t = align_trace(t, ref)
        t = zscore(t).astype(np.float32)
        return None if t.size < offset + window else t[offset:offset + window]

    hyps = lab.all_hypotheses()
    opt = torch.optim.Adam(model.parameters(), lr=1e-4)
    for ep_i in range(1, args.stage2_epochs + 1):
        model.train()
        tot = 0.0
        n_batches = 0
        for e in eps:
            bits = np.unpackbits(np.frombuffer(e['key'], np.uint8),
                                 bitorder='little')
            th = torch.tensor([[int((bits[c] << 1) | bits[64 + c])
                                for c in range(N_COLS)]],
                              dtype=torch.int64, device=dev)
            ev_stream, kept = [], []
            for nonce_b, tr_raw in zip(e['nonces'], e['traces']):
                trp = prep(tr_raw)
                if trp is None:
                    continue
                kept.append((nonce_b, trp))
                nb = np.frombuffer(nonce_b, np.uint8)[None]
                with torch.no_grad():
                    x = torch.tensor(trp[None, None],
                                     dtype=torch.float32, device=dev)
                    lp = torch.log_softmax(cnn(x), dim=-1)[0]
                ev = np.full((N_COLS, N_HYPS), -1e3, dtype=np.float32)
                for col in range(N_COLS):
                    pr = lab.hypothesis_labels(col, nb, hyps)[0]
                    for h, v in enumerate(pr):
                        v = int(v)
                        if 0 <= v < N_CLASSES:
                            ev[col, h] = lp[col, v].item()
                ev_stream.append(torch.tensor(ev, dtype=torch.float32,
                                              device=dev))
            if len(ev_stream) < 2:
                continue
            evt = torch.stack(ev_stream, 1)
            prev_hist = [torch.zeros(N_COLS, N_HYPS, device=dev)]
            alive_hist = [torch.ones(N_COLS, N_HYPS, device=dev)]
            rloss = 0.0
            for t_step in range(evt.shape[1]):
                post = model.forward_causal(
                    evt[:, :t_step + 1],
                    torch.stack(prev_hist, 1),
                    torch.stack(alive_hist, 1))[:, -1]
                rloss = rloss + lossf(post, th[0])
                prev_hist.append(post.detach())
                alive_hist.append((post.detach() > 1e-3).float())
            # KADD byte-head supervision on the same traces (real signal)
            xb = torch.tensor(np.stack([k for _, k in kept]),
                              dtype=torch.float32, device=dev)[:, None]
            klogits = model.kadd_logits(xb).view(-1, 9)
            ktargets = np.concatenate([
                lab.kadd_words_hw(
                    np.frombuffer(e['key'], np.uint8)[None].repeat(1, 0),
                    np.frombuffer(n, np.uint8)[None])[0]
                for n, _ in kept])
            kt = torch.tensor(ktargets.reshape(-1), dtype=torch.int64,
                              device=dev)
            rloss = rloss + lossf(klogits, kt)
            opt.zero_grad()
            rloss.backward()
            opt.step()
            tot += float(rloss.detach())
        print(f'  stage2 epoch {ep_i}/{args.stage2_epochs} '
              f'trajectory loss {tot:.1f}', flush=True)

    state['enc'] = model.enc.state_dict()
    state['head'] = model.head.state_dict()
    state['embed_in'] = model.embed_in.state_dict()
    state['pos'] = model.pos.detach().cpu()
    state['kadd_head'] = model.kadd_head.state_dict()
    state['key_head'] = model.key_head.state_dict()
    torch.save(state, args.out)
    print(f'[+] wrote {args.out} with stage2-trained integrator')


if __name__ == '__main__':
    main()
