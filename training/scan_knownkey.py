#!/usr/bin/env python3
r"""scan_knownkey.py — known-key CPA / per-bit DPA / regression scanner.

Purpose: on a FIXED-KEY capture we know every intermediate exactly, so there
is no hypothesis search — we correlate the trace against the TRUE value.
That is maximum sensitivity per trace, and it removes the random-key
key-write bus artifact (constant key => constant key-load => cancels).

Detection floor (calibrated: predicts 0.048 at N=5000, we measured 0.045):
        rho_min = 3.4 / sqrt(N_eff)
with N_eff = N_traces * M (M-averaging multiplies true r by sqrt(M) while
the null stays 3.4/sqrt(N)).  Permutation nulls are computed EMPIRICALLY
here so the reported floor needs no assumptions.

What it measures per column c (0..63):
  cpa_hw      : |r| trace vs HW(round-1 S-box output column c)
  dpa_bit_k   : |r| vs each of the 5 S-box OUTPUT bits (k=0..4) — HW assumes
                equal weight and equal sign per bit; opposite-sign
                transitions cancel inside HW, so single bits can be stronger
  in_bit_k    : |r| vs each of the 5 S-box INPUT bits (pre-affine state)
  reg_r       : multiple-correlation of the regression on those 5 out-bits
  peak        : argmax sample, and FWHM (smearing diagnostic)

Controls (both must behave, else the measurement chain is broken):
  POSITIVE control: nonce-load bus leak — nonce varies per trace, so its
      register-write activity correlates strongly.  If this does NOT show
      |r| >> null, the scanner/alignment is broken and crypto results are void.
  NEGATIVE control: key-load bus leak — key is fixed, so it must be ~0.
      A large value would mean the key is being rewritten per trace.

Usage:
  .venv/bin/python training/scan_knownkey.py --h5 board_session/sprint/A_fixedkey_K1_N2048_M64.h5
"""
import argparse
import json
import os
import sys
import time

import h5py
import numpy as np
from scipy import signal as sps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from labels import load_state, _POPCOUNT  # noqa: E402

IV = np.array([0x80, 0x40, 0x0C, 0x06, 0, 0, 0, 0], dtype=np.uint8)


# ---------------------------------------------------------------- intermediates
def round1_state(keys, nonces):
    """(N,5) uint64 state AFTER round-0 constant + affine1+chi+sbox pipeline
    inputs, i.e. the pre-affine1 state and the post-S-box state we need."""
    S = load_state(keys, nonces)
    Sin = S.copy()
    Sin[:, 2] ^= np.uint64(0xF0)          # round-0 constant applied
    return Sin


def sbox5_vec(v):
    """Vectorized 5-bit ASCON S-box on (N,) uint8 columns (== labels._sbox_col)."""
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


def col_bits(words, c):
    v = np.zeros(len(words), dtype=np.uint8)
    for i in range(5):
        v |= ((words[:, i] >> c) & 1).astype(np.uint8) << i
    return v


def intermediates(keys, nonces):
    """Returns (N,5,64) in_bits, (N,5,64) out_bits, (N,64) out_hw."""
    N = len(keys)
    Sin = round1_state(keys, nonces)
    in_bits = np.empty((N, 5, 64), dtype=np.uint8)
    out_bits = np.empty((N, 5, 64), dtype=np.uint8)
    out_hw = np.empty((N, 64), dtype=np.uint8)
    for c in range(64):
        v = col_bits(Sin, c)
        for k in range(5):
            in_bits[:, k, c] = (v >> k) & 1
        o = sbox5_vec(v)
        for k in range(5):
            out_bits[:, k, c] = (o >> k) & 1
        out_hw[:, c] = _POPCOUNT[o]
    return in_bits, out_bits, out_hw


