#!/usr/bin/env python3
r"""agg_activity_scan.py — Priority 1a: is the single-column ceiling caused by
aggregate switching activity from the other 63 columns?

Hypothesis under test
---------------------
Every round, all 64 bit-lanes of the 5-word ASCON state switch at once.  The
*aggregate* switching (Hamming distance between consecutive round states,
summed over all 320 state bits) has a large dynamic range across nonces, so
even at low per-bit coupling efficiency it should produce a measurable
correlation with trace energy.  A single column contributes 5 of those 320
bits and swings over only 0..5, so its AC variance is tiny by comparison.

If the aggregate correlates strongly while every single column stayed at the
permutation null, that directly demonstrates the shape of the problem: the
measurement sees bulk activity, and cannot resolve one column inside it.

Predictors
----------
For each trace (key, nonce) we compute the true state trajectory with the
oracle's own algebra (training/labels.py, self-tested against ascon_ref.py)
and form, per round r, the 320-bit Hamming distance S_r -> S_{r+1}.
Round 1 (r=0) is the one the sbox target lives in.

Controls
--------
* nonce Hamming weight  — the nonce-load bus, a KNOWN-PRESENT artifact.
  Its peak tells us where bus activity sits in time.  If the aggregate
  peaks at the same samples as the nonce-HW control, the "aggregate" signal
  is the bus, not the crypto.
* key Hamming weight    — constant on a fixed-key capture, must be 0.
* shuffled predictor    — the permutation null, max-statistic corrected.

Usage
-----
  .venv/bin/python training/agg_activity_scan.py \
      --h5 board_session/sprint/A_fixedkey_K1_N2048_M64.h5
"""
import argparse
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from labels import load_state, permutation_round  # noqa: E402


def popcount64(a):
    """Elementwise popcount on a uint64 array (numpy 1.26 has no bitwise_count)."""
    m1 = np.uint64(0x5555555555555555)
    m2 = np.uint64(0x3333333333333333)
    m4 = np.uint64(0x0F0F0F0F0F0F0F0F)
    h01 = np.uint64(0x0101010101010101)
    a = a.astype(np.uint64, copy=True)
    a = a - ((a >> np.uint64(1)) & m1)
    a = (a & m2) + ((a >> np.uint64(2)) & m2)
    a = (a + (a >> np.uint64(4))) & m4
    return (a * h01) >> np.uint64(56)


def hd_total(A, B):
    """Total Hamming distance across all 5 words, per row: (N,5) -> (N,)."""
    return popcount64(A ^ B).sum(axis=1).astype(np.float64)


def round_hds(keys, nonces, n_rounds=12):
    """Round-by-round aggregate switching: (N, n_rounds).

    Column r of the result is the 320-bit HD between the state entering
    round r and the state leaving it.  Uses the same round function the
    label generators use (constant + chi + affine + linear diffusion).
    """
    S = load_state(keys, nonces)
    out = np.empty((len(keys), n_rounds), dtype=np.float64)
    for r in range(n_rounds):
        nxt = permutation_round(S.copy(), r)
        out[:, r] = hd_total(S, nxt)
        S = nxt
    return out


def zs(a):
    a = np.asarray(a, dtype=np.float64)
    s = a.std()
    return (a - a.mean()) / (s if s > 1e-12 else 1.0)


def boxcar(X, w):
    """Causal-free centred moving average over w samples, (N,T) -> (N,T)."""
    if w <= 1:
        return X
    k = np.ones(w, dtype=np.float64) / w
    return np.apply_along_axis(lambda r: np.convolve(r, k, mode='same'), 1, X)


