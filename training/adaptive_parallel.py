#!/usr/bin/env python3
r"""adaptive_parallel.py — parallel full-key ACPPA: all 64 columns at once.

ASCON's bit-sliced S-box makes column attacks perfectly parallel:

  column c's S-box input bits come from bit c%8 of nonce byte c//8 and
  bit c%8 of nonce byte 8 + (c//8). Columns in the same byte group use
  DIFFERENT bits of the SAME bytes, so a single 16-byte nonce can carry
  the separating (n0,n1) choice for every column simultaneously.

Loop per query:
  1. For each column, pick the (n0,n1) that best separates its still-alive
     hypotheses (posterior-aware).
  2. Pack all 64 choices into ONE nonce.
  3. Capture ONE trace; score all 64 columns (one forward pass with
     --joint-model, or per-column models otherwise).
  4. Update 64 posteriors in parallel.
  5. A column is done when its top hypothesis repeats --stable-n times at
     posterior > --converge-p. All done -> assemble 128-bit key, verify.

--M N: average N repeated captures of the same nonce per query (+10log10(N) dB
SNR, the documented lever). On the Husky this is cheap and is the single
biggest reliability gain.

Usage (sim):
    .venv/bin/python training/adaptive_parallel.py \
        --npz training/data/main_unmasked_merged.npz \
        --joint-model training/models/joint_unmasked.pt \
        --key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 --sim --sim-amp 8.0

Usage (hardware, Husky/CW-Lite auto-detected):
    .venv/bin/python training/adaptive_parallel.py \
        --npz training/data/main_unmasked_merged.npz \
        --joint-model training/models/joint_unmasked.pt \
        --key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 --gain 20 --M 4
"""
import argparse
import os
import sys
import time

import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import labels as lab
from attack import build_input


def pack_nonce(choices, rng):
    """Pack per-column (n0,n1) choices into one 16-byte nonce."""
    nonce = rng.integers(0, 256, size=16, dtype=np.uint8)
    for col, (n0, n1) in choices.items():
        b0 = col // 8
        bit = col % 8
        nonce[b0] = (nonce[b0] & ~(1 << bit)) | (np.uint8(n0) << bit)
        nonce[8 + b0] = (nonce[8 + b0] & ~(1 << bit)) | (np.uint8(n1) << bit)
    return nonce


