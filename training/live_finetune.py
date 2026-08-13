#!/usr/bin/env python3
r"""live_finetune.py — Scheme A: known-key live fine-tuning for on-board ACPPA.

Captures traces from the CW305 at a KNOWN key (or a fresh random key per
trace with --random-keys), labels them exactly (the key is known in the lab,
so labels are oracle-exact, not hypothesized), and fine-tunes a pretrained
profile on (live_trace, exact_label) pairs. This adapts the profile to the
device's true noise/leakage shape AND to the attack's nonce distribution.

--random-keys is STRONGLY recommended: a fixed key only produces a
key-dependent subset of the column's structural HW classes (e.g. {3,4} for
col 0 under key 0001...), so the finetune collapses onto those classes and
the attack scores garbage for the other key's separating-nonce classes. A
fresh random key per trace spreads the true-HW class over the full support
{0..5} while labels stay oracle-exact.

Then attack a FRESH unknown key with the fine-tuned model:

    .venv/bin/python training/adaptive.py --attack \
        --npz training/data/main_unmasked_merged.npz \
        --model training/models/main_unmasked_c0_liveft.pt \
        --column 0 --key <NEW-16-BYTE-HEX> --max-queries 500

Fine-tuning loop details (must match the attack's features exactly):
  - preprocessing: Profile.preprocess (align full trace -> z-score full ->
    crop to window) — identical to the attack's live path
  - features: build_input(model arch) — identical to Profile.log_probs
  - loss: cross-entropy on the exact HW class, class-weighted like train.py
  - checkpoint format: identical to train.py (arch/column/window/classes/
    state_dict) so adaptive.py and attack.py load it unchanged

Usage:
    .venv/bin/python training/live_finetune.py \
        --model training/models/main_unmasked_merged_c0_sbox_cnn1.pt \
        --npz training/data/main_unmasked_merged.npz \
        --key 000102030405060708090a0b0c0d0e0f --column 0 \
        --ntrain 300 --epochs 20 --lr 1e-4 \
        --out training/models/main_unmasked_c0_liveft.pt
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
from train import CNN, MLP
from attack import build_input
from adaptive import Profile


def true_hyp_index(key, column):
    """Index (0..3) of the true 2-bit key hypothesis for this column."""
    k0 = (key[column // 8] >> (column % 8)) & 1
    k1 = (key[8 + column // 8] >> (column % 8)) & 1
    hyps = lab.all_hypotheses()
    return int(np.flatnonzero((hyps[:, 0] == k0) & (hyps[:, 1] == k1))[0])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model', required=True, help='pretrained profile *.pt')
    ap.add_argument('--npz', required=True, help='npz used to train the profile '
                    '(provides the alignment reference)')
    ap.add_argument('--key', default=None,
                    help='KNOWN key hex for capture/labels (required unless '
                         '--random-keys)')
    ap.add_argument('--random-keys', action='store_true',
                    help='draw a fresh random key per trace (labels stay '
                         'oracle-exact since we generate the key); spreads '
                         'the true-HW class across all classes in the '
                         'column\'s structural support — fixes the fixed-key '
                         'class collapse that made ACPPA lock onto wrong bits')
    ap.add_argument('--column', type=int, default=0)
    ap.add_argument('--ntrain', type=int, default=300, help='live traces to capture')
    ap.add_argument('--epochs', type=int, default=20)
    ap.add_argument('--batch', type=int, default=64)
    ap.add_argument('--lr', type=float, default=1e-4)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', default=None, help='output *.pt (default: <model>_liveft.pt)')
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--gain', type=int, default=-2)
    ap.add_argument('--offset', type=int, default=700)
    ap.add_argument('--std-floor', type=float, default=0.01)
    ap.add_argument('--sim', action='store_true',
                    help='use SimBoard instead of the board (testing only)')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset',
                                                     'main_unmasked_merged.h5'))
    ap.add_argument('--sim-amp', type=float, default=8.0,
                    help='leakage amp for the virtual board (testing only)')
    args = ap.parse_args()

    if not args.random_keys and not args.key:
        sys.exit('--key is required unless --random-keys is set')
    key = bytes.fromhex(args.key) if args.key else os.urandom(16)
    out = args.out or args.model.replace('.pt', '_liveft.pt')
    os.makedirs(os.path.dirname(out), exist_ok=True)

    prof = Profile(args.model, args.npz)
    col = args.column
    hyps = lab.all_hypotheses()
    print(f'[+] profile {os.path.basename(args.model)} col {col} '
          f'({prof.arch}, support {prof.classes})')
    if args.random_keys:
        print('[+] RANDOM-KEY mode: fresh key per trace (labels oracle-exact, '
              'true-HW class spreads across the column\'s full support)')
    else:
        hyp_true = true_hyp_index(key, col)
        print(f'[+] known key {key.hex()} -> col {col} true hyp {hyp_true} '
              f'= ({hyps[hyp_true,0]}, {hyps[hyp_true,1]})')

    import live_query
    if args.sim:
        from sim_board import SimBoard
        lq = SimBoard(args.sim_h5, key, column=col, amp=args.sim_amp,
                      seed=args.seed)
        print(f'[+] SIM BOARD (amp {args.sim_amp}x) — testing only')
    else:
        lq = live_query.LiveQuery(args.bitstream, key, gain=args.gain,
                                  offset=args.offset, std_floor=args.std_floor)
    rng = np.random.default_rng(args.seed)

    # ---- capture live traces, label exactly ----
    # Nonces are ALWAYS random (separating nonces would collapse every
    # training label onto one class, since the true key's class is fixed; the
    # ATTACK uses separating nonces later). With --random-keys the key is
    # fresh per trace too, so the true-HW class also varies with the key —
    # covering every class in the column's structural support (a fixed key
    # only produces a key-dependent subset, which is why the earlier finetune
    # collapsed onto {3,4} and the attack key needing class 5 scored garbage).
    traces, labels = [], []
    t0 = time.time()
    attempts = 0
    while len(traces) < args.ntrain:
        attempts += 1
        if args.random_keys:
            key = os.urandom(16)
            if args.sim:
                lq.key = key
            else:
                lq.t.loadEncryptionKey(key)
        nonce = os.urandom(16)
        trace, _ct = lq.query(nonce)
        if trace is None:                       # trigger race / flat — retry
            continue
        trace = prof.preprocess(trace)
        if trace is None:
            continue
        hyp_true = true_hyp_index(key, col)
        # exact label: HW class of col c under the TRUE key bits for this nonce
        pred = lab.hypothesis_labels(col, np.frombuffer(nonce, np.uint8)[None],
                                     hyps)[0]
        traces.append(trace)
        labels.append(int(pred[hyp_true]))
        if len(traces) % 50 == 0:
            print(f'    captured {len(traces)}/{args.ntrain} '
                  f'[{time.time()-t0:.0f}s]')
    print(f'[+] captured {len(traces)} live traces in {attempts} attempts '
          f'({time.time()-t0:.0f}s)')
    X = np.stack(traces)                        # (N, W) already aligned+z-scored
    Y = np.array(labels, dtype=np.int64)
    from collections import Counter
    print(f'[+] label counts: {dict(sorted(Counter(Y).items()))}')

    # ---- fine-tune ----
    torch.manual_seed(args.seed)
    model = prof.model
    Xf_all = build_input(X, prof.arch, prof.window, model)  # (N, C, W)
    Xt = torch.tensor(Xf_all, dtype=torch.float32)
    Yt = torch.tensor(Y)
    model.train()
    n_classes = len(prof.classes)
    counts = np.bincount(Y, minlength=n_classes)
    w = torch.tensor(len(Y) / (n_classes * counts.astype(np.float64)),
                     dtype=torch.float32)
    w[counts == 0] = 0.0
    lossf = nn.CrossEntropyLoss(weight=w)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)

    def acc():
        with torch.no_grad():
            return float((model(Xt).argmax(1) == Yt).float().mean())

    best_acc, best_state = 0.0, None
    for ep in range(1, args.epochs + 1):
        model.train()
        perm = torch.randperm(len(Xt))
        for i in range(0, len(perm), args.batch):
            bi = perm[i:i + args.batch]
            opt.zero_grad()
            lossf(model(Xt[bi]), Yt[bi]).backward()
            opt.step()
        model.eval()
        a = acc()
        if a > best_acc:
            best_acc = a
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        print(f'  ep {ep:3d}  train-acc {a*100:.1f} %  [{time.time()-t0:.0f}s]')
    model.load_state_dict(best_state)

    ckpt = torch.load(args.model, map_location='cpu')
    ckpt['state_dict'] = best_state
    ckpt['live_finetune'] = {'key': key.hex(), 'column': col,
                             'random_keys': bool(args.random_keys),
                             'ntrain': len(X), 'epochs': args.epochs,
                             'lr': args.lr, 'best_train_acc': best_acc,
                             'seconds': float(time.time() - t0)}
    torch.save(ckpt, out)
    print(f'[+] wrote {out} (train-acc {best_acc*100:.1f} % over '
          f'{len(X)} live traces)')

    lq.close()
    print(f'[+] next: attack a FRESH key with '
          f'--model {os.path.basename(out)}')


if __name__ == '__main__':
    main()
