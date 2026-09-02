#!/usr/bin/env python3
r"""board_bit_test.py — on-board validation of the 111/128-bit attack premise.

Random fixed key → M-averaged capture (avg-m semantics, same as
prof16sc_m32) → per-bit template prediction on the averaged+aligned+
z-scored trace → count ACTUAL wrong bits → build HW-constrained candidate
set → check TRUE key rank within the set → timing for the residual brute.

This validates the "111/128 bits leak, brute the rest" claim end-to-end
against the real board, at known key (honest rank measurement, no cheating).

Usage:
  python3 board_bit_test.py --M 4096 --bitstream vivado_ascon/ascon_cw305_top.bit
  python3 board_bit_test.py --key <hex> --M 1024   # reproducible key
"""
import argparse
import os
import sys
import time
import numpy as np
from itertools import product as iproduct

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

NPZ = os.path.join(ROOT, 'training/data/prof16sc_m32.npz')
TPL = os.path.join(ROOT, 'training/data/hw_attack_prof16sc_m32.npz')


def load_templates():
    d = np.load(NPZ, allow_pickle=True)
    traces, keys = d['traces'].astype(np.float64), d['keys']
    t = np.load(TPL)
    return d, traces, keys, t


def bit_predictor(traces, keys, split):
    r"""Fit per-bit (peak, sign, delta, sigma) on the first `split` traces."""
    n = len(traces)
    mu = traces.mean(0)
    sd = traces.std(0) + 1e-12
    X = (traces - mu) / sd
    B = np.zeros((n, 128))
    for b in range(16):
        for j in range(8):
            B[:, b * 8 + j] = (keys[:, b] >> j) & 1
    peaks = np.zeros(128, dtype=np.int64)
    signs = np.zeros(128)
    deltas = np.zeros(128)
    sigmas = np.zeros(128)
    for c in range(128):
        z = (B[:split, c] - B[:split, c].mean()) / (B[:split, c].std() + 1e-12)
        r = z @ X[:split] / split
        pk = int(np.abs(r).argmax())
        peaks[c] = pk
        signs[c] = np.sign(r[pk]) if r[pk] != 0 else 1.0
        bit = B[:split, c]
        deltas[c] = X[:split][bit == 1, pk].mean() - X[:split][bit == 0, pk].mean()
        resid = X[:split, pk] - bit * deltas[c]
        sigmas[c] = resid.std() + 1e-12
    return peaks, signs, deltas, sigmas, mu, sd


def predict_bits(avg_z, peaks, signs, deltas, sigmas, M_eff, M_prof=32):
    r"""Predict 128 bits + confidences from the averaged z-scored trace.

    M_prof = averaging depth of the profiling set (32). The live avg of
    M_eff traces has residual noise sigma/sqrt(M_eff/32) relative to the
    profiling per-trace (already-averaged) noise sigma.
    """
    pred = np.zeros(128, dtype=np.uint8)
    conf = np.zeros(128)
    scale = np.sqrt(M_prof / max(M_eff, 1))
    for c in range(128):
        val = avg_z[peaks[c]]
        thr = deltas[c] / 2.0  # X is z-scored: bit=0 mean ~0
        diff = (val - thr) * signs[c]
        pred[c] = 1 if diff > 0 else 0
        conf[c] = abs(diff) / (sigmas[c] * scale + 1e-12)
    return pred, conf


def hw_ridge_predict(avg_z, t):
    r"""Per-byte HW estimate from the stored HW ridge templates.

    The HW ridge was fit on z-scored traces with per-column mu/sd over a
    window around each byte's HW-peak sample. avg_z here is the full
    z-scored trace (per-sample z using profiling mu/sd — matches the
    per-byte window z only if we re-z the window. To stay consistent with
    the ridge fit domain, re-z inside each window).
    """
    hw_half = int(t['hw_half_width'])
    hw_peaks = t['hw_peaks']
    coefs = t['hw_coefs']
    inter = t['hw_intercepts']
    mus = t['hw_col_mus']
    sds = t['hw_col_sds']
    est = np.zeros(16)
    for b in range(16):
        lo = max(0, int(hw_peaks[b]) - hw_half)
        w = 2 * hw_half + 1
        row = avg_z[lo:lo + w]
        est[b] = inter[b] + ((row - mus[b]) / sds[b]) @ coefs[b]
    return est


