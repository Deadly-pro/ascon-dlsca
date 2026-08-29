#!/usr/bin/env python3
r"""adaptive_gru.py — parallel full-key ACPPA with the GRU belief integrator.

The joint CNN + GRU model (train_joint_gru.py) replaces the hand-coded
`log_acc += logp` posterior accumulation of adaptive_parallel.py:

  per query, per column:
    evidence = CNN log-prob of each hyp's predicted class for this nonce
    post, h  = GRU.step(evidence, prev_post, alive_mask, h)

  - the GRU learns the belief-update rule (evidence integration + prior
    interactions between hypotheses),
  - the alive mask IS the feedback loop: hypotheses whose posterior drops
    below --elim-p are eliminated, and the mask is fed back into the GRU
    input so the model knows what is still in play,
  - the separating-nonce picker only considers alive hypotheses.

One nonce packs separating (n0,n1) choices for all still-alive columns;
one forward pass scores all 64 columns. A column converges when its top
hypothesis repeats --stable-n queries at posterior > --converge-p.

Live training (--live-train): capture (nonce, trace) pairs at the known
attack key, store in a replay buffer, and periodically fine-tune the CNN
feature extractor + GRU on the buffer (labels: true HW per column from the
oracle). This closes the profiling-domain gap on the real board.

Usage (sim):
    .venv/bin/python training/adaptive_gru.py \
        --model training/models/joint_husky_g25.pt \
        --npz training/data/husky_g25.npz \
        --key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 --sim --sim-amp 8.0

Usage (hardware):
    .venv/bin/python training/adaptive_gru.py \
        --model training/models/joint_husky_g25.pt \
        --npz training/data/husky_g25.npz \
        --key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 \
        --gain 25 --M 64 --live-train
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
from train_joint import JointCNN, N_COLS, N_CLASSES
from train_joint_gru import JointGRU, N_HYPS
from preprocess import align_trace, zscore


class GRUEngine:
    """Joint CNN + GRU scoring engine with per-column hidden states."""

    def __init__(self, model_path, npz_path):
        ckpt = torch.load(model_path, map_location='cpu')
        self.window = ckpt['window']
        self.gru_hidden = ckpt.get('gru_hidden', 64)
        self.cnn = JointCNN()
        self.cnn.load_state_dict(ckpt['state_dict'])
        self.gru = torch.nn.GRUCell(N_HYPS * 3, self.gru_hidden)
        self.head = torch.nn.Linear(self.gru_hidden, N_HYPS)
        if 'gru_state_dict' in ckpt:
            self.gru.load_state_dict(ckpt['gru_state_dict'])
            self.head.load_state_dict(ckpt['head_state_dict'])
        self.cnn.eval()
        self.gru.eval()
        self.head.eval()
        d = np.load(npz_path, allow_pickle=True)
        self.ref = d.get('ref')
        self.offset = int(d.get('offset', 0)) if 'offset' in d else 0
        if self.ref is None:
            self.ref = d['traces'].mean(axis=0).astype(np.float32)

    def preprocess(self, trace):
        if trace.size < self.offset + self.window:
            return None
        t = trace.astype(np.float64)
        t = align_trace(t, self.ref)
        t = zscore(t).astype(np.float32)
        return t[self.offset:self.offset + self.window]

    def evidence_all(self, trace, nonce):
        """(64,4) evidence: CNN log-prob of each hyp's predicted class."""
        tr = self.preprocess(trace)
        if tr is None:
            return None
        hyps = lab.all_hypotheses()
        nb = np.frombuffer(nonce, np.uint8)[None]
        with torch.no_grad():
            logits = self.cnn(torch.tensor(tr[None, None],
                                           dtype=torch.float32))
            lp = torch.log_softmax(logits, dim=-1)[0]      # (64,6)
        ev = np.full((N_COLS, N_HYPS), -1e3, dtype=np.float32)
        for col in range(N_COLS):
            pred = lab.hypothesis_labels(col, nb, hyps)[0]
            for h, v in enumerate(pred):
                v = int(v)
                if v in range(N_CLASSES):
                    ev[col, h] = lp[col, v].item()
        return ev

    def step(self, ev_rows, post_rows, alive_rows, h_rows):
        """GRU update for a batch of columns. Returns (post, h)."""
        with torch.no_grad():
            x = torch.tensor(np.concatenate(
                [ev_rows, post_rows, alive_rows], axis=1), dtype=torch.float32)
            h = torch.tensor(h_rows, dtype=torch.float32)
            h = self.gru(x, h)
            post = torch.softmax(self.head(h), dim=-1).numpy()
        return post, h.numpy()


