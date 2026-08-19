#!/usr/bin/env python3
r"""adaptive.py — closed-loop adaptive chosen-plaintext key recovery (ACPPA).

Attacks ONE round-1 S-box column at a time (the only factorable target on this
masked core: exactly 2 key bits, 4 hypotheses). Uses a trained per-column HW
profile from train.py and drives the query->classify->posterior->select loop.

Selection heuristic (simple, no Bayesian experimental design):
  column c's S-box input bits that depend on the nonce are exactly
  nonce[0:8] bit c and nonce[8:16] bit c. Enumerate all 4 (n0,n1) combos,
  compute the 4 predicted HW classes (one per key hypothesis) for each, and
  pick the combo that SEPARATES the hypotheses most (most distinct classes).
  Random nonces mostly map all 4 hypotheses to the same class -> zero info;
  a separating nonce makes a single trace discriminate the key bits.

Offline validation (--validate, no board needed):
  Uses the held-out 20% split (same as train.py) of an existing random-key npz.
  Per trace: score the 4 hypotheses with the profile, compute the rank of the
  TRUE hypothesis, and the nonce's separation. Checks the premise of the whole
  approach: do high-separation nonces correlate with rank-1 true hypothesis,
  and are random nonces mostly uninformative?

Live attack (--attack, needs the board):
  Calls live_query.capture(nonce, key, ad) per query, feeds the trace through
  the profile, accumulates log-probabilities over hypotheses, converges when
  the top hypothesis's posterior clears a threshold for N consecutive queries,
  then VERIFIES the recovered key against ciphertext/tag.

Usage:
    # offline premise check (no hardware)
    python3 training/adaptive.py --validate \
        --npz training/data/main2.npz \
        --model training/models/main2_c1_sbox_cnn2.pt --column 1
    # live closed loop (board required)
    python3 training/adaptive.py --attack \
        --model training/models/main2_c1_sbox_cnn2.pt --column 1 \
        --key 000102030405060708090a0b0c0d0e0f --max-queries 500
    # virtual board (no hardware; noise model from a real capture)
    python3 training/adaptive.py --attack --sim \
        --npz training/data/main_unmasked_merged.npz \
        --model training/models/main_unmasked_merged_c0_sbox_cnn1.pt \
        --column 0 --key 000102030405060708090a0b0c0d0e0f --sim-amp 8.0
    # fine-tune a profile live on the board, then attack a fresh key:
    # see training/live_finetune.py
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import labels as lab
from train import CNN, MLP, load
from attack import build_input
from preprocess import align_trace, zscore


class Profile:
    """A trained per-column profile: model + reconstruction of its features."""

    def __init__(self, model_path, npz_path=None):
        ckpt = torch.load(model_path, map_location='cpu')
        self.arch = ckpt['arch']
        self.column = ckpt['column']
        self.window = ckpt['window']
        self.classes = list(ckpt['classes'])
        self.ymap = {c: i for i, c in enumerate(self.classes)}
        self.support = set(self.classes)
        self.target = ckpt.get('target', 'sbox')
        n_out = len(self.classes)
        if self.arch == 'cnn2':
            self.model = CNN(3, n_out, [8, 16, 32, 32], 128)
        elif self.arch == 'cnn1':
            self.model = CNN(1, n_out, [8, 16, 32], 128)
        else:
            mlp_in = ckpt['state_dict']['net.0.weight'].shape[1]
            self.model = MLP(mlp_in, ckpt['hidden'], n_out)
        self.model.load_state_dict(ckpt['state_dict'])
        self.model.eval()
        self.ref = None
        if npz_path:
            d = np.load(npz_path, allow_pickle=True)
            self.ref = d.get('ref')
            if self.ref is None:
                self.ref = d['traces'].mean(axis=0).astype(np.float32)

    def log_probs(self, traces):
        """(N,W) -> (N, n_classes) log-softmax over the model's class support."""
        with torch.no_grad():
            X = build_input(traces, self.arch, self.window, self.model)
            return torch.log_softmax(self.model(X), dim=1).numpy()

    def logits(self, traces):
        """(N,W) -> (N, n_classes) raw logits (pre-softmax, for calibration)."""
        with torch.no_grad():
            X = build_input(traces, self.arch, self.window, self.model)
            return self.model(X).numpy()

    def preprocess(self, trace):
        """One raw capture -> aligned+z-scored window (identical to profiling).

        Matches preprocess.py exactly: align the FULL trace against the stored
        reference, z-score the full trace, then crop to the model window.
        (Cropping before aligning/z-scoring would change the per-trace
        normalization and shift the live-trace feature distribution.)
        """
        if trace.size < self.window:
            return None
        t = trace.astype(np.float64)
        if self.ref is not None:
            t = align_trace(t, self.ref)
        t = zscore(t).astype(np.float32)
        return t[:self.window]


