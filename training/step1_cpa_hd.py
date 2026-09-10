#!/usr/bin/env python3
r"""step1_cpa_hd.py — Tier-1 metric check: does classical CPA see leakage?

Non-profiled correlation attack on the 5,000-trace profiling capture:
for every S-box column c (2 secret key bits), correlate each trace against
the HYPOTHESIZED intermediate value under all 4 key hypotheses.

Targets compared:
  hw   : HW of the round-1 S-box output column (static value, 6 classes)
  hd   : HD = HW(out_c XOR in_c) — register transition (what CMOS leaks)
  keyhw: HW of the 2 key bits themselves (k0_c + k1_c, 3 classes)

The column's round-1 S-box depends ONLY on bits c of key[0:8] / key[8:16]
plus public IV/nonce bits, so the predicted intermediate is exact given (h,
nonce). No model training, no hyperparameters — the result is a pure
measurement of whether first-order leakage exists above noise at this SNR.

Output: per-column best |r| and hypothesis rank for each target + summary.
Exit: writes results/step1_cpa_hd.json

Usage:
    .venv/bin/python training/step1_cpa_hd.py \
        --npz board_session/pa_assets/profiling.npz
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from labels import load_state, substitution_layer, _POPCOUNT  # noqa: E402


def col_bits(words, c):
    """(N,5) uint64 state words -> (N,) 5-bit column c as integer 0..31."""
    v = np.zeros(len(words), dtype=np.uint8)
    for i in range(5):
        v |= ((words[:, i] >> c) & 1).astype(np.uint8) << i
    return v


def sbox5(v):
    """Vectorized 5-bit full ASCON S-box on (N,) uint8 columns."""
    b0 = (v >> 0) & 1
    b1 = (v >> 1) & 1
    b2 = (v >> 2) & 1
    b3 = (v >> 3) & 1
    b4 = (v >> 4) & 1
    b0 ^= b4
    b4 ^= b3
    b2 ^= b1
    t0 = (~b0) & b1
    t1 = (~b1) & b2
    t2 = (~b2) & b3
    t3 = (~b3) & b4
    t4 = (~b4) & b0
    b0 ^= t1
    b1 ^= t2
    b2 ^= t3
    b3 ^= t4
    b4 ^= t0
    b1 ^= b0
    b0 ^= b4
    b3 ^= b2
    b2 ^= 1
    return b0 | (b1 << 1) | (b2 << 2) | (b3 << 3) | (b4 << 4)


def true_hyp(keys, c):
    """True hypothesis index per trace: h = 2*b0 + b1 (b0 = key[0:8] bit c,
    b1 = key[8:16] bit c — matches fullkey_assemble convention)."""
    w1 = (keys[:, 0].astype(np.uint64) << np.uint64(56))
    for i in range(1, 8):
        w1 |= keys[:, i].astype(np.uint64) << np.uint64(56 - 8 * i)
    w2 = (keys[:, 8].astype(np.uint64) << np.uint64(56))
    for i in range(1, 8):
        w2 |= keys[:, 8 + i].astype(np.uint64) << np.uint64(56 - 8 * i)
    b0 = ((w1 >> np.uint64(c)) & np.uint64(1)).astype(np.uint8)
    b1 = ((w2 >> np.uint64(c)) & np.uint64(1)).astype(np.uint8)
    return (b0 << 1) | b1


def cpa_scores(traces, pred):
    """Max |Pearson r| over samples between each trace set and prediction.

    traces: (N, S) float32; pred: (N,) float -> (S,) correlation per sample.
    """
    n = traces.shape[0]
    t = traces.astype(np.float64)
    t -= t.mean(axis=0, keepdims=True)
    v = pred.astype(np.float64)
    v -= v.mean()
    vt = v.std()
    if vt < 1e-12:
        return np.zeros(traces.shape[1])
    ts = t.std(axis=0)
    ts[ts < 1e-12] = np.inf
    return np.abs((t * v[:, None]).sum(axis=0) / (n * ts * vt))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--npz', default='board_session/pa_assets/profiling.npz')
    ap.add_argument('--out', default='results/step1_cpa_hd.json')
    args = ap.parse_args()

    d = np.load(args.npz, allow_pickle=True)
    traces, keys, nonces = d['traces'], d['keys'], d['nonces']
    n = len(traces)
    print(f'loaded {n} traces x {traces.shape[1]} samples')

    t0 = time.time()
    res = {'npz': args.npz, 'n_traces': int(n), 'columns': []}
    ranks = {'hw': [], 'hd': [], 'keyhw': []}
    best_r = {'hw': [], 'hd': [], 'keyhw': []}

    for c in range(64):
        th = true_hyp(keys, c)                      # (N,) true hypothesis
        # hypothesized states: try all 4 (b0, b1), predict intermediate
        pred = {t: np.empty((n, 4)) for t in ('hw', 'hd', 'keyhw')}
        for h in range(4):
            b0, b1 = (h >> 1) & 1, h & 1
            kk = keys.copy()
            # set bit c of key words 1 and 2 to the hypothesis
            kk[:, c % 8] &= np.uint8(255 - (1 << (c // 8)))
            kk[:, c % 8] |= np.uint8(b0 << (c // 8))
            kk[:, 8 + c % 8] &= np.uint8(255 - (1 << (c // 8)))
            kk[:, 8 + c % 8] |= np.uint8(b1 << (c // 8))
            S = load_state(kk, nonces)
            S[:, 2] ^= np.uint64(0xF0)
            in_v = col_bits(S, c)                   # (N,) 5-bit input col
            out_v = sbox5(in_v)                     # (N,) 5-bit output col
            pred['hw'][:, h] = _POPCOUNT[out_v]
            pred['hd'][:, h] = _POPCOUNT[out_v ^ in_v]
            pred['keyhw'][:, h] = b0 + b1

        col: dict = {'column': c, 'true_hyp_majority': int(np.bincount(th,
                     minlength=4).argmax())}
        for tgt in ('hw', 'hd', 'keyhw'):
            # score(h) = max |r| over samples for that hypothesis
            sc = np.array([cpa_scores(traces, pred[tgt][:, h]).max()
                           for h in range(4)])
            # rank of the TRUE hypothesis among the 4 scores:
            # true hyp index differs per trace, so aggregate: use the
            # majority true hyp of the column for ranking (random keys make
            # all 4 hyps ~equally represented, so this is well-defined)
            maj = int(np.bincount(th, minlength=4).argmax())
            rank = int((sc > sc[maj]).sum()) + 1     # 1 = best
            col[tgt] = {'r': sc.round(4).tolist(), 'rank': rank}
            ranks[tgt].append(rank)
            best_r[tgt].append(float(sc.max()))
        res['columns'].append(col)
        if c % 16 == 0:
            print(f'  col {c:2d} hd ranks so far: {ranks["hd"]}', flush=True)

    for tgt in ('hw', 'hd', 'keyhw'):
        rk = np.array(ranks[tgt])
        res[f'{tgt}_rank1'] = int((rk == 1).sum())
        res[f'{tgt}_rank_median'] = float(np.median(rk))
        res[f'{tgt}_best_r_mean'] = float(np.mean(best_r[tgt]))
        res[f'{tgt}_best_r_max'] = float(np.max(best_r[tgt]))
    res['elapsed_s'] = round(time.time() - t0, 1)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(res, f, indent=1)
    print(f"\n=== STEP 1 SUMMARY ({n} traces) ===")
    for tgt in ('hw', 'hd', 'keyhw'):
        print(f"{tgt:6s}: rank-1 on {res[tgt+'_rank1']}/64 columns  "
              f"median rank {res[tgt+'_rank_median']:.1f}  "
              f"best |r| mean {res[tgt+'_best_r_mean']:.3f} "
              f"max {res[tgt+'_best_r_max']:.3f}")
    print(f"-> {args.out}")


if __name__ == '__main__':
    main()