class JointOracle:
    """Scores all 64 columns from ONE model forward pass."""

    def __init__(self, model_path, npz_path):
        from train_joint import JointCNN, N_COLS, N_CLASSES
        ckpt = torch.load(model_path, map_location='cpu')
        self.window = ckpt['window']
        self.classes = list(range(N_CLASSES))
        self.model = JointCNN()
        self.model.load_state_dict(ckpt['state_dict'])
        self.model.eval()
        d = np.load(npz_path, allow_pickle=True)
        self.ref = d.get('ref')
        if self.ref is None:
            self.ref = d['traces'].mean(axis=0).astype(np.float32)

    def preprocess(self, trace):
        from preprocess import align_trace, zscore
        if trace.size < self.window:
            return None
        t = trace.astype(np.float64)
        t = align_trace(t, self.ref)
        t = zscore(t).astype(np.float32)
        return t[:self.window]

    def log_probs_all(self, traces):
        """(N,W) -> (N, 64, 6) log-softmax for all columns."""
        X = torch.tensor(traces[:, None], dtype=torch.float32)
        with torch.no_grad():
            logits = self.model(X)
        return torch.log_softmax(logits, dim=-1).numpy()

    def score_column(self, logp_row, nonce, col):
        """(64,6) log-probs row -> (4,) hypothesis log-scores for one column."""
        hyps = lab.all_hypotheses()
        pred = lab.hypothesis_labels(col, np.array([nonce]), hyps)[0]
        scores = np.full(len(hyps), -np.inf)
        for h, v in enumerate(pred):
            v = int(v)
            if v in self.classes:
                scores[h] = logp_row[col, self.classes.index(v)]
        return scores


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--npz', required=True)
    ap.add_argument('--joint-model', default=None,
                    help='joint model *.pt (one forward pass for all 64 cols); '
                         'if omitted, uses --model-fmt per-column profiles')
    ap.add_argument('--model-fmt', default=None,
                    help="per-column model path with {col} (alternative to "
                         "--joint-model)")
    ap.add_argument('--key', default=None, help='16-byte target key hex')
    ap.add_argument('--max-queries', type=int, default=400)
    ap.add_argument('--converge-p', type=float, default=0.99)
    ap.add_argument('--stable-n', type=int, default=5)
    ap.add_argument('--M', type=int, default=1,
                    help='traces per query, averaged (+10log10(M) dB SNR)')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--gain', type=int, default=20)
    ap.add_argument('--sim', action='store_true')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset',
                                                     'main_unmasked_merged.h5'))
    ap.add_argument('--sim-amp', type=float, default=8.0)
    ap.add_argument('--sim-flat', type=float, default=0.0)
    ap.add_argument('--sim-target', default='sbox64',
                    help='SimBoard leakage target: sbox64 (all 64 columns, '
                         'the physical aggregate premise) or sbox (single col)')
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon',
                                         'ascon_cw305_top.bit'))
    args = ap.parse_args()

    if not args.key:
        sys.exit('--key required')
    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('--key must be 16 bytes hex')
    if not args.joint_model and not args.model_fmt:
        sys.exit('need --joint-model or --model-fmt')

    hyps = lab.all_hypotheses()
    rng = np.random.default_rng(args.seed)

    # ---- scorer: joint (one pass) or per-column profiles ----
    if args.joint_model:
        oracle = JointOracle(args.joint_model, args.npz)
        n_cols = 64
        print(f'[+] joint model {os.path.basename(args.joint_model)} '
              f'window {oracle.window}')
    else:
        from adaptive import Profile
        oracle = [Profile(args.model_fmt.format(col=c), args.npz)
                  for c in range(64)]
        n_cols = 64
        print(f'[+] 64 per-column profiles')
    print(f'[+] key {args.key}, M={args.M} avg, '
          f'{args.stable_n}x same-hyp @ p>{args.converge_p}')

    # ---- query engine ----
    if args.sim:
        from sim_board import SimBoard
        lq = SimBoard(args.sim_h5, key, column=0, amp=args.sim_amp,
                      seed=args.seed, flat_p=args.sim_flat,
                      target=args.sim_target)
    else:
        import live_query
        lq = live_query.LiveQuery(args.bitstream, key, gain=args.gain)

    # ---- per-column state ----
    log_acc = [np.zeros(len(hyps)) for _ in range(n_cols)]
    stable = np.zeros(n_cols, dtype=int)
    done = np.zeros(n_cols, dtype=bool)
    top = np.zeros(n_cols, dtype=int)
    post = [None] * n_cols
    t0 = time.time()

    for q in range(1, args.max_queries + 1):
        # ---- 1. pick separating (n0,n1) per column, pack into one nonce ----
        # NOTE: pack_nonce overwrites ALL 128 nonce bits (64 cols x 2 bits),
        # so the random base is fully replaced. A deterministic tiebreak
        # would make every query the SAME nonce — zero information diversity.
        # The uniform tiebreak over equal-separation (n0,n1) choices keeps
        # the nonce varying across queries.
        choices = {}
        for col in range(n_cols):
            if done[col]:
                continue
            p = post[col]
            alive = np.ones(len(hyps), dtype=bool) if p is None else (p > 1e-3)
            if alive.sum() == 0:
                alive[p.argmax()] = True
            best = None
            ties = []
            for n0 in (0, 1):
                for n1 in (0, 1):
                    nonce = np.zeros(16, dtype=np.uint8)
                    nonce[col // 8] |= np.uint8(n0 << (col % 8))
                    nonce[8 + col // 8] |= np.uint8(n1 << (col % 8))
                    pred = lab.hypothesis_labels(col, nonce[None], hyps)[0]
                    s = {int(v) for v in pred[alive]}
                    score = (len(s), sum(int(a) != int(b)
                                         for a in s for b in s if a != b))
                    if best is None or score > best[0]:
                        best = (score, n0, n1)
                        ties = [(n0, n1)]
                    elif score == best[0]:
                        ties.append((n0, n1))
            n0, n1 = ties[int(rng.integers(len(ties)))]
            choices[col] = (n0, n1)
        nonce = pack_nonce(choices, rng)

        # ---- 2. M-averaged trace ----
        pool = []
        while len(pool) < args.M:
            trace, _ct = lq.query(nonce)
            if trace is None:
                continue
            pool.append(trace)
        trace = np.mean(pool, axis=0)

        # ---- 3. score all columns ----
        if args.joint_model:
            tr = oracle.preprocess(trace)
            if tr is None:
                continue
            lp = oracle.log_probs_all(tr[None])[0]   # (64, 6)
            for col in range(n_cols):
                if done[col]:
                    continue
                sc = oracle.score_column(lp, nonce, col)
                log_acc[col] += np.where(np.isfinite(sc), sc, -1e3)
                p = np.exp(log_acc[col] - log_acc[col].max())
                p /= p.sum()
                post[col] = p
                top[col] = int(p.argmax())
                stable[col] = stable[col] + 1 if p[top[col]] > args.converge_p else 0
                if stable[col] >= args.stable_n:
                    done[col] = True
        else:
            for col in range(n_cols):
                if done[col]:
                    continue
                prof = oracle[col]
                tr = prof.preprocess(trace)
                if tr is None:
                    continue
                logp_row = prof.log_probs(tr[None])[0]
                pred = lab.hypothesis_labels(col, nonce[None], hyps)[0]
                sc = np.full(len(hyps), -np.inf)
                for h, v in enumerate(pred):
                    v = int(v)
                    if v in prof.classes:
                        sc[h] = logp_row[prof.classes.index(v)]
                log_acc[col] += np.where(np.isfinite(sc), sc, -1e3)
                p = np.exp(log_acc[col] - log_acc[col].max())
                p /= p.sum()
                post[col] = p
                top[col] = int(p.argmax())
                stable[col] = stable[col] + 1 if p[top[col]] > args.converge_p else 0
                if stable[col] >= args.stable_n:
                    done[col] = True

        n_done = int(done.sum())
        if q <= 3 or q % 10 == 0 or n_done == n_cols:
            print(f'  q {q:4d}  cols done {n_done}/64  '
                  f'[{time.time()-t0:.0f}s]', flush=True)
        if n_done == n_cols:
            break

    lq.close()

    # ---- assemble 128-bit key ----
    bits = np.zeros(128, dtype=np.uint8)
    failed = []
    for col in range(n_cols):
        if not done[col]:
            failed.append(col)
            continue
        k0, k1 = int(hyps[top[col], 0]), int(hyps[top[col], 1])
        bits[col] = k0
        bits[64 + col] = k1
    candidate = bytes(np.packbits(bits, bitorder='little'))
    truth = np.unpackbits(np.frombuffer(key, dtype=np.uint8),
                          bitorder='little')
    match = 100.0 * (1 - np.count_nonzero(bits != truth) / 128.0)
    print(f'\n[+] queries used: {q}  converged: {n_cols - len(failed)}/{n_cols}')
    print(f'[+] recovered key: {candidate.hex()}')
    print(f'[+] target key   : {key.hex()}')
    print(f'[+] bit match    : {match:.1f}%')
    if failed:
        print(f'[!] non-converged columns: {failed}')

    # ---- verify full key against ciphertext (fresh query) ----
    if args.sim:
        from sim_board import SimBoard
        vlq = SimBoard(args.sim_h5, key, column=0, amp=args.sim_amp,
                       seed=args.seed + 1, target=args.sim_target)
    else:
        import live_query
        vlq = live_query.LiveQuery(args.bitstream, candidate, gain=args.gain)
    try:
        ok, exp, got = vlq.verify_key(candidate)
        print(f'[+] verify_key: {"PASS" if ok else "FAIL"} '
              f'(oracle {exp[:24]}... fpga {got[:24]}...)')
    finally:
        vlq.close()


if __name__ == '__main__':
    main()