def separation(nonce16, column, model_support):
    """#distinct predicted HW classes across the 4 hypotheses for this nonce."""
    hyps = lab.all_hypotheses()
    pred = lab.hypothesis_labels(column, np.array([nonce16]), hyps)[0]
    return len({int(v) for v in pred if int(v) in model_support})


def pick_separating_nonce(column, model_support, rng=None, post=None):
    """Choose the 2 nonce bits (of column c) that separate the hypotheses best.

    Returns a 16-byte nonce. Other nonce bytes are random (they affect the
    trace but not this column's label). Ties broken by wider class spread.

    With `post` (current posterior over the 4 hypotheses) supplied, the pick
    becomes posterior-aware: only hypotheses that are still plausibly alive
    (posterior above ~1e-3) are required to separate. Once the loop has
    narrowed to a single survivor, that survivor is what must distinguish
    itself, so we choose a nonce where its predicted class differs from the
    (now-dead) alternatives — this sharpens elimination instead of wasting
    queries re-separating hypotheses that are already ruled out.
    """
    if rng is None:
        rng = np.random.default_rng()
    hyps = lab.all_hypotheses()
    best = None
    # Posterior-aware: de-weight hypotheses the loop has already eliminated.
    if post is not None:
        alive = post > 1e-3
        if alive.sum() == 0:
            alive[post.argmax()] = True
    else:
        alive = np.ones(len(hyps), dtype=bool)
    for n0 in (0, 1):
        for n1 in (0, 1):
            nonce = np.zeros(16, dtype=np.uint8)
            nonce[column // 8] |= np.uint8(n0 << (column % 8))
            nonce[8 + column // 8] |= np.uint8(n1 << (column % 8))
            pred = lab.hypothesis_labels(column, nonce[None], hyps)[0]
            # class-set and pairwise distinct-class count over ALIVE hyps only
            s = {int(v) for v in pred[alive] if int(v) in model_support}
            score = (len(s), sum(int(a) != int(b)
                                 for a in s for b in s if a != b))
            if best is None or score > best[0]:
                best = (score, nonce)
    nonce = best[1].copy()
    rest = rng.integers(0, 256, size=16, dtype=np.uint8)
    mask = np.zeros(16, dtype=np.uint8)
    mask[column // 8] |= 1 << (column % 8)
    mask[8 + column // 8] |= 1 << (column % 8)
    nonce = np.where(mask != 0, nonce, rest)
    return nonce


def score_trace(logp_row, nonce16, column, classes):
    """Per-hypothesis log-score for one trace: (4,) with -inf for impossible."""
    hyps = lab.all_hypotheses()
    pred = lab.hypothesis_labels(column, np.array([nonce16]), hyps)[0]
    scores = np.full(len(hyps), -np.inf)
    for h, v in enumerate(pred):
        v = int(v)
        if v in classes:
            scores[h] = logp_row[classes.index(v)]
    return scores


TEMP_GRID = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0]


def fit_lr(profile, npz_path):
    """Fit (temp, prior) for likelihood-ratio scoring on the profiling npz.

    temp  : temperature minimizing held-out NLL on the last 20% of traces
            (calibrates the profile's overconfidence at low SNR)
    prior : mean softmax posterior over those traces at temp — the model's
            class bias. LR scoring subtracts log prior so a hypothesis is
            rewarded only for *relative* evidence, killing the prior
            dominance that made ACPPA lock onto wrong bits.
    """
    d = np.load(npz_path, allow_pickle=True)
    X = d['traces']
    y = d['labels_sbox' if profile.target == 'sbox' else 'labels_kadd']
    y = y[:, profile.column]
    n = len(X)
    split = int(0.8 * n)                     # last 20% is held-out for fitting
    Xc, yc = X[split:], y[split:]
    valid = np.array([int(v) in profile.ymap for v in yc])
    L = profile.logits(Xc[valid])
    idx = np.array([profile.ymap[int(v)] for v in yc[valid]], dtype=np.int64)
    best_t, best_nll = 1.0, np.inf
    for T in TEMP_GRID:
        lp = L / T
        lp -= lp.max(axis=1, keepdims=True)
        lp -= np.log(np.exp(lp).sum(axis=1, keepdims=True))
        nll = -lp[np.arange(len(idx)), idx].mean()
        if nll < best_nll:
            best_nll, best_t = nll, T
    lp = L / best_t
    lp -= lp.max(axis=1, keepdims=True)
    prior = np.exp(lp)
    prior /= prior.sum(axis=1, keepdims=True)
    prior = prior.mean(axis=0)
    prior = np.maximum(prior, 1e-4)          # empty classes: clamp, not -inf
    prior /= prior.sum()
    return best_t, prior


def score_trace_logits(logits_row, prior, temp, nonce16, column, classes):
    """LR hypothesis score from raw logits: logits[c]/T - log prior[c].

    The logsumexp(logits/T) normalization is dropped deliberately: it is
    identical for every class, so it shifts all 4 hypothesis scores equally
    and cannot affect the posterior over hypotheses.
    """
    hyps = lab.all_hypotheses()
    pred = lab.hypothesis_labels(column, np.array([nonce16]), hyps)[0]
    scores = np.full(len(hyps), -np.inf)
    for h, v in enumerate(pred):
        v = int(v)
        if v in classes:
            i = classes.index(v)
            scores[h] = logits_row[i] / temp - np.log(prior[i])
    return scores


def best_nonce_bits(column):
    """(n0, n1) bit setting that separates the 4 hypotheses the most."""
    hyps = lab.all_hypotheses()
    best = None
    for n0 in (0, 1):
        for n1 in (0, 1):
            nonce = np.zeros(16, dtype=np.uint8)
            nonce[column // 8] |= np.uint8(n0 << (column % 8))
            nonce[8 + column // 8] |= np.uint8(n1 << (column % 8))
            pred = lab.hypothesis_labels(column, nonce[None], hyps)[0]
            s = len({int(v) for v in pred})
            if best is None or s > best[0]:
                best = (s, (n0, n1), pred)
    return best


def validate_offline(args):
    d = np.load(args.npz)
    traces, labels = d['traces'], d['labels_sbox']
    nonces = d['nonces']
    keys = d['keys']
    n = len(traces)
    col = args.column
    prof = Profile(args.model, args.npz)

    rng = np.random.default_rng(args.seed)
    idx = rng.permutation(n)
    ntr = int(0.8 * n)
    attack = idx[ntr:]
    print(f'validate col {col}: {len(attack)} held-out attack traces '
          f'({prof.arch}, support {prof.classes})')

    logp = prof.log_probs(traces[attack])
    kbit0 = ((keys[attack, col // 8] >> (col % 8)) & 1) * 1
    kbit1 = ((keys[attack, 8 + col // 8] >> (col % 8)) & 1) * 1
    hyps = lab.all_hypotheses()
    true = np.array([np.flatnonzero((hyps[:, 0] == a) & (hyps[:, 1] == b))[0]
                     for a, b in zip(kbit0, kbit1)])

    ranks = np.empty(len(attack), dtype=int)      # strict: count strictly-better
    ranks_tie = np.empty(len(attack), dtype=int)  # conservative: ties count against
    seps = np.empty(len(attack), dtype=int)
    for i, ti in enumerate(attack):
        sc = score_trace(logp[i], nonces[ti], col, prof.classes)
        ranks[i] = np.count_nonzero(sc > sc[true[i]]) + 1
        ranks_tie[i] = np.count_nonzero(sc >= sc[true[i]])
        seps[i] = separation(nonces[ti], col, prof.support)

    mean_rank = ranks_tie.mean()
    chance_rank = (len(hyps) + 1) / 2
    top1 = (ranks == 1).mean()
    top1_conservative = (ranks_tie == 1).mean()
    print(f'  per-trace true-hyp rank: mean {mean_rank:.2f} '
          f'(chance {chance_rank}), top-1 {top1*100:.1f} % '
          f'(ties-count-against {top1_conservative*100:.1f} %)')

    # model's own HW-class accuracy on the same traces (the raw signal)
    model_top1 = 0
    for i, ti in enumerate(attack):
        pred = lab.hypothesis_labels(col, nonces[ti][None], hyps)[0]
        true_cls = int(pred[true[i]])
        if true_cls in prof.classes and np.argmax(logp[i]) == prof.classes.index(true_cls):
            model_top1 += 1
    print(f'  model HW-class top-1 accuracy: {model_top1/len(attack)*100:.1f} % '
          f'(chance {100/len(prof.classes):.1f} %)')

    # collision structure: does the true hyp share its class with another hyp?
    n_collide = 0
    for i, ti in enumerate(attack):
        pred = lab.hypothesis_labels(col, nonces[ti][None], hyps)[0]
        v = int(pred[true[i]])
        others = [int(pred[h]) for h in range(4) if h != true[i]]
        if v in others:
            n_collide += 1
    print(f'  true hyp collides with another hyp (same class): '
          f'{n_collide/len(attack)*100:.1f} % of traces')

    # per-class reliability: how often is each class the model's argmax
    # and how often is it the TRUE class?
    print(f'  nonce separation distribution (random nonces):')
    for s in range(1, 5):
        sub = ranks_tie[seps == s]
        if len(sub):
            print(f'    sep={s}: {len(sub):4d} traces, mean rank {sub.mean():.2f}, '
                  f'top-1 {(sub == 1).mean()*100:.1f} %')
        else:
            print(f'    sep={s}: none')

    hi = seps >= 3
    if hi.sum():
        print(f'  high-sep (>=3) nonces: {hi.sum()} traces, '
              f'mean rank {ranks_tie[hi].mean():.2f}, '
              f'top-1 {(ranks_tie[hi] == 1).mean()*100:.1f} % '
              f'vs all {top1_conservative*100:.1f} %')

    # achievable separation for this column (adaptive selection's ceiling)
    _, (n0, n1), pred = best_nonce_bits(col)
    print(f'  best achievable separation: {len({int(v) for v in pred})} '
          f'(n0={n0}, n1={n1}, pred {[int(v) for v in pred]})')

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    os.makedirs(out, exist_ok=True)
    name = os.path.splitext(os.path.basename(args.npz))[0]
    path = os.path.join(out, f'{name}_c{col}_sbox_{prof.arch}_adaptive_validate.json')
    with open(path, 'w') as f:
        json.dump({'column': col, 'arch': prof.arch, 'n_attack': int(len(attack)),
                   'support': prof.classes, 'mean_rank': float(mean_rank),
                   'chance_rank': float(chance_rank), 'top1': float(top1),
                   'top1_conservative': float(top1_conservative),
                   'n_queries_rank1': int((ranks == 1).sum()),
                   'separation_dist': {int(s): int((seps == s).sum())
                                       for s in range(1, 5)}}, f, indent=2)
    print(f'  wrote {path}')


def make_lq(args, col, key):
    """Board or sim query engine for one column (SimBoard is per-column)."""
    if args.sim:
        from sim_board import SimBoard
        return SimBoard(args.sim_h5, key, column=col, amp=args.sim_amp,
                        seed=args.seed, flat_p=args.sim_flat)
    import live_query
    return live_query.LiveQuery(args.bitstream, key, gain=args.gain,
                                offset=args.offset, std_floor=args.std_floor)


def attack_column(prof, lq, col, args, rng, out_dir):
    """One column's adaptive loop. Returns (k0, k1) on convergence, else None.

    Phase 1+2: likelihood-ratio scoring (logits/T - log prior, prior from the
    profiling npz's held-out traces, refit every --refit-k queries from the
    loop's own captures) and --M trace averaging per query (nonce repetition:
    noise ~ iid, signal identical -> +10*log10(M) dB SNR).
    """
    hyps = lab.all_hypotheses()
    log_acc = np.full(len(hyps), 0.0)
    stable = 0
    temp, prior = 1.0, None
    if args.cal:
        temp, prior = fit_lr(prof, args.npz)
        p_ent = float(-(prior * np.log(np.maximum(prior, 1e-12))).sum())
        print(f'[+] LR calibration: temp {temp:.2f}, prior entropy {p_ent:.2f} '
              f'nats (uniform {np.log(len(prior)):.2f})')
    print(f'[+] adaptive attack col {col}, 4 hyps, profile {prof.arch} '
          f'(support {prof.classes}), M={args.M} traces/query, '
          f'scoring {"LR" if prior is not None else "posterior"}')
    session_posts = []
    t0 = time.time()
    n_captured = 0
    post = None
    # Scope state watchdog
    pool_fail_streak = 0
    for q in range(1, args.max_queries + 1):
        nonce = pick_separating_nonce(col, prof.support, rng, post=post)
        pool = []
        while len(pool) < args.M:
            trace, _ct = lq.query(nonce)
            if trace is None:            # trigger timeout — retry same nonce
                pool_fail_streak += 1
                if pool_fail_streak >= 25 and not args.sim:
                    print(f'[!] col {col}: {pool_fail_streak} consecutive bad '
                          f'captures — rebuilding scope connection')
                    samples = lq.scope.adc.samples
                    lq.scope.dis()
                    import chipwhisperer as cw
                    lq.scope = cw.scope()
                    lq.scope.gain.db = args.gain
                    lq.scope.adc.samples = samples
                    lq.scope.adc.offset = args.offset
                    lq.scope.clock.adc_src = 'clkgen_x4'
                    lq.scope.clock.clkgen_freq = 40e6
                    lq.scope.clock.reset_adc()
                    lq.scope.trigger.triggers = 'tio4'
                    pool_fail_streak = 0
                continue
            pool_fail_streak = 0
            if np.abs(trace).max() > args.clip_threshold:   # ADC rail — retry
                continue
            pool.append(trace)
        n_captured += 1
        trace = prof.preprocess(np.mean(pool, axis=0))
        if trace is None:
            continue
        if prior is not None:
            logits_row = prof.logits(trace[None])[0]
            sc = score_trace_logits(logits_row, prior, temp, nonce,
                                    col, prof.classes)
            p_c = np.exp(logits_row / temp)
            p_c /= p_c.sum()
            session_posts.append(p_c)
        else:
            logp_row = prof.log_probs(trace[None])[0]
            sc = score_trace(logp_row, nonce, col, prof.classes)
        log_acc += np.where(np.isfinite(sc), sc, -1e3)
        post = np.exp(log_acc - log_acc.max())
        post /= post.sum()
        top = int(post.argmax())
        stable = stable + 1 if post[top] > args.converge_p else 0
        if args.refit_k and prior is not None and n_captured % args.refit_k == 0 \
                and len(session_posts) >= args.refit_k:
            prior = 0.5 * prior + 0.5 * np.mean(session_posts, axis=0)
            prior = np.maximum(prior, 1e-4)
            prior /= prior.sum()
        if n_captured <= 5 or n_captured % 25 == 0 or stable >= args.stable_n:
            ent = float(-(post * np.log(np.maximum(post, 1e-12))).sum())
            print(f'  q {n_captured:4d}  top hyp {top}  post {post[top]:.3f}  '
                  f'ent {ent:.2f}  [{time.time()-t0:.0f}s]')
        if stable >= args.stable_n:
            k0, k1 = int(hyps[top, 0]), int(hyps[top, 1])
            print(f'[+] converged at query {n_captured}: hyp {top} '
                  f'(key bits k[{col}%8]={k0}, k[8+col%8]={k1})')
            os.makedirs(out_dir, exist_ok=True)
            path = os.path.join(out_dir, f'adaptive_c{col}_q{n_captured}.json')
            with open(path, 'w') as f:
                json.dump({'column': col, 'queries': n_captured, 'hyp': int(top),
                           'k0': k0, 'k1': k1,
                           'posterior': float(post[top]),
                           'seconds': float(time.time() - t0)}, f, indent=2)
            return k0, k1
    print(f'[!] col {col}: no convergence after {n_captured} queries — '
          f'top hyp {int(log_acc.argmax())}, posterior {post.max():.3f}')
    return None


def live_attack(args):
    col = args.column
    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('--key must be 16 bytes hex')
    prof = Profile(args.model, args.npz)
    print(f'[+] profile {prof.arch} window {prof.window} target {prof.target}')
    rng = np.random.default_rng(args.seed)
    lq = make_lq(args, col, key)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    try:
        attack_column(prof, lq, col, args, rng, out_dir)
    finally:
        lq.close()


def full_key_attack(args):
    """All 64 columns, assemble the 128 bits, verify the full key via ciphertext.

    Column c recovers bit c of key[0:8] (byte c//8, bit c%8) and bit c of
    key[8:16] (byte 8 + c//8, bit c%8) — see labels.hypothesis_labels.
    """
    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('--key must be 16 bytes hex')
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
    bits = np.zeros(128, dtype=np.uint8)
    failed = []
    rng = np.random.default_rng(args.seed)
    # One LiveQuery for the whole run (board path): per-column construction is
    # fragile (64 scope opens + FPGA re-programs can wedge the ADC clock) and
    # slow. SimBoard stays per-column (its column parameter selects the
    # leakage template).
    shared_lq = None if args.sim else make_lq(args, 0, key)
    try:
        for col in range(64):
            model = args.model_fmt.format(col=col)
            if not os.path.exists(model):
                sys.exit(f'[!] missing model for col {col}: {model}')
            prof = Profile(model, args.npz)
            lq = shared_lq if shared_lq is not None else make_lq(args, col, key)
            print(f'\n=== column {col}/63 ===')
            try:
                res = attack_column(prof, lq, col, args, rng, out_dir)
            finally:
                if shared_lq is None:
                    lq.close()
            if res is None:
                print(f'[!] col {col} did not converge — recording as failed, continuing')
                failed.append(col)
                continue
            k0, k1 = res
            bits[col] = k0
            bits[64 + col] = k1
    finally:
        if shared_lq is not None:
            shared_lq.close()
    candidate = bytes(np.packbits(bits, bitorder='little'))
    truth = np.unpackbits(np.frombuffer(key, dtype=np.uint8), bitorder='little')
    match = 100.0 * (1 - np.count_nonzero(bits != truth) / 128.0)
    print(f'\n[+] assembled key: {candidate.hex()}')
    print(f'    expected      : {key.hex()}')
    print(f'    bit match     : {match:.1f}%')
    if failed:
        print(f'[!] non-converged columns: {failed}')
    lq = make_lq(args, 0, key)
    try:
        ok, exp, got = lq.verify_key(candidate)
        print(f'    verify_key    : {"PASS" if ok else "FAIL"} '
              f'(oracle {exp[:24]}... fpga {got[:24]}...)')
    finally:
        lq.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--validate', action='store_true',
                    help='offline premise check on held-out npz (no board)')
    ap.add_argument('--attack', action='store_true',
                    help='live closed loop (board required)')
    ap.add_argument('--npz', default='training/data/main2.npz')
    ap.add_argument('--model', default=None)
    ap.add_argument('--column', type=int, default=1)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--key', default=None, help='16-byte target key hex (attack)')
    ap.add_argument('--max-queries', type=int, default=500)
    ap.add_argument('--converge-p', type=float, default=0.99)
    ap.add_argument('--stable-n', type=int, default=5)
    ap.add_argument('--bitstream',
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         '..', 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--gain', type=int, default=-2,
                    help='scope gain dB (must match the profiling capture)')
    ap.add_argument('--offset', type=int, default=700,
                    help='scope ADC offset (must match the profiling capture)')
    ap.add_argument('--std-floor', type=float, default=0.01,
                    help='reject flat live captures below this std')
    ap.add_argument('--clip-threshold', type=float, default=0.49,
                    help='reject live captures above this abs value (ADC rail)')
    ap.add_argument('--sim', action='store_true',
                    help='attack a virtual board (SimBoard) instead of the CW305')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset',
                                                     'main_unmasked_merged.h5'),
                    help='real unmasked capture used to fit the SimBoard noise model')
    ap.add_argument('--sim-amp', type=float, default=1.0,
                    help='leakage gain for the virtual board (1.0 = real SNR)')
    ap.add_argument('--sim-flat', type=float, default=0.0,
                    help='probability the virtual board returns a flat (trigger-race) capture')
    ap.add_argument('--M', type=int, default=1,
                    help='traces per query, averaged (nonce repetition: '
                         '+10*log10(M) dB SNR)')
    ap.add_argument('--cal', action='store_true',
                    help='enable likelihood-ratio scoring (logits/T - log prior); '
                         'default is plain posterior — LR dilutes the finetuned '
                         'profile (T~4) and is only useful for heavily prior-'
                         'biased models')
    ap.add_argument('--refit-k', type=int, default=25,
                    help='refit the LR prior every K scored queries from the '
                         "loop's own captures (0 disables online refinement)")
    ap.add_argument('--all-columns', action='store_true',
                    help='attack all 64 columns, assemble 128 bits, verify_key')
    ap.add_argument('--model-fmt', default=None,
                    help="per-column model path with {col}, e.g. "
                         "'training/models/main_unmasked_merged_c{col}_sbox_cnn1.pt'")
    args = ap.parse_args()

    if args.validate:
        if not args.model:
            sys.exit('--validate requires --model')
        validate_offline(args)
    elif args.attack:
        if not args.key:
            sys.exit('--attack requires --key <16-byte hex>')
        if args.all_columns:
            if not args.model_fmt:
                sys.exit("--all-columns requires --model-fmt 'path/c{col}_...pt'")
            full_key_attack(args)
        else:
            if not args.model:
                sys.exit('--attack requires --model (or use --all-columns '
                         'with --model-fmt)')
            live_attack(args)
    else:
        ap.error('choose --validate or --attack')


if __name__ == '__main__':
    main()
