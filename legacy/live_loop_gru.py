#!/usr/bin/env python3
r"""live_loop_gru.py — self-play live training on the board.

The board is the training environment. Each episode:

  1. a FRESH random 128-bit key is loaded on the FPGA (set_key, no re-program),
  2. the GRU engine attacks it with the packed-nonce parallel loop (all 64
     columns, one query scores all of them), up to --max-queries,
  3. every captured (nonce, trace) pair is oracle-labelled with the KNOWN key
     (CNN targets: per-column round-1 S-box HW; GRU targets: the true
     hypothesis per column), pushed into a replay buffer,
  4. every --train-every episodes the CNN + GRU are fine-tuned on the buffer
     (labels come from the oracle, so the model learns the board's real
     leakage distribution AND the belief-update rule from live data),
  5. the episode ends (all 64 columns converged or query budget exhausted)
     and a NEW random key starts the next episode.

This is the exact scenario the attack will face: a fresh key, a query
budget, and only the GRU's posterior to decide. The model trains on its own
attack trajectories, so the profiling-domain gap (sim vs board) is closed
by construction.

Usage (board):
    .venv/bin/python training/live_loop_gru.py \
        --model training/models/joint_husky_g25.pt \
        --npz training/data/husky_g25.npz \
        --gain 25 --episodes 50 --max-queries 60 \
        --train-every 5 --M 1 --lt-epochs 2 \
        --out training/models/joint_husky_g25_live.pt

Usage (sim dry-run, no hardware):
    .venv/bin/python training/live_loop_gru.py \
        --model training/models/joint_husky_g25.pt \
        --npz training/data/husky_g25.npz \
        --sim --sim-amp 1.0 --episodes 5 --max-queries 40 \
        --train-every 2
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
from train_joint_gru import JointGRU, N_HYPS, _pick_separating
from preprocess import align_trace, zscore


def pack_nonce(choices, rng):
    nonce = rng.integers(0, 256, size=16, dtype=np.uint8)
    for col, (n0, n1) in choices.items():
        b0, bit = col // 8, col % 8
        mask = np.uint8(0xFF ^ (1 << bit))
        nonce[b0] = (nonce[b0] & mask) | (np.uint8(n0) << bit)
        nonce[8 + b0] = (nonce[8 + b0] & mask) | (np.uint8(n1) << bit)
    return nonce


class GRULoop:
    """One episode's attack state: GRU hidden/posterior/alive per column."""

    def __init__(self, eng):
        self.eng = eng
        self.h = np.zeros((N_COLS, eng.gru_hidden), dtype=np.float32)
        self.post = np.zeros((N_COLS, N_HYPS), dtype=np.float32)
        self.post[:, 0] = 1.0
        self.alive = np.ones((N_COLS, N_HYPS), dtype=np.float32)
        self.stable = np.zeros(N_COLS, dtype=int)
        self.done = np.zeros(N_COLS, dtype=bool)
        self.top = np.zeros(N_COLS, dtype=int)

    def step(self, ev):
        cols = [c for c in range(N_COLS) if not self.done[c]]
        if not cols:
            return
        post, h = self.eng.step(ev[cols], self.post[cols], self.alive[cols],
                                self.h[cols])
        self.post[cols] = post
        self.h[cols] = h
        self.alive[cols] = (post > 1e-3).astype(np.float32)
        for c in cols:
            if self.alive[c].sum() == 0:
                self.alive[c, int(self.post[c].argmax())] = 1.0
            self.top[c] = int(self.post[c].argmax())
            if self.post[c, self.top[c]] > 0.99:
                self.stable[c] += 1
                if self.stable[c] >= 5:
                    self.done[c] = True
            else:
                self.stable[c] = 0

    def pick_choices(self, rng):
        hyps = lab.all_hypotheses()
        choices = {}
        for col in range(N_COLS):
            if self.done[col]:
                continue
            alive = self.alive[col] > 0.5
            if alive.sum() == 0:
                alive[self.post[col].argmax()] = True
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
        return choices


