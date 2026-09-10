#!/usr/bin/env python3
r"""step1b_null_floor.py — verify the CPA result is real leakage, not floor.

Three checks on the step1 result (all 64/64 columns rank-1, |r|~0.045):
 1. NULL FLOOR: max |r| of PERMUTED predictions (destroys trace<->label
    link, keeps marginal distributions) over the same 1200 samples.
    Observed |r| must sit above the null 99.9th percentile.
 2. PEAK CONCENTRATION: the argmax sample per column should cluster at the
    same clock cycle(s) (round-1 S-box) — random artifacts scatter.
 3. HELD-OUT SPLIT: find the peak sample on half A, then score hypotheses
    using ONLY that single sample on half B. If rank-1 survives on B, the
    attack generalizes to a fresh capture (new key) without retraining.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from labels import load_state  # noqa: E402
from step1_cpa_hd import col_bits, sbox5, true_hyp, cpa_scores  # noqa: E402


def hw_pred_for(keys, nonces, c):
    """(N, 4) predicted round-1 S-box output HW per hypothesis h."""
    n = len(keys)
    out = np.empty((n, 4))
    for h in range(4):
        b0, b1 = (h >> 1) & 1, h & 1
        kk = keys.copy()
        m = np.uint8(1 << (c % 8))
        if b0:
            kk[:, c % 8] |= m
        else:
            kk[:, c % 8] &= np.uint8(255 - int(m))
        if b1:
            kk[:, 8 + c % 8] |= m
        else:
            kk[:, 8 + c % 8] &= np.uint8(255 - int(m))
        S = load_state(kk, nonces)
        S[:, 2] ^= np.uint64(0xF0)
        cols = sbox5(col_bits(S, c))              # (N,) 5-bit output column
        out[:, h] = np.array([bin(int(v)).count('1') for v in cols])
    return out


def main():
    d = np.load('board_session/pa_assets/profiling.npz', allow_pickle=True)
    traces, keys, nonces = d['traces'], d['keys'], d['nonces']
    n, ns = traces.shape
    half = n // 2
    A, B = slice(0, half), slice(half, None)
    rng = np.random.default_rng(0)
    res = {'n': n, 'null_max_r': [], 'peak_samples': [], 'heldout': []}

    # --- 1. null floor: permuted predictions, column 0, 30 perms
    p0 = hw_pred_for(keys, nonces, 0)[:, 0]
    for _ in range(30):
        perm = rng.permutation(n)
        r = cpa_scores(traces, p0[perm])
        res['null_max_r'].append(float(r.max()))
    null_arr = np.array(res['null_max_r'])
    res['null_p999'] = float(np.quantile(null_arr, 0.999))
    res['null_mean'] = float(null_arr.mean())

    # --- 2 + 3. per column: peak sample (half A), held-out score (half B)
    rank_b = []
    for c in range(64):
        p = hw_pred_for(keys, nonces, c)          # (N,4)
        th = true_hyp(keys, c)                    # (N,)
        # peak sample from half A using per-trace true hyp
        predA_true = p[np.arange(0, half), th[:half]]
        rA = cpa_scores(traces[:half], predA_true)
        pk = int(rA.argmax())
        res['peak_samples'].append(pk)
        # held-out: score all 4 hyps on half B at sample pk ONLY
        tb = traces[B, pk].astype(np.float64)
        tb -= tb.mean()
        tstd = tb.std()
        sc = np.empty(4)
        for h in range(4):
            v = p[B, h].astype(np.float64)
            v -= v.mean()
            sc[h] = abs((tb @ v) / (tstd * v.std() * half)) if v.std() > 1e-12 else 0
        # rank of true hyp on B (per-trace truth -> use majority)
        maj = int(np.bincount(th[B], minlength=4).argmax())
        rank_b.append(int((sc > sc[maj]).sum()) + 1)
        res['heldout'].append({'c': c, 'peak': pk, 'rank_B': rank_b[-1],
                               'r': sc.round(4).tolist()})

    pk_arr = np.array(res['peak_samples'])
    res['peak_sample_median'] = int(np.median(pk_arr))
    res['peak_iqr'] = [int(np.percentile(pk_arr, 25)),
                       int(np.percentile(pk_arr, 75))]
    res['heldout_rank1'] = int((np.array(rank_b) == 1).sum())
    res['heldout_rank_le2'] = int((np.array(rank_b) <= 2).sum())

    os.makedirs('results', exist_ok=True)
    with open('results/step1b_null_floor.json', 'w') as f:
        json.dump(res, f, indent=1)
    print('=== STEP 1b: NULL FLOOR & HELD-OUT VERIFICATION ===')
    print(f"null max|r| (30 perms, col 0): mean {res['null_mean']:.4f}  "
          f"p99.9 {res['null_p999']:.4f}")
    obs = json.load(open('results/step1_cpa_hd.json'))
    print(f"observed best |r|: mean {obs['hw_best_r_mean']:.4f}  "
          f"max {obs['hw_best_r_max']:.4f}  -> "
          f"{'ABOVE' if obs['hw_best_r_mean'] > res['null_p999'] else 'AT/BELOW'} null p99.9")
    print(f"peak sample: median {res['peak_sample_median']}, "
          f"IQR {res['peak_iqr']} (of 1200)")
    print(f"held-out rank-1 on half B: {res['heldout_rank1']}/64, "
          f"rank<=2: {res['heldout_rank_le2']}/64")
    print('-> results/step1b_null_floor.json')


if __name__ == '__main__':
    main()
