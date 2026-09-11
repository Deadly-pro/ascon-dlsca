#!/usr/bin/env python3
r"""s1_multikey_validate.py — is the col-0 convergence genuine, or trap-2?

Trap 2 (prior-only profile + separating-nonce picker) yields a CONFIDENT WRONG
answer that is a FUNCTION OF THE PROFILE, not the key: the same hypothesis
every time, regardless of which key the board is running. Genuine extraction
tracks each key's own true hypothesis.

Protocol: one profile, N different keys, fixed query budget each, using the
EXACT scoring path of adaptive.attack_column (score_trace over the profile's
log-probs, separating-nonce selection).

Verdict rule:
  * same hypothesis for every key AND wrong for most  -> TRAP-2, no extraction
  * top hyp matches each key's true hyp for >=75%     -> genuine, S2 justified
  * anything else                                     -> inconclusive

Context: the 64-column fine-tune used a FIXED key, which collapses the label
support (col 0 realized only {2:47, 3:32, 4:21} of 6 classes) — this profile
is structurally suspect, and this test is what decides whether it recovered
anything real.

Usage:
  .venv/bin/python training/s1_multikey_validate.py \
      --model board_session/pa_assets/models/c0_liveft.pt --column 0 --queries 20
"""
import argparse
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import labels as lab                                        # noqa: E402
from adaptive import (Profile, make_lq, pick_separating_nonce,  # noqa: E402
                      score_trace)


def true_hyp(key, col):
    w1 = int.from_bytes(key[0:8], 'big')
    w2 = int.from_bytes(key[8:16], 'big')
    return ((w1 >> col) & 1) << 1 | ((w2 >> col) & 1)


def run_key(prof, lq, col, key, queries, seed):
    """Run `queries` adaptive queries for one key; return (top, post, n)."""
    lq.t.loadEncryptionKey(key)
    lq.key = key
    rng = np.random.default_rng(seed)
    log_acc = np.zeros(4)
    post = np.full(4, 0.25)
    n_ok = 0
    for _ in range(queries):
        nonce = pick_separating_nonce(col, prof.support, rng, post=post)
        trace = None
        for _ in range(6):                       # trigger-race retries
            trace, _ct = lq.query(nonce)
            if trace is not None:
                break
        if trace is None:
            continue
        x = prof.preprocess(trace)
        if x is None:
            continue
        logp_row = prof.log_probs(x[None])[0]
        sc = score_trace(logp_row, nonce, col, prof.classes)
        log_acc += np.where(np.isfinite(sc), sc, -1e3)
        post = np.exp(log_acc - log_acc.max())
        post /= post.sum()
        n_ok += 1
    return int(post.argmax()), float(post.max()), n_ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model', required=True)
    ap.add_argument('--npz', default='board_session/pa_assets/profiling.npz')
    ap.add_argument('--column', type=int, default=0)
    ap.add_argument('--queries', type=int, default=20)
    ap.add_argument('--keys', nargs='*', default=None)
    ap.add_argument('--gain', type=int, default=50)
    ap.add_argument('--offset', type=int, default=700)
    ap.add_argument('--std-floor', type=float, default=0.001)
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon',
                                         'ascon_cw305_top.bit'))
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()

    keys = args.keys or [
        '0123456789abcdef0123456789abcdef',
        'a45f8bcdab3d569e1ee091e0d29f2ab7',
        '2b7e151628aed2a6abf7158809cf4f3c',
        'deadbeef00112233445566778899aabb',
    ]
    keys = [bytes.fromhex(k) for k in keys]
    col = args.column

    prof = Profile(args.model, args.npz)
    print(f'[+] profile {os.path.basename(args.model)} col {col} '
          f'support {prof.classes}')
    print(f'[+] {len(keys)} keys x {args.queries} queries, gain {args.gain}\n')

    lq = make_lq(args, col, keys[0])
    rows = []
    try:
        for key in keys:
            t0 = time.time()
            top, post, n_ok = run_key(prof, lq, col, key, args.queries,
                                      args.seed)
            th = true_hyp(key, col)
            rows.append((key.hex(), th, top, post))
            print(f'  key {key.hex()[:16]}..  true {th}  top {top} '
                  f'(post {post:.3f})  {"MATCH" if top == th else "WRONG"}  '
                  f'[{n_ok}/{args.queries} q, {time.time()-t0:.0f}s]',
                  flush=True)
    finally:
        lq.close()

    tops = [r[2] for r in rows]
    matches = sum(1 for r in rows if r[1] == r[2])
    n = len(rows)
    print('\n=== VERDICT ===')
    print(f'top hyps: {tops}   true hyps: {[r[1] for r in rows]}')
    print(f'correct: {matches}/{n}')
    if len(set(tops)) == 1 and matches <= n // 2:
        print('SAME hyp for every key and wrong for most => TRAP-2 '
              '(prior-driven). No extraction.')
    elif matches >= max(1, int(0.75 * n)):
        print('Tracks each key\'s true hyp => GENUINE extraction. '
              'S2 (full-key attempt) justified.')
    else:
        print('Mixed/scattered => inconclusive. Do not claim extraction.')


if __name__ == '__main__':
    main()