def candidate_space(pred_bits, conf, hw_est, conf_threshold, tol=1):
    r"""Build per-byte candidate lists pinned by (conf, HW)."""
    certain = conf > conf_threshold
    byte_cands = []
    for b in range(16):
        base = int(round(hw_est[b]))
        hw_try = [base + d for d in range(-tol, tol + 1)]
        fixed = 0
        free = []
        for j in range(8):
            c = b * 8 + j
            if certain[c]:
                fixed |= int(pred_bits[c]) << j
            else:
                free.append(j)
        fixed_hw = bin(fixed).count('1')
        cands = set()
        for target in hw_try:
            if not (0 <= target <= 8):
                continue
            rem = target - fixed_hw
            if rem < 0 or rem > len(free):
                continue
            for combo in iproduct([0, 1], repeat=len(free)):
                if sum(combo) != rem:
                    continue
                v = fixed
                for k, j in enumerate(free):
                    v |= combo[k] << j
                cands.add(v)
        if not cands:
            cands = {int(''.join(str(x) for x in pred_bits[b*8:(b+1)*8][::-1]), 2)}
        byte_cands.append(sorted(cands))
    return byte_cands


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--key', default=None, help='fixed attack key hex; random if omitted')
    ap.add_argument('--M', type=int, default=2048,
                    help='traces averaged for the attack capture')
    ap.add_argument('--bitstream', default='vivado_ascon/ascon_cw305_top.bit')
    ap.add_argument('--crypto-mhz', type=float, default=2.5)
    ap.add_argument('--gain', type=int, default=25)
    ap.add_argument('--samples', type=int, default=2000)
    ap.add_argument('--conf-threshold', type=float, default=1.0)
    ap.add_argument('--max-candidates', type=int, default=2 ** 20)
    ap.add_argument('--skip-brute', action='store_true',
                    help='stop after rank measurement (no verify-key loop)')
    args = ap.parse_args()

    rng = np.random.default_rng()
    attack_key = (bytes.fromhex(args.key) if args.key
                  else bytes(rng.integers(0, 256, 16, dtype=np.uint8)))
    print('[*] attack key: %s' % attack_key.hex())
    print('[*] true HW  : %s' % ' '.join(str(bin(k).count('1')) for k in attack_key))

    d, traces, keys, t = load_templates()
    split = int(0.8 * len(traces))
    print('[+] templates: %d profiling traces (split %d)' % (len(traces), split))
    peaks, signs, deltas, sigmas, mu, sd = bit_predictor(traces, keys, split)
    ref = d['ref'].astype(np.float64)

    from live_query import LiveQuery
    from preprocess import align_trace, zscore
    lq = LiveQuery(args.bitstream, attack_key, crypto_mhz=args.crypto_mhz,
                   gain=args.gain, samples=args.samples, offset=0)

    # ---- capture M averaged traces -------------------------------------
    # The attack needs ONE high-SNR averaged trace of the fixed key.
    # prof16sc_m32 stored mean-of-32 per (key,nonce); here we average
    # M single captures of the same key across random nonces — leakage
    # (key-load INIT) is nonce-independent so this is coherent.
    print('[*] capturing %d single captures (gain %d, %.1f MHz)...' %
          (args.M, args.gain, args.crypto_mhz))
    t0 = time.time()
    pool = []
    n_fail = 0
    i = 0
    while len(pool) < args.M and i < args.M * 3:
        i += 1
        tr, ct = lq.query(os.urandom(16))
        if tr is None:
            n_fail += 1
            continue
        pool.append(tr.astype(np.float64))
        if len(pool) % 200 == 0:
            print('  %d/%d (%.0fs, %d rejects)' %
                  (len(pool), args.M, time.time() - t0, n_fail))
    if len(pool) < args.M // 2:
        print('[!] capture failed: only %d good traces' % len(pool))
        lq.close()
        return 1
    M_eff = len(pool)
    print('[+] %d good captures in %.0fs (%d rejected)' %
          (M_eff, time.time() - t0, n_fail))

    # preprocessing EXACTLY as profiling: align vs ref -> per-trace zscore,
    # then average the ALIGNED traces (key-load leakage is at fixed sample
    # positions after alignment).
    aligned = [zscore(align_trace(tr, ref)) for tr in pool]
    avg = np.mean(aligned, axis=0)
    print('[+] aligned+averaged; avg trace std %.4f' % avg.std())

    # ---- bit prediction --------------------------------------------------
    pred, conf = predict_bits(avg, peaks, signs, deltas, sigmas, M_eff)
    true_bits = np.zeros(128, dtype=np.uint8)
    for b in range(16):
        for j in range(8):
            true_bits[b * 8 + j] = (attack_key[b] >> j) & 1
    wrong = int((pred != true_bits).sum())
    print('[+] PREDICTED %d/128 bits correct (%d wrong) at M=%d' %
          (128 - wrong, wrong, M_eff))
    wrong_bits = np.where(pred != true_bits)[0]
    print('    wrong bit positions: %s' % wrong_bits.tolist())
    for b in range(16):
        wv = [int(c) for c in wrong_bits if c // 8 == b]
        if wv:
            print('    byte %2d: wrong bits %s (conf %s)' %
                  (b, wv, np.round(conf[wv], 2).tolist()))
    acc = (pred == true_bits).mean()
    print('[+] per-bit accuracy: %.1f%%' % (100 * acc))

    # ---- HW estimate ------------------------------------------------------
    hw_est = hw_ridge_predict(avg, t)
    print('[+] HW estimate: %s' % ' '.join('%.1f' % h for h in hw_est))
    hw_true = np.array([bin(k).count('1') for k in attack_key])
    hw_err = np.abs(hw_est - hw_true)
    print('[+] HW true    : %s' % ' '.join(str(h) for h in hw_true))
    print('[+] HW error   : %s (|err|<=1 on %d/16 bytes)' %
          (' '.join('%.0f' % e for e in hw_err), int((hw_err <= 1).sum())))

    # ---- candidate set + true-key rank -----------------------------------
    for thr in [args.conf_threshold, 2.0, 3.0, 5.0]:
        cands = candidate_space(pred, conf, hw_est, thr)
        total = int(np.prod([len(c) for c in cands]))
        # true-key rank: is the true byte in each byte's candidate list?
        present = [attack_key[b] in cands[b] for b in range(16)]
        n_present = sum(present)
        print('[*] conf>%.1f: space %d (%.2f=%d bit), true bytes present %d/16' %
              (thr, total, '2^', int(np.log2(max(total, 1))), n_present))
        if n_present == 16:
            print('[+] TRUE KEY IS IN THE CANDIDATE SET at conf>%.1f' % thr)
            if total <= args.max_candidates and not args.skip_brute:
                t0 = time.time()
                tried = 0
                found = False
                for combo in iproduct(*cands):
                    tried += 1
                    ok, _, _ = lq.verify_key(bytes(combo))
                    if ok:
                        print('[KEY CRACKED] %s after %d candidates (%.1fs)' %
                              (bytes(combo).hex(), tried, time.time() - t0))
                        found = True
                        break
                    if tried % 500 == 0:
                        print('  ... %d tried (%.0fs)' % (tried, time.time() - t0))
                if not found:
                    print('[!] true key NOT verified in %d candidates' % tried)
            break
        else:
            miss = [b for b in range(16) if not present[b]]
            print('    bytes missing from set: %s' % miss)

    lq.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
