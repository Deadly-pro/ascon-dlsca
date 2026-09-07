#!/usr/bin/env python3
r"""merge_scores.py — merge FI-recovered columns into PA per-column scores
for fullkey_assemble (the mixed-assembly multiplier).

FI columns (exact key bits from localize_fault + DFA) are written as
infinitely confident scores: +BIG for the true hypothesis, -BIG for the
other three. PA columns keep their log-likelihood scores. The assembler's
margin logic then treats FI columns as certain and brute-forces only the
remainder.

Inputs:
  --pa    attack_scores.npz  (scores (64,4), nonce, ct_tag)   [optional]
  --fi    faults_bank.npz    (cols (N,), bits (N,) — localized fault
          (column, key-bit-pair) per fault; a column is FI-recovered when
          >=2 DISTINCT bits faulted there AND its DFA solve converged —
          pass --fi-solved solved.json {col: true_h} for exact control)
Output:
  --out   mixed_scores.npz   (scores, nonce, ct_tag) — same nonce/ct_tag
          as the PA npz (or --nonce/--ct-tag given directly).

Selftest: 20 PA-confident columns + 34 FI columns -> full key recovered.
"""
import sys, os, argparse, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import ascon_ref as ar
from fullkey_assemble import recover

AD = b'\x00' * 4
PT = b'\x00' * 4
BIG = 1e6


def merge(pa_scores, fi_solved):
    """pa_scores (64,4) or None; fi_solved {col: true_h}. Returns (64,4)."""
    if pa_scores is None:
        pa_scores = np.zeros((64, 4))
    out = np.array(pa_scores, dtype=float)
    for col, h in fi_solved.items():
        out[int(col)] = -BIG
        out[int(col), int(h)] = BIG
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pa', help='PA scores npz (scores/nonce/ct_tag)')
    ap.add_argument('--fi', help='faults bank npz (cols/bits)')
    ap.add_argument('--fi-solved', help='json {col: true_h} DFA-solved cols')
    ap.add_argument('--nonce', help='16B hex (if no --pa npz)')
    ap.add_argument('--ct-tag', help='20B hex (if no --pa npz)')
    ap.add_argument('--out', default='mixed_scores.npz')
    ap.add_argument('--max-weak', type=int, default=12)
    args = ap.parse_args()

    pa_scores = None
    nonce = ct_tag = None
    if args.pa:
        d = np.load(args.pa, allow_pickle=True)
        pa_scores = d['scores']
        nonce = bytes(d['nonce'])
        ct_tag = bytes(d['ct_tag'])
    if args.nonce:
        nonce = bytes.fromhex(args.nonce)
    if args.ct_tag:
        ct_tag = bytes.fromhex(args.ct_tag)

    fi_solved = {}
    if args.fi_solved:
        fi_solved = {int(k): int(v)
                     for k, v in json.load(open(args.fi_solved)).items()}
    elif args.fi:
        d = np.load(args.fi, allow_pickle=True)
        cols = d['cols']
        bits = d['bits']
        # a column counts as FI-recovered when >=2 DISTINCT flipped bits
        # were observed and localized there (the DFA solvability condition)
        from collections import defaultdict
        per_col = defaultdict(set)
        for c, b in zip(cols, bits):
            per_col[int(c)].add(int(b))
        for c, bs in per_col.items():
            if len(bs) >= 2:
                # true_h must come from the DFA solve; without it we can
                # still mark the column as FI-covered only via --fi-solved
                pass
        if not fi_solved:
            print('[!] --fi alone lacks DFA solutions; pass --fi-solved '
                  '{col: true_h} (from dfa_bitflip recover output)')
            sys.exit(1)

    if nonce is None or ct_tag is None:
        ap.error('need --pa npz or both --nonce and --ct-tag')

    merged = merge(pa_scores, fi_solved)
    np.savez(args.out, scores=merged,
             nonce=np.frombuffer(nonce, np.uint8),
             ct_tag=np.frombuffer(ct_tag, np.uint8))
    n_fi = len(fi_solved)
    print(f'[+] merged -> {args.out}  ({n_fi} FI cols certain, '
          f'{64 - n_fi} from PA/brute-force)')
    key, nv, kk = recover(merged, nonce, ct_tag, max_weak=args.max_weak)
    if key:
        print(f'  FULL KEY: {key.hex()}  ({nv} verifications, {kk} weak cols)')
    else:
        print('  [!] not recovered — insufficient confident columns '
              '(FI + PA confident < 52)')
        sys.exit(1)


def selftest():
    rng = np.random.default_rng(5)
    ok = 0
    trials = 5
    for _ in range(trials):
        key = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        nonce = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        ct_tag = ar.ascon_encrypt(key, nonce, AD, PT)
        w1 = int(ar.bytes_to_int(key[0:8]))
        w2 = int(ar.bytes_to_int(key[8:16]))
        # 38 FI-solved columns (exact), 18 confident PA, 8 weak (4^8 budget)
        cols = rng.permutation(64)
        fi = {}
        pa = rng.normal(0, 0.3, (64, 4))
        for i, c_ in enumerate(cols):
            c = int(c_)
            true_h = (((w1 >> c) & 1) << 1) | ((w2 >> c) & 1)
            if i < 38:
                fi[c] = true_h
            elif i < 56:
                pa[c] = rng.normal(0, 0.1, 4)
                pa[c][true_h] += 10.0
        merged = merge(pa, fi)
        rk, nv, kk = recover(merged, nonce, ct_tag, max_weak=8,
                             verbose=False)
        ok += (rk == key)
    print(f'merge_scores selftest: {ok}/{trials} full keys '
          f'(38 FI + 18 PA-confident + 8 brute)')
    return ok == trials


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        sys.exit(0 if selftest() else 1)
    main()