def corr_map(P, X):
    """|corr| between each predictor column and each sample column.

    P: (N,R) predictors, X: (N,T) traces (will be z-scored per sample).
    Returns (R,T) of Pearson |r| computed on standardised columns.
    """
    Pz = (P - P.mean(0)) / np.where(P.std(0) > 0, P.std(0), 1.0)
    Xz = (X - X.mean(0)) / np.where(X.std(0) > 0, X.std(0), 1.0)
    n = len(X)
    return np.abs(Pz.T @ Xz) / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--h5', required=True)
    ap.add_argument('--n-perm', type=int, default=200)
    ap.add_argument('--max-traces', type=int, default=0,
                    help='subsample for speed (0 = all)')
    ap.add_argument('--rounds', type=int, default=12)
    ap.add_argument('--smooth', type=int, default=4,
                    help='cycle-length boxcar before correlating (0 = off)')
    args = ap.parse_args()

    import h5py
    with h5py.File(args.h5, 'r') as f:
        traces = f['traces'][:].astype(np.float64)
        keys = f['keys'][:] if 'keys' in f else None
        nonces = f['nonces'][:].astype(np.uint8)
        attrs = dict(f.attrs)

    if args.max_traces and len(traces) > args.max_traces:
        idx = np.linspace(0, len(traces) - 1, args.max_traces).astype(int)
        traces, nonces = traces[idx], nonces[idx]
        if keys is not None:
            keys = keys[idx]

    if keys is None:
        kb = np.frombuffer(bytes.fromhex(attrs.get('key', '')), dtype=np.uint8)
        keys = np.tile(kb, (len(traces), 1))

    N, T = traces.shape
    fs = attrs.get('fs_hz', 40e6)
    crypto = attrs.get('crypto_clk_hz', 10e6)
    M = attrs.get('avg_m', 1)
    print(f'[+] {os.path.basename(args.h5)}: N={N} T={T} M={M} '
          f'fs={fs/1e6:.0f}MS/s crypto={crypto/1e6:.1f}MHz '
          f'({fs/crypto:.1f} samp/cyc)  key={attrs.get("key_mode")}')

    # ---- predictors -------------------------------------------------------
    R = round_hds(keys, nonces, args.rounds)
    preds = {}
    for r in range(args.rounds):
        preds[f'round{r+1}_hd'] = R[:, r]
    preds['total_hd'] = R.sum(axis=1)

    # controls
    pc = np.array([bin(v).count('1') for v in range(256)], dtype=np.float64)
    preds['CTRL_nonce_hw'] = pc[nonces].sum(axis=1)
    preds['CTRL_key_hw'] = pc[keys].sum(axis=1)

    names = list(preds)
    P = np.column_stack([preds[n] for n in names])
    # drop degenerate (zero-variance) predictors
    keep = P.std(0) > 1e-9
    names = [n for n, k in zip(names, keep) if k]
    P = P[:, keep]

    X = boxcar(traces, args.smooth) if args.smooth > 1 else traces

    print(f'[+] predictors: {len(names)}  '
          f'(round HD range {R.min():.0f}..{R.max():.0f} of 320 bits, '
          f'std {R.std():.1f})')
    print(f'[+] smoothing: {args.smooth} samples '
          f'= {args.smooth/(fs/crypto):.2f} clock cycles')

    # ---- correlation map --------------------------------------------------
    C = corr_map(P, X)                          # (R_p, T)
    peak_val = C.max(axis=1)
    peak_smp = C.argmax(axis=1)

    # ---- permutation null for the max-over-(pred x sample) statistic ------
    rng = np.random.default_rng(0)
    nulls = np.empty(args.n_perm)
    for i in range(args.n_perm):
        Pn = P[rng.permutation(N)]
        nulls[i] = corr_map(Pn, X).max()
    nulls.sort()
    n999 = float(np.quantile(nulls, 0.999))

    print()
    print('[AGGREGATE ACTIVITY vs TRACE]   |r| at best sample')
    order = np.argsort(-peak_val)
    for i in order:
        tag = ''
        if names[i].startswith('CTRL_'):
            tag = '   <- control'
        print(f'  {names[i]:16s} max|r| {peak_val[i]:.4f}  '
              f'at sample {peak_smp[i]:5d} ({peak_smp[i]/fs*1e6:7.2f} us){tag}')
    print()
    print(f'  permutation null: mean {nulls.mean():.4f}  '
          f'p99.9 {n999:.4f}  max {nulls[-1]:.4f}')

    # ---- interpretation ---------------------------------------------------
    agg = [i for i, n in enumerate(names) if n.startswith('round') or n == 'total_hd']
    ctl = [i for i, n in enumerate(names) if n == 'CTRL_nonce_hw']
    best_agg = max(agg, key=lambda i: peak_val[i]) if agg else None
    print()
    if best_agg is not None:
        a_val, a_smp, a_name = peak_val[best_agg], peak_smp[best_agg], names[best_agg]
        sig = 'ABOVE' if a_val > n999 else 'AT'
        print(f'  best aggregate predictor: {a_name}  |r| {a_val:.4f} '
              f'at {a_smp/fs*1e6:.2f} us  -> {sig} null p99.9')
        if ctl:
            c_val, c_smp = peak_val[ctl[0]], peak_smp[ctl[0]]
            print(f'  nonce-HW control:         |r| {c_val:.4f} '
                  f'at {c_smp/fs*1e6:.2f} us')
            d = abs(int(a_smp) - int(c_smp))
            print(f'  separation from control peak: {d} samples '
                  f'({d/fs*1e6:.2f} us)')
            if d < 8:
                print('  -> aggregate and bus peaks COINCIDE: the aggregate '
                      'correlation is likely the nonce-load bus, not crypto.')
            else:
                print('  -> peaks are separated in time: the aggregate '
                      'correlation is not simply the bus.')
        if a_val > n999:
            print('  VERDICT: bulk switching activity IS measurable. A '
                  'single column contributes 5/320 bits, so this quantifies '
                  'what is seen (aggregate) vs not resolvable (one column).')
        else:
            print('  VERDICT: even the 320-bit aggregate does not clear the '
                  'null. The measurement point is insensitive to the crypto '
                  'switching itself, not merely to one column of it.')

    out = {
        'h5': os.path.basename(args.h5), 'N': N, 'T': T, 'M': int(M),
        'fs_hz': float(fs), 'crypto_clk_hz': float(crypto),
        'smoothed_samples': args.smooth,
        'predictors': [{
            'name': names[i], 'max_abs_r': float(peak_val[i]),
            'peak_sample': int(peak_smp[i]),
            'peak_time_us': float(peak_smp[i] / fs * 1e6),
        } for i in order],
        'null': {'mean': float(nulls.mean()), 'p999': n999,
                 'max': float(nulls[-1]), 'n_perm': args.n_perm},
    }
    dst = os.path.join(ROOT, 'results',
                       'agg_' + os.path.basename(args.h5).replace('.h5', '.json'))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f'\n-> {os.path.relpath(dst, ROOT)}')


if __name__ == '__main__':
    main()
