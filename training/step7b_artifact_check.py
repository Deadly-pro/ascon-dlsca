#!/usr/bin/env python3
r"""step7b_artifact_check.py — is the 8-samp/cyc signal crypto or key-write?

Step 7 showed |r| is systematically higher for 8 samples/cycle captures than
for 4 samples/cycle ones. But those captures are RANDOM-KEY, and our own
Sep-7 verdict (board_session/verdict_hwin_hd.md) proved that random-key
captures embed the KEY-WRITE BUS leak (sum-of-key-byte-HW, |r|~0.60), which
masquerades as crypto leakage in exactly this way.

Decisive checks:
  1. Compare |r|(sbox-HW) against |r|(sum-of-key-byte-HW) — the artifact
     signature. If the artifact dominates, the crypto |r| is an echo.
  2. Locate the argmax sample per column. If peaks cluster at the trace
     START (the key/nonce register-write region) it is the load artifact,
     not the crypto round.
  3. Null uses the SAME n as the real correlation (step 7 used fewer).
"""
import glob
import json
import os
import sys

import h5py
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from step1_cpa_hd import col_bits, sbox5   # noqa: E402
from labels import load_state              # noqa: E402

_PC = np.array([bin(v).count('1') for v in range(256)], dtype=np.float64)


def col_hw(keys, nonces, c):
    S = load_state(keys, nonces)
    S[:, 2] ^= np.uint64(0xF0)
    cols = sbox5(col_bits(S, c))
    return np.array([bin(int(v)).count('1') for v in cols], dtype=np.float64)


def key_bytesum(keys):
    return _PC[keys].sum(axis=1)


def corr_profile(traces, pred):
    n = traces.shape[0]
    t = traces.astype(np.float64)
    t -= t.mean(axis=0, keepdims=True)
    v = pred.astype(np.float64)
    v -= v.mean()
    ts = t.std(axis=0)
    ts[ts < 1e-12] = np.inf
    return np.abs((t * v[:, None]).sum(axis=0) / (n * ts * max(v.std(), 1e-12)))


def main():
    files = sorted(glob.glob('board_session/run_pa_*/cfg_g35_*.h5'))
    out = []
    for f in files:
        with h5py.File(f, 'r') as h:
            a = dict(h.attrs)
            tr = h['traces'][:].astype(np.float64)
            keys, nonces = h['keys'][:], h['nonces'][:]
        n = len(tr)
        spc = a.get('fs_hz', 40e6) / max(a.get('crypto_clk_hz', 1), 1)
        rng = np.random.default_rng(0)

        # key-write artifact signature
        kb = key_bytesum(keys)
        r_kb = corr_profile(tr, kb)
        pk_kb = int(r_kb.argmax())

        # crypto target
        rs = np.zeros(64)
        peaks = np.zeros(64, dtype=int)
        for c in range(64):
            rp = corr_profile(tr, col_hw(keys, nonces, c))
            rs[c] = rp.max()
            peaks[c] = int(rp.argmax())

        # null with the SAME n
        perm = rng.permutation(n)
        r_null = corr_profile(tr, kb[perm]).max()
        nulls = [corr_profile(tr, col_hw(keys, nonces, 0)[rng.permutation(n)]).max()
                 for _ in range(10)]
        null_p = float(np.quantile(nulls, 0.9))

        top = np.argsort(-rs)[:5]
        rec = dict(file=os.path.basename(f), n=n, key_mode=a.get('key_mode'),
                   samp_per_cyc=round(float(spc), 1), gain=a.get('gain_db'),
                   r_kb_max=float(r_kb.max()), r_kb_peak_sample=pk_kb,
                   r_crypto_max=float(rs.max()), null_same_n=null_p,
                   n_cols_above_null=int((rs > null_p).sum()),
                   top_cols=top.tolist(), top_peaks=[int(peaks[c]) for c in top],
                   peak_median=int(np.median(peaks)))
        out.append(rec)
        print(f"{rec['file']:26s} {rec['samp_per_cyc']:.0f}s/cyc "
              f"key_mode={rec['key_mode']}")
        print(f"   KEY-WRITE |r| max {rec['r_kb_max']:.4f} @sample {pk_kb}"
              f"   |   CRYPTO |r| max {rec['r_crypto_max']:.4f}"
              f"   null(same n) {rec['null_same_n']:.4f}"
              f"   above-null {rec['n_cols_above_null']}/64")
        print(f"   top-5 col peaks: {rec['top_peaks']}  "
              f"(median peak {rec['peak_median']} of {tr.shape[1]})", flush=True)
    os.makedirs('results', exist_ok=True)
    with open('results/step7b_artifact.json', 'w') as fh:
        json.dump(out, fh, indent=1, default=lambda o: float(o))
    print('-> results/step7b_artifact.json')


if __name__ == '__main__':
    main()
