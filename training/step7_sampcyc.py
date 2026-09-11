#!/usr/bin/env python3
r"""step7_sampcyc.py — does more samples/cycle create extractable signal?

The repo's own thesis (results/conclusive_summary.md) says the 125-vs-4
samples/cycle gap explains every negative result. We can test that claim for
free: existing captures already exist at 4 samp/cyc (10 MHz crypto) and
8 samp/cyc (5 MHz crypto), both at 40 MS/s.

Metric (attack-relevant, not 6-class accuracy):
  for each column c, CPA |r| between the trace and HW(round-1 S-box col c),
  maximised over samples, plus a permutation null (shuffled nonce order).
  Report: mean/max |r|, columns above the null p99.9, and the margin.

Usage:
  .venv/bin/python training/step7_sampcyc.py --glob 'board_session/run_pa_20260909_032325/cfg_*.h5'
"""
import argparse
import glob
import json
import os
import sys

import h5py
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from step1_cpa_hd import col_bits, sbox5, true_hyp  # noqa: E402
from labels import load_state                      # noqa: E402


def hw_all_cols(keys, nonces):
    """(N,64) true HW of the round-1 S-box output column (real key)."""
    S = load_state(keys, nonces)
    S[:, 2] ^= np.uint64(0xF0)
    out = np.empty((len(keys), 64))
    for c in range(64):
        cols = sbox5(col_bits(S, c))
        out[:, c] = np.array([bin(int(v)).count('1') for v in cols])
    return out


def cpa(traces, pred):
    n = traces.shape[0]
    t = traces.astype(np.float64)
    t -= t.mean(axis=0, keepdims=True)
    v = pred.astype(np.float64)
    v -= v.mean()
    ts = t.std(axis=0)
    ts[ts < 1e-12] = np.inf
    return np.abs((t * v[:, None]).sum(axis=0) / (n * ts * max(v.std(), 1e-12)))


def analyse(path, cols=16, n_null=20):
    with h5py.File(path, 'r') as f:
        a = dict(f.attrs)
        tr = f['traces'][:].astype(np.float64)
        keys, nonces = f['keys'][:], f['nonces'][:]
    n = len(tr)
    samp = a.get('fs_hz', 40e6) / max(a.get('crypto_clk_hz', 1), 1)
    hw = hw_all_cols(keys, nonces)
    rng = np.random.default_rng(0)
    # permutation null: shuffle the label assignment
    nulls = []
    for _ in range(n_null):
        perm = rng.permutation(n)
        nulls.append(cpa(tr[:400], hw[perm][:400, 0]).max())
    null_p = float(np.quantile(nulls, 0.999))

    rs = np.zeros(64)
    for c in range(64):
        rs[c] = cpa(tr, hw[:, c]).max()
    return dict(path=os.path.basename(path), n=n, samples=int(tr.shape[1]),
                samp_per_cyc=round(float(samp), 1),
                crypto_mhz=a.get('crypto_clk_hz', 0) / 1e6,
                gain=a.get('gain_db'), avg_m=a.get('avg_m', 1),
                r_mean=float(rs.mean()), r_max=float(rs.max()),
                null_p999=null_p,
                cols_above_null=int((rs > null_p).sum()),
                r_top4=sorted(rs.round(4), reverse=True)[:4])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--glob', required=True)
    ap.add_argument('--out', default='results/step7_sampcyc.json')
    args = ap.parse_args()
    files = sorted(glob.glob(args.glob))
    if not files:
        sys.exit(f'no files match {args.glob}')
    res = []
    for f in files:
        try:
            r = analyse(f)
            res.append(r)
            margin = r['r_max'] / r['null_p999']
            print(f"{r['path']:28s} {r['n']:4d}tr {r['samp_per_cyc']:.0f}s/cyc "
                  f"g{r['gain']}  |r| max {r['r_max']:.4f}  null {r['null_p999']:.4f}"
                  f"  ratio {margin:.2f}  above-null {r['cols_above_null']}/64"
                  f"  top {r['r_top4']}", flush=True)
        except Exception as e:
            print(f'{f}: ERR {str(e)[:70]}')
    os.makedirs('results', exist_ok=True)
    with open(args.out, 'w') as fh:
        json.dump(res, fh, indent=1, default=lambda o: float(o))
    print(f'-> {args.out}')


if __name__ == '__main__':
    main()