# ---------------------------------------------------------------- stats
def maxabs_r(traces, pred):
    """(S,) |Pearson r| per sample between traces (N,S) and pred (N,)."""
    n = traces.shape[0]
    t = traces - traces.mean(axis=0, keepdims=True)
    v = pred.astype(np.float64)
    v = v - v.mean()
    vstd = v.std()
    if vstd < 1e-12:
        return np.zeros(traces.shape[1])
    ts = t.std(axis=0)
    ts = np.where(ts < 1e-12, np.inf, ts)
    return np.abs((t * v[:, None]).sum(axis=0) / (n * ts * vstd))


def perm_null(traces, pred, n_perm=200, rng=None):
    """Empirical null distribution of max|r| under label permutation."""
    rng = rng or np.random.default_rng(0)
    n = traces.shape[0]
    vals = np.empty(n_perm)
    for i in range(n_perm):
        vals[i] = maxabs_r(traces, pred[rng.permutation(n)]).max()
    return vals


def tstat_p(r, n):
    """Two-sided p-value for a Pearson r with n samples (t-test)."""
    from scipy import stats
    r = min(max(abs(r), 0.0), 1 - 1e-12)
    if n < 4:
        return 0.0, 1.0
    t = r * np.sqrt((n - 2) / (1 - r ** 2))
    return t, float(2 * stats.t.sf(abs(t), n - 2))


