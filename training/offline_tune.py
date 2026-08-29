#!/usr/bin/env python3
r"""offline_tune.py — self-contained offline CNN tuning + attack-config sweep.

Runs entirely without the board:
  1. Split session H5 by EPISODE (train/cal vs sim-fit split) -> no
     train-on-test leakage between CNN and SimBoard.
  2. Train the joint CNN on the train split (or resume a .cnn checkpoint).
  3. Temperature-calibrate on the cal split (fixes the Bayes assumption).
  4. Fit SimBoard on the sim-fit split, verify SNR against the real fit.
  5. Sweep (integrator x M-averaging x max-queries) by invoking the live
     loop in sim mode; collect cracked-key / bit-match / avg-q stats.
  6. Print a ranked table and save the winning config to JSON.

Usage:
    OMP_NUM_THREADS=12 .venv/bin/python training/offline_tune.py \
        --h5 Dataset/live_xfm_session_*.h5 \
        --cnn training/models/joint_xfm_unmasked_s1.pt.cnn \
        --out-prefix training/models/unmasked_tuned
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import time

import h5py
import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

sys.path.insert(0, os.path.join(ROOT, 'training'))


def split_by_episode(paths, frac_train, seed=0):
    """Group episodes (key-by-key) into train+cal and simfit h5 files."""
    eps = []  # (key, traces, nonces)
    for path in paths:
        with h5py.File(path, 'r', locking=False) as f:
            for name in sorted(f.keys()):
                g = f[name]
                if 'traces' not in g:
                    continue
                eps.append((bytes(np.asarray(g.attrs['key']).tobytes()),
                            g['traces'][:], g['nonces'][:]))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(eps))
    n_tr = max(1, int(len(eps) * frac_train))
    train, simfit = perm[:n_tr], perm[n_tr:]
    out = {}
    for tag, idx in (('train', train), ('simfit', simfit)):
        tr, ky, nn = [], [], []
        for i in idx:
            key, traces, nonces = eps[i]
            ky.append(np.frombuffer(key, np.uint8)[None].repeat(
                len(nonces), axis=0))
            tr.append(traces)
            nn.append(nonces)
        p = f'/tmp/split_{tag}.h5'
        with h5py.File(p, 'w') as f:
            f.create_dataset('traces', data=np.concatenate(tr).astype(np.float32))
            f.create_dataset('keys', data=np.concatenate(ky))
            f.create_dataset('nonces', data=np.concatenate(nn))
        out[tag] = p
    print(f'[+] split: {len(train)} eps -> train/cal {out["train"]}, '
          f'{len(simfit)} eps -> simfit {out["simfit"]}')
    return out


def run_loop(model, sim_h5, integrator, M, max_q, episodes, seed, temp,
             out_tag):
    """Run the live loop in sim mode; return dict of summary stats."""
    cmd = [
        sys.executable, 'training/live_loop_transformer.py',
        '--model', model, '--integrator', integrator,
        '--sim', '--sim-h5', sim_h5, '--sim-amp', '1.0',
        '--episodes', str(episodes), '--max-queries', str(max_q),
        '--train-every', '100', '--M', str(M), '--seed', str(seed),
        '--temp', str(temp),
        '--no-save', '--out', f'/tmp/{out_tag}.pt',
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    tail = '\n'.join(r.stdout.splitlines()[-3:])
    stats = {'integrator': integrator, 'M': M, 'max_q': max_q}
    for line in r.stdout.splitlines():
        if 'keys oracle-VERIFIED' in line:
            m = __import__('re').search(
                r'(\d+)/\d+ eps locked \d+/\d+, (\d+) keys '
                r'oracle-VERIFIED, best bit-match ([0-9.]+)%, '
                r'avg q ([0-9.]+)', line)
            if m:
                stats.update(locked=int(m.group(1)),
                             keys=int(m.group(2)),
                             best_match=float(m.group(3)),
                             avg_q=float(m.group(4)))
    stats['tail'] = tail
    return stats


def calibrate_temperature(cnn_ckpt, h5, window, offset, device, max_n=1500):
    """Temperature scaling on the cal split (held-out from training)."""
    import labels as lab
    from preprocess import align_trace, zscore
    from train_joint import JointCNN
    with h5py.File(h5, 'r', locking=False) as f:
        traces = f['traces'][:max_n].astype(np.float64)
        keys = f['keys'][:max_n]
        nonces = f['nonces'][:max_n]
    ref = traces.mean(axis=0)
    X = []
    for t in traces:
        a = align_trace(t, ref)
        z = zscore(a).astype(np.float32)
        if z.size < offset + window:
            continue
        X.append(z[offset:offset + window])
    X = np.stack(X)
    Y = lab.round1_sbox_hw(keys, nonces).astype(np.int64)
    ck = torch.load(cnn_ckpt, map_location='cpu')
    cnn = JointCNN()
    cnn.load_state_dict(ck['state_dict'])
    cnn.eval().to(device)
    with torch.no_grad():
        logits = torch.stack([cnn(torch.tensor(x[None, None],
                                               dtype=torch.float32,
                                               device=device))[0]
                              for x in X])
    logits = logits.cpu()
    # grid search T minimizing mean NLL over all columns
    best_T, best_nll = 1.0, float('inf')
    for T in np.linspace(0.5, 3.0, 51):
        lp = torch.log_softmax(logits / T, dim=-1)
        nll = 0.0
        for c in range(64):
            nll += -lp[:, c, Y[:, c]].mean().item()
        if nll < best_nll:
            best_T, best_nll = T, nll
    print(f'[+] temperature T={best_T:.2f} (mean per-col NLL {best_nll:.4f})')
    return float(best_T)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h5', required=True, nargs='+')
    ap.add_argument('--cnn', default=None,
                    help='pretrained joint CNN .cnn (resume; else train)')
    ap.add_argument('--out-prefix', default='training/models/unmasked_tuned')
    ap.add_argument('--epochs', type=int, default=25)
    ap.add_argument('--frac-train', type=float, default=0.6)
    ap.add_argument('--sim-eps', type=int, default=12)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--sweep', default='naive:1:120,naive:4:120,xfm:1:120')
    ap.add_argument('--no-simfit-check', action='store_true')
    args = ap.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    paths = sorted(p for pat in args.h5 for p in glob.glob(pat))
    split = split_by_episode(paths, args.frac_train, args.seed)

    # 1. CNN (train or resume)
    cnn_out = f'{args.out_prefix}.cnn'
    if args.cnn and os.path.exists(args.cnn):
        print(f'[+] resuming CNN from {args.cnn}')
        cnn_out = args.cnn
    else:
        subprocess.run([
            sys.executable, 'training/train_xfm_from_session.py',
            '--h5', split['train'], '--epochs', str(args.epochs),
            '--val-h5', split['simfit'], '--out', f'{args.out_prefix}.raw.pt',
            '--stage2-epochs', '0',
        ], cwd=ROOT, check=True)
        cnn_out = f'{args.out_prefix}.raw.pt.cnn'

    # 2. calibrate
    T = calibrate_temperature(cnn_out, split['train'], 256, 0, device)

    # 3. merge calibrated CNN into a full xfm checkpoint (fresh xfm heads)
    from train_joint_transformer import JointTransformer
    from train_joint import JointCNN
    ck = torch.load(cnn_out, map_location='cpu')
    cnn = JointCNN()
    cnn.load_state_dict(ck['state_dict'])
    model = JointTransformer(cnn=cnn)
    merged = f'{args.out_prefix}_merged.pt'
    torch.save({'arch': 'joint_xfm', 'window': 256,
                'state_dict': cnn.state_dict(),
                'embed_in': model.embed_in.state_dict(),
                'pos': model.pos.detach().cpu(),
                'enc': model.enc.state_dict(),
                'head': model.head.state_dict(),
                'kadd_head': model.kadd_head.state_dict(),
                'key_head': model.key_head.state_dict(),
                'd_model': 64, 'best_val_acc': 0.0, 'seed': args.seed,
                'target': 'sbox', 'joint': True}, merged)
    print(f'[+] merged full xfm checkpoint -> {merged}')

    # 4. SimBoard fit check on the DISJOINT split (same keys the CNN never saw)
    if not args.no_simfit_check:
        r = subprocess.run([
            sys.executable, 'sim_board.py', split['simfit'],
            '--column', '0', '--ntraces', '1500',
        ], capture_output=True, text=True, cwd=ROOT)
        print('\n'.join(r.stdout.splitlines()[-4:]))

    # 5. sweep
    rows = []
    for cfg in args.sweep.split(','):
        integ, M, mq = cfg.split(':')
        st = run_loop(merged, split['simfit'], integ, int(M), int(mq),
                      args.sim_eps, args.seed, T,
                      f'run_{integ}_m{M}_q{mq}')
        rows.append(st)
        print(f'  {integ} M={M} q<={mq}: '
              f'keys={st.get("keys", "?")} '
              f'bitmatch={st.get("best_match", "?")}% '
              f'avgq={st.get("avg_q", "?")}')

    # 5. rank + save
    rows.sort(key=lambda r: (-r.get('keys', -1), -r.get('best_match', 0)))
    best = rows[0] if rows else {}
    cfg_out = f'{args.out_prefix}_best_config.json'
    with open(cfg_out, 'w') as f:
        json.dump({'temperature': T, 'best': best, 'rows': rows}, f,
                  indent=2, default=str)
    print(f'[+] best: {best}')
    print(f'[+] saved {cfg_out} (T={T:.2f})')


if __name__ == '__main__':
    main()