def pack_nonce(choices, rng):
    nonce = rng.integers(0, 256, size=16, dtype=np.uint8)
    for col, (n0, n1) in choices.items():
        b0, bit = col // 8, col % 8
        nonce[b0] = (nonce[b0] & ~(1 << bit)) | (np.uint8(n0) << bit)
        nonce[8 + b0] = (nonce[8 + b0] & ~(1 << bit)) | (np.uint8(n1) << bit)
    return nonce


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model', required=True, help='joint CNN+GRU *.pt')
    ap.add_argument('--npz', required=True)
    ap.add_argument('--key', default=None, help='16-byte target key hex')
    ap.add_argument('--max-queries', type=int, default=400)
    ap.add_argument('--converge-p', type=float, default=0.99)
    ap.add_argument('--stable-n', type=int, default=5)
    ap.add_argument('--elim-p', type=float, default=1e-3,
                    help='posterior below this kills the hypothesis')
    ap.add_argument('--M', type=int, default=1,
                    help='traces per query, averaged (+10log10(M) dB)')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--gain', type=int, default=25)
    ap.add_argument('--sim', action='store_true')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset',
                                                     'husky_g25.h5'))
    ap.add_argument('--sim-amp', type=float, default=1.0)
    ap.add_argument('--sim-flat', type=float, default=0.0)
    ap.add_argument('--sim-target', default='sbox64')
    ap.add_argument('--live-train', action='store_true',
                    help='fine-tune CNN+GRU on captured traces (board only)')
    ap.add_argument('--lt-buffer', type=int, default=128,
                    help='replay buffer size for live training')
    ap.add_argument('--lt-every', type=int, default=10,
                    help='fine-tune once per N queries')
    ap.add_argument('--lt-epochs', type=int, default=3)
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon',
                                         'ascon_cw305_top.bit'))
    args = ap.parse_args()

    if not args.key:
        sys.exit('--key required')
    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('--key must be 16 bytes hex')

    eng = GRUEngine(args.model, args.npz)
    print(f'[+] GRU engine: window {eng.window}, hidden {eng.gru_hidden}')
    print(f'[+] key {args.key}, M={args.M} avg, elim-p {args.elim_p}, '
          f'{args.stable_n}x same-hyp @ p>{args.converge_p}')

    hyps = lab.all_hypotheses()
    rng = np.random.default_rng(args.seed)

    if args.sim:
        from sim_board import SimBoard
        lq = SimBoard(args.sim_h5, key, column=0, amp=args.sim_amp,
                      seed=args.seed, flat_p=args.sim_flat,
                      target=args.sim_target)
    else:
        import live_query
        lq = live_query.LiveQuery(args.bitstream, key, gain=args.gain)

    # per-column GRU state
    h_rows = np.zeros((N_COLS, eng.gru_hidden), dtype=np.float32)
    post_rows = np.zeros((N_COLS, N_HYPS), dtype=np.float32)
    post_rows[:, 0] = 1.0          # uniform start
    alive_rows = np.ones((N_COLS, N_HYPS), dtype=np.float32)
    stable = np.zeros(N_COLS, dtype=int)
    done = np.zeros(N_COLS, dtype=bool)
    top = np.zeros(N_COLS, dtype=int)
    buf_traces, buf_nonces = [], []
    t0 = time.time()

    for q in range(1, args.max_queries + 1):
        # ---- 1. pick separating (n0,n1) per alive column, pack ----
        choices = {}
        for col in range(N_COLS):
            if done[col]:
                continue
            alive = alive_rows[col] > 0.5
            if alive.sum() == 0:
                alive[post_rows[col].argmax()] = True
            best = None
            ties = []
            for n0 in (0, 1):
                for n1 in (0, 1):
                    nn = np.zeros(16, dtype=np.uint8)
                    nn[col // 8] |= np.uint8(n0 << (col % 8))
                    nn[8 + col // 8] |= np.uint8(n1 << (col % 8))
                    pred = lab.hypothesis_labels(col, nn[None], hyps)[0]
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
        if args.live_train and not args.sim:
            buf_traces.append(trace)
            buf_nonces.append(bytes(nonce))
            if len(buf_traces) > args.lt_buffer:
                buf_traces.pop(0)
                buf_nonces.pop(0)

        # ---- 3. evidence + GRU belief update for all alive columns ----
        ev = eng.evidence_all(trace, nonce)
        if ev is None:
            continue
        cols = [c for c in range(N_COLS) if not done[c]]
        if cols:
            post, h = eng.step(ev[cols], post_rows[cols], alive_rows[cols],
                               h_rows[cols])
            post_rows[cols] = post
            h_rows[cols] = h
            # elimination feedback
            alive_rows[cols] = (post > args.elim_p).astype(np.float32)
            for c in cols:
                if alive_rows[c].sum() == 0:
                    alive_rows[c, int(post_rows[c].argmax())] = 1.0
                top[c] = int(post_rows[c].argmax())
                if post_rows[c, top[c]] > args.converge_p:
                    stable[c] += 1
                    if stable[c] >= args.stable_n:
                        done[c] = True
                else:
                    stable[c] = 0

        # ---- 4. live fine-tuning on the replay buffer ----
        if args.live_train and not args.sim and q % args.lt_every == 0 \
                and len(buf_traces) >= 16:
            _live_tune(eng, buf_traces, buf_nonces, key, args)

        n_done = int(done.sum())
        if q <= 3 or q % 10 == 0 or n_done == N_COLS:
            print(f'  q {q:4d}  cols done {n_done}/64  '
                  f'[{time.time()-t0:.0f}s]', flush=True)
        if n_done == N_COLS:
            break

    lq.close()

    # ---- assemble 128-bit key ----
    bits = np.zeros(128, dtype=np.uint8)
    failed = []
    for col in range(N_COLS):
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
    print(f'\n[+] queries used: {q}  converged: {N_COLS - len(failed)}/{N_COLS}')
    print(f'[+] recovered key: {candidate.hex()}')
    print(f'[+] target key   : {key.hex()}')
    print(f'[+] bit match    : {match:.1f}%')
    if failed:
        print(f'[!] non-converged columns: {failed}')

    # ---- verify full key ----
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


def _live_tune(eng, traces, nonces, key, args):
    """Fine-tune CNN+GRU on the replay buffer (labels = oracle HW)."""
    hyps = lab.all_hypotheses()
    kb = np.frombuffer(key, np.uint8)[None]
    nb_all = np.frombuffer(b''.join(nonces), np.uint8).reshape(-1, 16)
    labels = lab.round1_sbox_hw(kb, nb_all)      # (B,64) true HW per column
    X = []
    for tr in traces:
        p = eng.preprocess(tr)
        if p is None:
            return
        X.append(p)
    X = torch.tensor(np.array(X), dtype=torch.float32)[:, None]
    Y = torch.tensor(labels, dtype=torch.int64)
    lossf = torch.nn.CrossEntropyLoss()
    opt = torch.optim.Adam(
        list(eng.cnn.parameters()) + list(eng.gru.parameters()) +
        list(eng.head.parameters()), lr=1e-4)
    eng.cnn.train()
    eng.gru.train()
    eng.head.train()
    for _ in range(args.lt_epochs):
        logits = eng.cnn(X)                        # (B,64,6)
        loss = 0.0
        for c in range(N_COLS):
            loss = loss + lossf(logits[:, c], Y[:, c])
        opt.zero_grad()
        loss.backward()
        opt.step()
    eng.cnn.eval()
    eng.gru.eval()
    eng.head.eval()
    print(f'    [live-tune] loss {loss.item():.3f} '
          f'on {len(traces)} traces', flush=True)


if __name__ == '__main__':
    main()