def perm_max_null(traces, preds, n_perm=300, rng=None):
    """Null distribution of the MAX-OVER-SAMPLES |r| statistic.

    The per-hypothesis test statistic is max_s |r_s|, and its null
    distribution must also be a max-over-samples. Using a per-sample t-test
    instead ignores the ~2000-sample selection and yields many false
    positives (the trap that produced the 57/64 artifact in step 1b).
    Evaluated on a few predictors so the null is not tied to one label.
    """
    rng = rng or np.random.default_rng(0)
    n = traces.shape[0]
    vals = []
    per = max(1, n_perm // max(1, len(preds)))
    for pred in preds:
        for _ in range(per):
            vals.append(maxabs_r(traces, pred[rng.permutation(n)]).max())
    return np.array(vals)


def perm_p(obs, null):
    """Permutation p-value: (1 + #{null >= obs}) / (1 + n_null)."""
    return float((1 + int((null >= obs).sum())) / (1 + len(null)))


def holm(pvals):
    """Holm-Bonferroni adjusted p-values."""
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    run = 0.0
    for rank, idx in enumerate(order):
        run = max(run, (m - rank) * p[idx])
        adj[idx] = min(run, 1.0)
    return adj


def fwhm(profile, peak):
    """Approx FWHM in samples around `peak` (smearing diagnostic)."""
    m = profile[peak] / 2.0
    left = peak
    while left > 0 and profile[left] > m:
        left -= 1
    right = peak
    while right < len(profile) - 1 and profile[right] > m:
        right += 1
    return int(right - left)


def align_traces(tr, k=200):
    """Cross-correlation alignment to the mean trace (preprocess.align)."""
    ref = tr.mean(axis=0)
    out = np.empty_like(tr)
    for i in range(len(tr)):
        c = sps.correlate(tr[i], ref, mode='same', method='fft')
        out[i] = np.roll(tr[i], -int(np.argmax(c) - tr.shape[1] // 2))
    return out


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--h5', required=True)
    ap.add_argument('--no-align', action='store_true')
    ap.add_argument('--n-perm', type=int, default=200)
    ap.add_argument('--cols', type=int, default=64)
    ap.add_argument('--out', default=None)
    args = ap.parse_args()

    with h5py.File(args.h5, 'r') as f:
        a = dict(f.attrs)
        tr = f['traces'][:].astype(np.float64)
        keys, nonces = f['keys'][:], f['nonces'][:]
    n, S = tr.shape
    M = int(a.get('avg_m', 1))
    fs = a.get('fs_hz', 40e6)
    crypto = a.get('crypto_clk_hz', 1e7)
    out = args.out or os.path.join(
        'results', 'scan_%s.json' % os.path.basename(args.h5).replace('.h5', ''))

    print(f'[+] {os.path.basename(args.h5)}')
    print(f'    n={n} samples={S} M={M} fs={fs/1e6:.0f}MS/s '
          f'crypto={crypto/1e6:.1f}MHz ({fs/crypto:.0f} samp/cyc) '
          f'key_mode={a.get("key_mode")}')
    thr = 3.4 / np.sqrt(n * M)
    print(f'    theoretical detection floor 3.4/sqrt(N*M) = {thr:.4f}'
          f'   (N*M = {n*M})')

    if not args.no_align:
        t0 = time.time()
        tr = align_traces(tr)
        print(f'    aligned ({time.time()-t0:.0f}s)')

    rng = np.random.default_rng(0)
    res = {'file': os.path.basename(args.h5), 'n': n, 'samples': S, 'M': M,
           'fs_hz': float(fs), 'crypto_hz': float(crypto),
           'key_mode': a.get('key_mode'), 'floor_3.4_sqrt_NM': float(thr)}

    # ---------------- controls ----------------
    # The key-load bus leak (|r|~0.5-0.65) is a KNOWN-PRESENT signal in
    # random-key captures and must be ABSENT in fixed-key ones.  Its role
    # therefore depends on the capture mode:
    #   random-key -> positive control: must be detected, proves the chain works
    #   fixed-key  -> negative control: must be ~null, proves the artifact is gone
    pc = np.array([bin(v).count('1') for v in range(256)], dtype=np.float64)
    nonce_hw = pc[nonces].sum(axis=1)
    key_hw = pc[keys].sum(axis=1)
    r_nonce = maxabs_r(tr, nonce_hw)
    r_key = maxabs_r(tr, key_hw)
    null_n = perm_max_null(tr, [nonce_hw, key_hw], n_perm=args.n_perm, rng=rng)
    n999 = float(np.quantile(null_n, 0.999))
    mode = a.get('key_mode')
    print('\n[CONTROLS]  (key_mode=%s)' % mode)
    if mode == 'random':
        ok = r_key.max() > null_n.max()
        print(f'  POSITIVE (key-load bus, known present in random-key data): '
              f'max|r| {r_key.max():.4f} @sample {int(r_key.argmax())}  '
              f'null max {null_n.max():.4f}  -> '
              f'{"OK — chain detects a known signal" if ok else "FAILED"}')
        res['control_positive_ok'] = bool(ok)
    else:
        ok = r_key.max() <= null_n.max()
        verdict = ('OK — artifact cancelled' if ok else
                   'WARNING — key rewritten per trace; scan is confounded')
        print(f'  NEGATIVE (key-load bus, must vanish for a fixed key): '
              f'max|r| {r_key.max():.4f}  null max {null_n.max():.4f}  '
              f'-> {verdict}')
        res['control_negative_ok'] = bool(ok)
    print(f'  nonce-load bus (varies in both modes): max|r| '
          f'{r_nonce.max():.4f} @sample {int(r_nonce.argmax())}')
    res['control_nonce_max_r'] = float(r_nonce.max())
    res['control_key_max_r'] = float(r_key.max())
    res['null_control_max'] = float(null_n.max())

    # ---------------- per-column scan ----------------
    in_bits, out_bits, out_hw = intermediates(keys, nonces)
    recs = []
    t0 = time.time()
    for c in range(args.cols):
        r_hw = maxabs_r(tr, out_hw[:, c])
        pk = int(r_hw.argmax())
        rec = {'col': c,
               'cpa_hw': float(r_hw.max()),
               'peak': pk,
               'fwhm': fwhm(r_hw, pk),
               'r_hw_profile_argmax_val': float(r_hw[pk])}
        for k in range(5):
            rec[f'dpa_out_bit{k}'] = float(maxabs_r(tr, out_bits[:, k, c]).max())
            rec[f'dpa_in_bit{k}'] = float(maxabs_r(tr, in_bits[:, k, c]).max())
        recs.append(rec)
        if c % 16 == 0:
            print(f'  col {c:2d}  cpa_hw {rec["cpa_hw"]:.4f}  '
                  f'peak {pk}  fwhm {rec["fwhm"]}  ({time.time()-t0:.0f}s)',
                  flush=True)

    # ---------------- significance: permutation max-statistic + Holm -------
    # Null built from several predictors (HW + a couple of output bits) so
    # the distribution of the max-over-samples statistic is well sampled.
    print(f'\n[null] building permutation max-|r| distribution '
          f'({args.n_perm} perms)...', flush=True)
    t1 = time.time()
    null_max = perm_max_null(
        tr,
        [out_hw[:, 0], out_bits[:, 0, 0], nonce_hw],
        n_perm=args.n_perm, rng=rng)
    res['null_max_mean'] = float(null_max.mean())
    res['null_max_p999'] = float(np.quantile(null_max, 0.999))
    print(f'[null] mean {null_max.mean():.4f}  p99 {np.quantile(null_max,0.99):.4f}'
          f'  p99.9 {np.quantile(null_max,0.999):.4f}  '
          f'max {null_max.max():.4f}  ({time.time()-t1:.0f}s)')

    tests, names = [], []
    for rec in recs:
        tests.append(rec['cpa_hw']); names.append(f"col{rec['col']}_hw")
        for k in range(5):
            tests.append(rec[f'dpa_out_bit{k}'])
            names.append(f"col{rec['col']}_obit{k}")
            tests.append(rec[f'dpa_in_bit{k}'])
            names.append(f"col{rec['col']}_ibit{k}")
    pv = [perm_p(r, null_max) for r in tests]
    adj = holm(pv)
    res['n_tests'] = len(tests)
    res['n_sig_holm_05'] = int((np.array(adj) < 0.05).sum())
    res['n_above_null_max'] = int((np.array(tests) > null_max.max()).sum())
    sig_names = [nm for nm, q in zip(names, adj) if q < 0.05]

    # ---------------- summary ----------------
    hw = np.array([r['cpa_hw'] for r in recs])
    nmm = float(np.quantile(null_max, 0.999))
    # Per-trace rho equivalent: the stored traces are M-averaged, so an
    # observed correlation r corresponds to a per-trace rho ~= r/sqrt(M).
    rho_floor = nmm / np.sqrt(M)
    res['rho_floor_per_trace'] = float(rho_floor)
    print(f'\n[CRYPTO SCAN — {args.cols} columns]')
    print(f'  cpa_hw  mean {hw.mean():.4f}  max {hw.max():.4f} '
          f'(col {int(hw.argmax())})  null p99.9 {nmm:.4f}')
    print(f'  columns above null p99.9: {int((hw > nmm).sum())}/{args.cols}')
    print(f'  equivalent per-trace detection floor rho_min = null/sqrt(M) '
          f'= {rho_floor:.4f}   (M=1 baseline was ~0.048)')
    peaks = np.array([r['peak'] for r in recs])
    print(f'  peak-sample distribution: median {int(np.median(peaks))}  '
          f'iqr {int(np.percentile(peaks,25))}-{int(np.percentile(peaks,75))}'
          f'  (clustered => consistent POI; scattered => noise argmax)')
    print(f'  FWHM of |r| profile: median {int(np.median([r["fwhm"] for r in recs]))} samples'
          f'  (large => smearing from unaligned M-averaging)')
    print(f'\n[SIGNIFICANCE] {res["n_tests"]} tests vs permutation max-|r| null, Holm-corrected')
    print(f'  null max-|r|: mean {null_max.mean():.4f}  p99.9 '
          f'{np.quantile(null_max,0.999):.4f}  observed max {null_max.max():.4f}')
    print(f'  significant at alpha=0.05 (Holm): {res["n_sig_holm_05"]}')
    print(f'  above the largest null value ({null_max.max():.4f}): '
          f'{res["n_above_null_max"]}')
    if sig_names:
        print(f'  first significant: {sig_names[:10]}')
    else:
        print('  none — no crypto intermediate correlates above the '
              'multiple-comparison-corrected null')

    res['columns'] = recs
    res['significant_names'] = sig_names[:50]
    os.makedirs('results', exist_ok=True)
    with open(out, 'w') as fh:
        json.dump(res, fh, indent=1, default=lambda o: float(o))
    print(f'\n-> {out}')


if __name__ == '__main__':
    main()