def fine_tune(eng, buf, args):
    """Oracle-supervised CNN+GRU fine-tune on the replay buffer.

    buf: list of dicts {key, nonces (list of bytes), traces (list of f64)}

    CNN: HW classification on every captured trace (oracle labels).
    GRU: replay each episode's attack trajectory per column — feed the
    stored evidence sequence back through the GRU with the true hypothesis
    as target at every step (teacher-forced BPTT). This is the self-play:
    the integrator learns to accumulate evidence the way the board actually
    produces it.
    """
    hyps = lab.all_hypotheses()
    Xs, Ys = [], []
    for ep in buf:
        kb = np.frombuffer(ep['key'], np.uint8)[None]
        nb = np.frombuffer(b''.join(ep['nonces']), np.uint8).reshape(-1, 16)
        kb_rep = np.repeat(kb, len(nb), axis=0)
        Ys.append(lab.round1_sbox_hw(kb_rep, nb))             # (B,64)
        Xb = []
        for tr in ep['traces']:
            p = eng.preprocess(tr)
            if p is None:
                break
            Xb.append(p)
        if len(Xb) != len(ep['traces']):
            continue
        Xs.append(np.array(Xb, dtype=np.float32))
    if not Xs:
        return
    X = torch.tensor(np.concatenate(Xs), dtype=torch.float32)[:, None]
    Y = torch.tensor(np.concatenate(Ys), dtype=torch.int64)
    lossf = torch.nn.CrossEntropyLoss()
    opt = torch.optim.Adam(
        list(eng.cnn.parameters()) + list(eng.gru.parameters()) +
        list(eng.head.parameters()), lr=1e-4)
    eng.cnn.train()
    eng.gru.train()
    eng.head.train()

    # precompute per-trace evidence for GRU targets (teacher forcing)
    ev_batches, th_batches = [], []
    for ep in buf:
        bits = np.unpackbits(np.frombuffer(ep['key'], np.uint8),
                             bitorder='little')
        th = np.array([int((bits[c] << 1) | bits[64 + c])
                       for c in range(N_COLS)])
        evs = []
        for nonce_b, tr in zip(ep['nonces'], ep['traces']):
            p = eng.preprocess(tr)
            if p is None:
                continue
            with torch.no_grad():
                logits = eng.cnn(torch.tensor(p[None, None],
                                              dtype=torch.float32))
                lp = torch.log_softmax(logits, dim=-1)[0]
            nb = np.frombuffer(nonce_b, np.uint8)[None]
            ev = np.full((N_COLS, N_HYPS), -1e3, dtype=np.float32)
            for c in range(N_COLS):
                pred = lab.hypothesis_labels(c, nb, hyps)[0]
                for h, v in enumerate(pred):
                    v = int(v)
                    if v in range(N_CLASSES):
                        ev[c, h] = lp[c, v].item()
            evs.append(ev)
        if len(evs) == len(ep['nonces']):
            ev_batches.append(np.array(evs, dtype=np.float32))  # (B,64,4)
            th_batches.append(np.tile(th, (len(evs), 1)))       # (B,64)

    for _ in range(args.lt_epochs):
        # CNN loss
        logits = eng.cnn(X)                                    # (B,64,6)
        loss = 0.0
        for c in range(N_COLS):
            loss = loss + lossf(logits[:, c], Y[:, c])
        # GRU loss: replay each episode's trajectory, all columns in parallel
        for ev_b, th_b in zip(ev_batches, th_batches):
            T = len(ev_b)
            h = torch.zeros(T, eng.gru_hidden)
            for t in range(T):
                if t == 0:
                    prev = torch.zeros(T, N_HYPS)
                    alive = torch.ones(T, N_HYPS)
                else:
                    prev = post.detach()
                    alive = (post.detach() > 1e-3).float()
                ev_t = torch.tensor(ev_b[:, t], dtype=torch.float32)
                x = torch.cat([ev_t, prev, alive], dim=-1)
                h = eng.gru(x, h)
                post = torch.softmax(eng.head(h), dim=-1)
                loss = loss + lossf(post, torch.tensor(th_b[:, t],
                                                       dtype=torch.int64))
        opt.zero_grad()
        loss.backward()
        opt.step()
    eng.cnn.eval()
    eng.gru.eval()
    eng.head.eval()
    print(f'    [ft] CNN+GRU loss {loss.item():.3f} on {len(X)} traces, '
          f'{sum(len(e) for e in ev_batches)} trajectory steps')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model', required=True, help='joint CNN+GRU *.pt')
    ap.add_argument('--npz', required=True)
    ap.add_argument('--out', default=None,
                    help='output checkpoint (default <model>_live.pt)')
    ap.add_argument('--episodes', type=int, default=50)
    ap.add_argument('--max-queries', type=int, default=60,
                    help='query budget per episode')
    ap.add_argument('--train-every', type=int, default=5,
                    help='fine-tune once per N episodes')
    ap.add_argument('--lt-epochs', type=int, default=2)
    ap.add_argument('--M', type=int, default=1,
                    help='traces per query averaged (live: 1 = fast capture)')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--gain', type=int, default=25)
    ap.add_argument('--sim', action='store_true')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset',
                                                     'husky_g25.h5'))
    ap.add_argument('--sim-amp', type=float, default=1.0)
    ap.add_argument('--sim-flat', type=float, default=0.0)
    ap.add_argument('--sim-target', default='sbox64')
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon',
                                         'ascon_cw305_top.bit'))
    args = ap.parse_args()

    from adaptive_gru import GRUEngine
    eng = GRUEngine(args.model, args.npz)
    out = args.out or (args.model[:-3] + '_live.pt')
    print(f'[+] engine: window {eng.window}, hidden {eng.gru_hidden}')
    print(f'[+] {args.episodes} episodes x <= {args.max_queries} queries, '
          f'ft every {args.train_every}, out {out}')

    rng = np.random.default_rng(args.seed)
    if args.sim:
        from sim_board import SimBoard
        lq = None
        print('[!] SIM MODE: SimBoard per episode (no hardware)')
    else:
        import live_query
        lq = live_query.LiveQuery(args.bitstream, os.urandom(16),
                                  gain=args.gain)

    buf = []
    stats = {'cracked_64': 0, 'best_match': 0.0, 'q_sum': 0, 'n_ep': 0}
    t0 = time.time()
    for ep in range(1, args.episodes + 1):
        key = os.urandom(16)
        if args.sim:
            from sim_board import SimBoard
            lq = SimBoard(args.sim_h5, key, column=0, amp=args.sim_amp,
                          seed=args.seed + ep, flat_p=args.sim_flat,
                          target=args.sim_target)
        else:
            lq.set_key(key)
        loop = GRULoop(eng)
        ep_nonces, ep_traces = [], []
        for q in range(1, args.max_queries + 1):
            choices = loop.pick_choices(rng)
            nonce = pack_nonce(choices, rng)
            pool = []
            while len(pool) < args.M:
                trace, _ct = lq.query(nonce)
                if trace is None:
                    continue
                pool.append(trace)
            trace = np.mean(pool, axis=0)
            ep_nonces.append(bytes(nonce))
            ep_traces.append(trace)
            ev = eng.evidence_all(trace, nonce)
            if ev is None:
                continue
            loop.step(ev)
            if loop.done.all():
                break
        if args.sim:
            lq.close()
        # oracle labels from the KNOWN key
        bits = np.unpackbits(np.frombuffer(key, np.uint8), bitorder='little')
        truth = np.array([int((bits[c] << 1) | bits[64 + c])
                          for c in range(N_COLS)])
        correct = int((loop.top == truth)[loop.done].sum()) if \
            loop.done.any() else 0
        n_done = int(loop.done.sum())
        match = 100.0 * (1 - np.count_nonzero(
            [int(loop.top[c]) != int(truth[c]) for c in range(N_COLS)]) /
            N_COLS)
        stats['n_ep'] += 1
        stats['q_sum'] += q
        stats['best_match'] = max(stats['best_match'], match)
        if n_done == N_COLS:
            stats['cracked_64'] += 1
        print(f'  ep {ep:3d}  key {key.hex()[:8]}…  q {q:3d}  '
              f'done {n_done:2d}/64  bit-match {match:5.1f}%', flush=True)
        buf.append({'key': key, 'nonces': ep_nonces, 'traces': ep_traces})
        if len(buf) > 16:
            buf.pop(0)
        if ep % args.train_every == 0:
            fine_tune(eng, buf, args)

    if lq is not None:
        try:
            lq.close()
        except Exception:
            pass

    # save the live-trained model
    state = {'arch': 'joint_gru', 'window': eng.window,
             'state_dict': eng.cnn.state_dict(),
             'gru_state_dict': eng.gru.state_dict(),
             'head_state_dict': eng.head.state_dict(),
             'gru_hidden': eng.gru_hidden,
             'best_val_acc': 0.0, 'seed': args.seed,
             'target': 'sbox', 'joint': True}
    torch.save(state, out)
    print(f'[+] wrote {out}')
    print(f'[+] {stats["cracked_64"]}/{stats["n_ep"]} episodes cracked all 64, '
          f'best bit-match {stats["best_match"]:.1f}%, '
          f'avg q {stats["q_sum"]/max(stats["n_ep"],1):.1f}')


if __name__ == '__main__':
    main()
