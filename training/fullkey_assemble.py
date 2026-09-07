#!/usr/bin/env python3
r"""fullkey_assemble.py — assemble the full 128-bit ASCON key from per-column
S-box hypothesis scores, with bounded brute-force over weak columns and
verification against a known-plaintext oracle.

Method (the "broken key" assembly step of the profiled SCA attack):
  * Round-1 S-box input column c depends on 2 UNKNOWN KEY bits (word1[c],
    word2[c]) plus public nonce bits. Each column therefore has 4 key-bit
    hypotheses, scored by the per-column profile (adaptive.py / train_joint).
  * Strong columns: take the top-scoring hypothesis directly.
  * Weak columns: enumerate all 4^k combinations (k = number of weak columns,
    capped by --max-weak so 4^k stays computable).
  * Every assembled candidate is VERIFIED by encrypting a known
    (nonce, plaintext) pair and comparing tag/ct — the public-output oracle.
    ASCON-128's diffusion guarantees only the true key passes.

Input npz (per-column scores):
  scores : (64, 4) float — log-likelihood (or any score, higher=better)
           per hypothesis h = 2*b0 + b1 where the column's key bits are
           (word1[c]=b0, word2[c]=b1)
  nonce  : (16,) uint8 — a query nonce whose ct/tag the attacker knows
  ct_tag : (20,) uint8 — oracle output for that nonce (ct||tag)
  (or --key for a self-test with a known key)

Usage:
  .venv/bin/python training/fullkey_assemble.py --selftest
  .venv/bin/python training/fullkey_assemble.py --scores scores.npz
"""
import sys, os, argparse, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import ascon_ref as ar

AD = b'\x00' * 4
PT = b'\x00' * 4

def assemble(col_hyp):
    """col_hyp: {col: h in 0..3}. Returns 16-byte key."""
    w1 = 0
    w2 = 0
    for c in range(64):
        b0 = (col_hyp[c] >> 1) & 1   # word1 bit c
        b1 = col_hyp[c] & 1          # word2 bit c
        w1 |= b0 << c
        w2 |= b1 << c
    # S layout: word1 = K0 (key bytes 0..7), word2 = K1 (bytes 8..15)
    return ar.int_to_bytes(w1, 8) + ar.int_to_bytes(w2, 8)

def verify(key, nonce, ct_tag):
    out = ar.ascon_encrypt(bytes(key), bytes(nonce), AD, PT)
    return bytes(out) == bytes(ct_tag)

def recover(scores, nonce, ct_tag, max_weak=8, verbose=True):
    """scores: (64,4). Returns (key or None, n_verified, k_weak)."""
    scores = np.asarray(scores, dtype=float)
    top = scores.argmax(axis=1)
    # confidence margin per column (top1 - top2 score)
    srt = np.sort(scores, axis=1)
    margin = srt[:, -1] - srt[:, -2]
    order = np.argsort(margin)          # weakest first
    k = 0
    while 4 ** (k + 1) <= 4 ** max_weak and k < 64:
        k += 1
    # try increasing numbers of brute-forced weak columns
    n_verified = 0
    for kk in range(0, max_weak + 1):
        weak = list(order[:kk])
        strong = {c: int(top[c]) for c in range(64) if c not in weak}
        if verbose:
            print(f'  pass kk={kk}: brute-forcing {kk} weak cols '
                  f'({4**kk} combos), {64-kk} strong')
        for combo in itertools.product(range(4), repeat=kk):
            col_hyp = dict(strong)
            col_hyp.update({c: h for c, h in zip(weak, combo)})
            key = assemble(col_hyp)
            n_verified += 1
            if verify(key, nonce, ct_tag):
                return key, n_verified, kk
        # if even the strongest columns are wrong, more brute force of the
        # SAME wrong top-1s won't help; escalate anyway (margins may mislead)
    return None, n_verified, max_weak

def selftest(trials=30, seed=42, n_conf=56):
    """Simulate per-column posteriors: n_conf columns correct+confident, the
    rest weak/wrong — then assert full-key recovery within the budget."""
    rng = np.random.default_rng(seed)
    ok = 0
    worst = 0
    for t in range(trials):
        key = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        nonce = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        ct_tag = ar.ascon_encrypt(key, nonce, AD, PT)
        # true per-column hypotheses from the key
        w1 = int(ar.bytes_to_int(key[0:8]))
        w2 = int(ar.bytes_to_int(key[8:16]))
        scores = rng.normal(0, 1, (64, 4))
        cols = rng.permutation(64)
        for i, c_ in enumerate(cols):
            c = int(c_)
            true_h = (((w1 >> c) & 1) << 1) | ((w2 >> c) & 1)
            if i < n_conf:
                # confident + correct: big margin on the true hypothesis
                scores[c] = rng.normal(0, 0.1, 4)
                scores[c][true_h] += 10.0
            else:
                # weak: near-uniform, argmax may be wrong
                scores[c] = rng.normal(0, 0.3, 4)
        rk, nv, kk = recover(scores, nonce, ct_tag,
                             max_weak=min(12, 64 - n_conf),
                             verbose=False)
        if rk == key:
            ok += 1
            worst = max(worst, kk)
        else:
            print(f'  FAIL trial {t} (recovered '
                  f'{rk.hex() if rk else None})')
    print(f'fullkey assemble self-test: {ok}/{trials} keys recovered '
          f'(confident cols {n_conf}, worst weak-col brute {worst})')
    return ok == trials

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--scores', type=str,
                    help='npz with scores (64,4), nonce (16,), ct_tag (20,)')
    ap.add_argument('--max-weak', type=int, default=8)
    args = ap.parse_args()
    if args.selftest:
        sys.exit(0 if selftest() else 1)
    if not args.scores:
        ap.error('need --scores npz or --selftest')
    d = np.load(args.scores, allow_pickle=True)
    scores = d['scores']
    nonce = bytes(d['nonce'])
    ct_tag = bytes(d['ct_tag'])
    key, nv, kk = recover(scores, nonce, ct_tag, max_weak=args.max_weak)
    if key:
        print(f'\n  FULL KEY RECOVERED: {key.hex()}')
        print(f'  verified in {nv} oracle encryptions '
              f'({kk} weak columns brute-forced)')
    else:
        print('\n[!] not recovered within budget — per-column profiles too '
              'weak (need >= 64 - max_weak confident columns)')
        sys.exit(1)

if __name__ == '__main__':
    main()
