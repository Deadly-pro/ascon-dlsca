#!/usr/bin/env python3
r"""active_loop.py — closed-loop online training + key guessing, epoch based.

One unified loop that does, per captured trace:
  1. the MODEL picks the next nonce (posterior-aware separating selection)
  2. the trace is fed to the model as an online training example (the key is
     known to the trainer, so labels are oracle-exact)
  3. the model scores the 4 key hypotheses, the running posterior is updated,
     and the model's current key guess is printed

An EPOCH ends when EITHER:
  - the same key guess (top hypothesis) repeats for --stable-n consecutive
    queries with posterior > --converge-p   (high-confidence lock), OR
  - the trace budget --max-traces is exhausted

At the end of each epoch a fresh RANDOM key is loaded (labels stay
oracle-exact; this spreads the true-HW class over the full support, which is
what fixed the fixed-key class collapse). Model weights carry across epochs,
so the model is being trained *while* it guesses: later epochs should lock
faster and more often correct. Epoch summaries are appended to a JSONL log,
and a checkpoint is saved after every epoch.

Final attack mode: pass --attack-key <hex> — the trainer stops knowing the
key, online updates stop, and the same loop runs against one fixed key.

Usage (hardware — Husky or CW-Lite):
    .venv/bin/python training/active_loop.py \
        --model training/models/main_unmasked_merged_c0_sbox_cnn1.pt \
        --npz training/data/main_unmasked_merged.npz \
        --column 0 --epochs 20 --max-traces 120 \
        --gain 20 --out training/models/active_c0

Usage (sim, no board):
    .venv/bin/python training/active_loop.py \
        --model training/models/main_unmasked_merged_c0_sbox_cnn1.pt \
        --npz training/data/main_unmasked_merged.npz \
        --column 0 --epochs 5 --max-traces 60 --sim --sim-amp 8.0
"""
import argparse
import json
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
from attack import build_input
from adaptive import Profile, pick_separating_nonce, score_trace


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model', required=True, help='base profile *.pt')
    ap.add_argument('--npz', required=True, help='profiling npz (alignment ref)')
    ap.add_argument('--column', type=int, default=0)
    ap.add_argument('--epochs', type=int, default=20,
                    help='random-key training+guessing epochs')
    ap.add_argument('--max-traces', type=int, default=120,
                    help='epoch ends after this many accepted traces')
    ap.add_argument('--stable-n', type=int, default=5,
                    help='same key guess repeated this many times with high '
                         'confidence ends the epoch')
    ap.add_argument('--converge-p', type=float, default=0.99,
                    help='posterior threshold for a high-confidence guess')
    ap.add_argument('--lr', type=float, default=1e-4,
                    help='online per-trace learning rate')
    ap.add_argument('--replay', type=int, default=500,
                    help='replay-buffer size: online updates train on batches '
                         'drawn from the last N accepted traces (0 = pure '
                         'single-trace SGD; prevents catastrophic collapse)')
    ap.add_argument('--train-nonce-mode', choices=['separating', 'random'],
                    default='separating',
                    help='input selection during train epochs: separating = '
                         'model-driven (posterior-aware picker), random = '
                         'exploratory random nonces (spreads classes better, '
                         'prevents overfitting to one nonce pattern)')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', default=None,
                    help='output dir for epoch checkpoints + summary.jsonl')
    ap.add_argument('--attack-key', default=None,
                    help='fixed 16-byte key hex: switches to attack mode '
                         '(no online updates, no oracle labels)')
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--gain', type=int, default=20)
    ap.add_argument('--offset', type=int, default=700)
    ap.add_argument('--std-floor', type=float, default=0.001,
                    help='minimum trace std to accept (default 0.001 for Husky)')
    ap.add_argument('--sim', action='store_true',
                    help='use SimBoard instead of hardware')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset',
                                                     'main_unmasked_merged.h5'))
    ap.add_argument('--sim-amp', type=float, default=8.0)
    args = ap.parse_args()

    attack_key = bytes.fromhex(args.attack_key) if args.attack_key else None
    if attack_key is not None and len(attack_key) != 16:
        sys.exit('--attack-key must be 16 bytes hex')

    prof = Profile(args.model, args.npz)
    col = args.column
    hyps = lab.all_hypotheses()
    print(f'[+] active loop col {col} arch {prof.arch} support {prof.classes}')
    print(f'[+] epoch ends: {args.stable_n}x same guess @ p>{args.converge_p} '
          f'OR {args.max_traces} traces')
    if attack_key is not None:
        print(f'[+] ATTACK MODE: fixed key {attack_key.hex()}, '
              f'no online updates')
    else:
        print(f'[+] TRAIN MODE: fresh random key per epoch, oracle labels, '
              f'online lr {args.lr}')

    # ---- board / sim ----
    if args.sim:
        from sim_board import SimBoard
        lq = SimBoard(args.sim_h5, os.urandom(16), column=col,
                      amp=args.sim_amp, seed=args.seed)
    else:
        import live_query
        lq = live_query.LiveQuery(args.bitstream, os.urandom(16),
                                  gain=args.gain, offset=args.offset,
                                  std_floor=args.std_floor)

    model = prof.model
    torch.manual_seed(args.seed)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    lossf = nn.CrossEntropyLoss()
    rng = np.random.default_rng(args.seed)
    replay_x, replay_y = [], []          # replay buffer for online training

    out_dir = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       'models', f'active_c{col}')
    os.makedirs(out_dir, exist_ok=True)
    log_path = os.path.join(out_dir, 'summary.jsonl')

    for epoch in range(1, args.epochs + 1):
        key = attack_key if attack_key is not None else os.urandom(16)
        if args.sim:
            lq.key = key
        else:
            lq.t.loadEncryptionKey(key)
        log_acc = np.full(len(hyps), 0.0)
        post = None
        stable = 0
        top = 0
        t0 = time.time()
        n_traces = 0
        n_flat = 0
        converged = False

        for _ in range(args.max_traces):
            if attack_key is None and args.train_nonce_mode == 'random':
                nonce = rng.integers(0, 256, size=16, dtype=np.uint8)
            else:
                nonce = pick_separating_nonce(col, prof.support, rng, post=post)
            trace, _ct = lq.query(nonce)
            if trace is None:
                n_flat += 1
                continue
            trace = prof.preprocess(trace)
            if trace is None:
                n_flat += 1
                continue
            n_traces += 1

            hyp_true = int(np.flatnonzero(
                (hyps[:, 0] == ((key[col // 8] >> (col % 8)) & 1)) &
                (hyps[:, 1] == ((key[8 + col // 8] >> (col % 8)) & 1)))[0])
            pred = lab.hypothesis_labels(
                col, np.frombuffer(nonce, np.uint8)[None], hyps)[0]
            label = int(pred[hyp_true])

            # online training: push into replay buffer, train on a batch
            if attack_key is None:
                replay_x.append(trace)
                replay_y.append(label)
                if len(replay_x) > args.replay:
                    replay_x.pop(0)
                    replay_y.pop(0)
                model.train()
                if args.replay > 0:
                    bidx = rng.choice(len(replay_x),
                                      size=min(args.batch if hasattr(args, 'batch') else 32, len(replay_x)),
                                      replace=False)
                    Xb = np.stack([replay_x[i] for i in bidx])
                    yb = torch.tensor([replay_y[i] for i in bidx])
                    Xf = build_input(Xb, prof.arch, prof.window, model)
                else:
                    Xf = build_input(trace[None], prof.arch, prof.window, model)
                    yb = torch.tensor([label])
                opt.zero_grad()
                lossf(model(torch.as_tensor(Xf, dtype=torch.float32)), yb).backward()
                opt.step()

            # key guess: score 4 hyps, update posterior
            model.eval()
            logp_row = prof.log_probs(trace[None])[0]
            sc = score_trace(logp_row, nonce, col, prof.classes)
            log_acc += np.where(np.isfinite(sc), sc, -1e3)
            post = np.exp(log_acc - log_acc.max())
            post /= post.sum()
            top = int(post.argmax())
            stable = stable + 1 if post[top] > args.converge_p else 0
            k0, k1 = int(hyps[top, 0]), int(hyps[top, 1])
            if n_traces <= 3 or n_traces % 10 == 0 or \
                    stable >= args.stable_n:
                print(f'  ep {epoch:3d} tr {n_traces:3d}  guess k0={k0} '
                      f'k1={k1}  hyp {top}  p {post[top]:.3f}')
            if stable >= args.stable_n:
                converged = True
                break

    # Guard: if no traces captured, use final posterior
    if n_traces == 0:
        top = int(post.argmax()) if 'post' in locals() else 0
        k0, k1 = int(hyps[top, 0]), int(hyps[top, 1])

    correct = (k0 == ((key[col // 8] >> (col % 8)) & 1) and
               k1 == ((key[8 + col // 8] >> (col % 8)) & 1))
    ent = float(-(post * np.log(np.maximum(post, 1e-12))).sum())
    print(f'[+] epoch {epoch}: {"LOCKED" if converged else "BUDGET OUT"} '
          f'in {n_traces} traces ({n_flat} flat), guess hyp {top} '
          f'= ({k0},{k1}), p {post[top]:.3f}, ent {ent:.2f}, '
          f'{"CORRECT" if correct else "WRONG"}, {time.time()-t0:.0f}s')

    summary = {'epoch': epoch, 'column': col, 'converged': converged,
               'n_traces': n_traces, 'n_flat': n_flat, 'hyp': top,
               'k0': k0, 'k1': k1, 'posterior': float(post[top]),
               'correct': bool(correct),
               'seconds': float(time.time() - t0)}
    if attack_key is None:
        summary['key'] = key.hex()
    with open(log_path, 'a') as f:
        f.write(json.dumps(summary) + '\n')

    ckpt = torch.load(args.model, map_location='cpu')
    ckpt['state_dict'] = {k: v.clone()
                          for k, v in model.state_dict().items()}
    ckpt['active_loop'] = summary
    ckpt_path = os.path.join(out_dir, f'ep{epoch:03d}_c{col}.pt')
    torch.save(ckpt, ckpt_path)

    lq.close()
    print(f'[+] done. checkpoints + {os.path.basename(log_path)} in {out_dir}')


if __name__ == '__main__':
    main()
