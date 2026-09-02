#!/usr/bin/env python3
r"""bit_attack.py — per-bit template attack + HW-constrained brute-force.

prof16sc_m32 measured: 112/128 key bits leak above noise (r > 0.062,
perm null max). The S-box probe is at floor, but the key-load transient
has per-bit signal at r = 0.06-0.15 (bytes 1-3 at 0.43-0.48).

Strategy:
  1. Profile: per-bit peak sample + sign from random-key data
  2. Live: capture M traces of fixed attack key, average → high-SNR
  3. Predict 128 bits from the averaged trace (threshold at midpoint)
  4. HW-constrained brute-force the uncertain bits
  5. verify_key each candidate

Usage:
  # profile (offline, from npz)
  .venv/bin/python training/bit_attack.py profile --npz training/data/prof16sc_m32.npz

  # attack (live board)
  .venv/bin/python training/bit_attack.py attack --npz training/data/prof16sc_m32.npz \
      --key <hex> --M 512 --bitstream vivado_ascon/ascon_cw305_top.bit
"""
import argparse
import os
import sys
import time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def compute_bit_templates(traces, keys):
    r"""Per-bit (peak_sample, sign, r, delta, sigma_resid) from profiling data.

    Returns (128,) arrays: peak_sample, sign, r, delta (bit=1 mean - bit=0
    mean at peak), sigma_resid (residual std at peak after removing bit effect).
    """
    n = len(traces)
    X = (traces.astype(np.float64) - traces.mean(0)) / (traces.std(0) + 1e-12)
    B = np.zeros((n, 128))
    for b in range(16):
        for j in range(8):
            B[:, b * 8 + j] = (keys[:, b] >> j) & 1
    peaks = np.zeros(128, dtype=np.int64)
    signs = np.zeros(128)
    rs = np.zeros(128)
    deltas = np.zeros(128)
    sigmas = np.zeros(128)
    for c in range(128):
        z = (B[:, c] - B[:, c].mean()) / (B[:, c].std() + 1e-12)
        r = z @ X / n
        pk = int(np.abs(r).argmax())
        peaks[c] = pk
        signs[c] = np.sign(r[pk])
        rs[c] = r[pk]
        # delta = E[sample | bit=1] - E[sample | bit=0] at peak
        bit = B[:, c]
        deltas[c] = X[bit == 1, pk].mean() - X[bit == 0, pk].mean()
        # residual std after removing bit effect
        pred = bit * deltas[c] + (1 - bit) * 0
        resid = X[:, pk] - bit * deltas[c]
        sigmas[c] = resid.std()
    return peaks, signs, rs, deltas, sigmas


def predict_bits(avg_trace, peaks, signs, deltas, mu_at_peak, M):
    r"""Predict 128 bits from an M-averaged trace.

    Returns (predicted_bits (128,), confidence (128,)).
    Confidence = |avg[peak] - threshold| in units of sigma/sqrt(M).
    """
    n_bits = len(peaks)
    pred = np.zeros(n_bits, dtype=np.uint8)
    conf = np.zeros(n_bits)
    for c in range(n_bits):
        val = avg_trace[peaks[c]]
        # threshold = midpoint between bit=0 and bit=1 means
        thr = mu_at_peak[c] + deltas[c] / 2  # = mean + delta/2
        diff = (val - thr) * signs[c]
        pred[c] = 1 if diff > 0 else 0
        # confidence in std units: |diff| / (sigma / sqrt(M))
        conf[c] = abs(diff) / (sigmas[c] / np.sqrt(M) + 1e-12)
    return pred, conf


def hw_constrained_candidates(unknown_bits_by_byte, byte_hw_est, tol=1):
    r"""Enumerate key candidates consistent with per-byte HW estimates.

    unknown_bits_by_byte: dict {byte_idx: list of unknown bit positions}
    byte_hw_est: (16,) float HW estimates from the ridge
    tol: HW estimate tolerance (try hw±tol)

    Yields (16,) uint8 key arrays.
    """
    from itertools import product as iproduct

    def hw(v):
        return bin(v).count('1')

    def byte_candidates(byte_idx, unknown_positions, hw_est):
        known_positions = [j for j in range(8) if j not in unknown_positions]
        known_bits = [None]  # filled by caller via context
        results = []
        for target_hw in [int(round(hw_est)) + d for d in range(-tol, tol + 1)]:
            if target_hw < 0 or target_hw > 8:
                continue
            # enumerate bit assignments for unknown positions
            n_unknown = len(unknown_positions)
            for combo in iproduct([0, 1], repeat=n_unknown):
                total = sum(combo)
                if sum(combo) + _known_sum(byte_idx, unknown_positions, combo) == target_hw:
                    results.append(combo)
        return results

    # simpler: per byte, enumerate all 2^|unknown| and filter by HW
    def byte_opts(byte_idx, unknown_pos, hw_est):
        known_mask = 0
        known_val = 0
        for j in range(8):
            if j not in unknown_pos:
                known_val |= (PRED[byte_idx * 8 + j] << j)
        known_sum = hw(known_val)
        opts = []
        seen = set()
        for target_hw in range(max(0, int(round(hw_est)) - tol),
                               min(8, int(round(hw_est)) + tol) + 1):
            for combo in iproduct([0, 1], repeat=len(unknown_pos)):
                uval = 0
                for k, j in enumerate(unknown_pos):
                    uval |= (combo[k] << j)
                total = hw(known_val | uval)
                if total == target_hw:
                    key = known_val | uval
                    if key not in seen:
                        seen.add(key)
                        opts.append(key)
        return opts

    # build per-byte option lists
    byte_options = []
    for b in range(16):
        unk = unknown_bits_by_byte.get(b, [])
        if not unk:
            byte_options.append([sum(PRED[b * 8 + j] << j for j in range(8))])
        else:
            opts = byte_opts(b, unk, hw_est[b])
            if not opts:
                opts = [sum(PRED[b * 8 + j] << j for j in range(8))]
            byte_options.append(opts)

    # enumerate all byte combinations
    for combo in iproduct(*byte_options):
        key = bytes(combo)
        yield key


PRED = None  # global for hw_constrained_candidates


def cmd_profile(args):
    d = np.load(args.npz, allow_pickle=True)
    traces, keys = d['traces'], d['keys']
    n = len(traces)
    split = int(0.8 * n)
    peaks, signs, rs, deltas, sigmas = compute_bit_templates(
        traces[:split], keys[:split])
    # held-out validation
    B = np.zeros((n - split, 128))
    for b in range(16):
        for j in range(8):
            B[:, b * 8 + j] = (keys[split:, b] >> j) & 1
    Xva = (traces[split:].astype(np.float64) - traces[:split].mean(0)) / \
          (traces[:split].std(0) + 1e-12)
    mu_at_peak = traces[:split].mean(0)[peaks]
    correct = 0
    for i in range(n - split):
        for c in range(128):
            val = Xva[i, peaks[c]]
            thr = mu_at_peak[c] + deltas[c] / 2
            pred = 1 if (val - thr) * signs[c] > 0 else 0
            correct += (pred == B[i, c])
    print('[+] per-bit held-out accuracy: %.1f%% (chance 50%%)' %
          (100 * correct / ((n - split) * 128)))
    # noise floor
    rng = np.random.default_rng(0)
    fls = []
    for _ in range(30):
        p = rng.permutation(split)
        z = (B[:1, 0] * 0)  # placeholder
        zb = np.random.randint(0, 2, split).astype(np.float64)
        zb = (zb - zb.mean()) / (zb.std() + 1e-12)
        fls.append(np.abs(zb @ Xva[:, 0:1] if False else
                    (traces[:split].astype(np.float64) -
                     traces[:split].mean(0))[0] / 1).max()
                  if False else 0.1)
    # simpler: report r distribution
    leaking = (rs > 0.062).sum()
    print('[+] bits leaking (r > 0.062): %d / 128' % leaking)
    print('[+] r distribution: min %.3f  median %.3f  max %.3f' %
          (rs.min(), np.median(rs), rs.max()))
    print('[+] per-bit r (by byte):')
    for b in range(16):
        print('  byte %2d: %s' % (b, ' '.join('%.3f' % rs[b * 8 + j] for j in range(8))))
    # save templates
    out = os.path.join(os.path.dirname(args.npz),
                       'bit_templates_' + os.path.basename(args.npz))
    np.savez(out, peaks=peaks, signs=signs, rs=rs, deltas=deltas,
             sigmas=sigmas, mu_at_peak=traces[:split].mean(0)[peaks])
    print('[+] saved bit templates -> %s' % out)
    # estimate required M for 99% per-bit accuracy
    for M in [128, 256, 512, 1024, 4096]:
        snr = np.abs(rs) * np.sqrt(M)
        from scipy.stats import norm
        p_correct = norm.cdf(snr)
        exp_wrong = (1 - p_correct).sum()
        print('  M=%4d: expected wrong bits among leaking: %.1f / %d' %
              (M, exp_wrong, leaking))


def cmd_attack(args):
    d = np.load(args.npz, allow_pickle=True)
    traces, keys = d['traces'], d['keys']
    n = len(traces)
    split = int(0.8 * n)

    # templates
    tpl_path = os.path.join(os.path.dirname(args.npz),
                            'bit_templates_' + os.path.basename(args.npz))
    if os.path.exists(tpl_path):
        t = np.load(tpl_path)
        peaks = t['peaks']; signs = t['signs']; rs = t['rs']
        deltas = t['deltas']; sigmas = t['sigmas']
        mu_at_peak = t['mu_at_peak']
        print('[+] bit templates loaded from %s' % os.path.basename(tpl_path))
    else:
        peaks, signs, rs, deltas, sigmas = compute_bit_templates(
            traces[:split], keys[:split])
        mu_at_peak = traces[:split].mean(0)[peaks]
        print('[+] bit templates computed from profiling data')

    # HW ridge (per-byte HW estimates)
    from fused_acppa import HWRidge, find_byte_windows
    peaks_hw, hw_half = find_byte_windows(traces[:split], keys[:split])
    ridge = HWRidge.fit(traces, keys, peaks_hw, hw_half)
    print('[+] HW ridge: mean val r = %.3f' % np.mean(ridge.val_r))

    # connect to board
    from live_query import LiveQuery
    attack_key = bytes.fromhex(args.key)
    lq = LiveQuery(args.bitstream, attack_key, crypto_mhz=args.crypto_mhz,
                   gain=args.gain, samples=2000, offset=0)
    ref = d['ref'].astype(np.float64) if 'ref' in d else traces.mean(0)
    offset = int(d['offset']) if 'offset' in d else 0

    # capture M traces of the fixed key, average
    print('[+] capturing %d traces for bit prediction...' % args.M)
    from preprocess import align_trace, zscore
    pool = []
    for _ in range(args.M):
        nonce = os.urandom(16)
        tr, ct = lq.query(nonce)
        if tr is not None:
            pool.append(tr)
    if len(pool) < args.M // 2:
        print('[!] only %d/%d captures succeeded' % (len(pool), args.M))
    avg = np.mean(pool, axis=0)
    # align against ref and z-score (same as profiling)
    avg = zscore(align_trace(avg.astype(np.float64), ref))
    avg = avg[offset:offset + traces.shape[1]]
    print('[+] averaged %d traces' % len(pool))

    # predict bits
    global PRED
    PRED = predict_bits(avg, peaks, signs, deltas, mu_at_peak, len(pool))[0]
    conf = predict_bits(avg, peaks, signs, deltas, mu_at_peak, len(pool))[1]

    # sort bits by confidence (ascending = least confident first)
    bit_order = np.argsort(conf)
    n_certain = int((conf > args.conf_threshold).sum())
    n_uncertain = 128 - n_certain
    print('[+] bit prediction: %d certain (conf > %.1f), %d uncertain' %
          (n_certain, args.conf_threshold, n_uncertain))
    print('[+] confidence distribution: min %.2f  median %.2f  max %.2f' %
          (conf.min(), np.median(conf), conf.max()))

    # HW estimate from the averaged trace
    hw_est = ridge.hat(avg)
    hw_round = np.round(hw_est).astype(int)
    print('[+] HW estimates: %s' % ' '.join('%d' % h for h in hw_round))

    # determine uncertain bits per byte
    uncertain_bits = set(bit_order[:n_uncertain].tolist())
    unknown_by_byte = {}
    for c in uncertain_bits:
        b = c // 8
        unknown_by_byte.setdefault(b, []).append(c % 8)
    print('[+] uncertain bits per byte: %s' %
          {b: len(v) for b, v in sorted(unknown_by_byte.items())})

    # HW-constrained brute-force
    n_candidates = 1
    for b in range(16):
        unk = unknown_by_byte.get(b, [])
        if unk:
            n_candidates *= min(2 ** len(unk), 70)  # cap at C(8,4)
    print('[+] brute-force search space: ~%d candidates' % n_candidates)

    if n_candidates > args.max_candidates:
        print('[!] search space too large (%d > %d), raising confidence threshold' %
              (n_candidates, args.max_candidates))
        # raise threshold until we have few enough uncertain bits
        for thr in [2.0, 3.0, 5.0, 10.0]:
            n_unc = int((conf <= thr).sum())
            unk_set = set(np.argsort(conf)[:n_unc].tolist())
            unk_by = {}
            for c in unk_set:
                unk_by.setdefault(c // 8, []).append(c % 8)
            nc = 1
            for b in range(16):
                if b in unk_by:
                    nc *= min(2 ** len(unk_by[b]), 70)
            if nc <= args.max_candidates:
                n_uncertain = n_unc
                uncertain_bits = unk_set
                unknown_by_byte = unk_by
                n_candidates = nc
                print('[+] threshold %.1f: %d uncertain, ~%d candidates' %
                      (thr, n_uncertain, n_candidates))
                break

    # enumerate and verify
    t0 = time.time()
    tried = 0
    for cand in hw_constrained_candidates(unknown_by_byte, hw_est, tol=1):
        tried += 1
        ok, ct_o, ct_f = lq.verify_key(cand)
        if ok:
            print('[KEY CRACKED] %s after %d candidates (%.1fs)' %
                  (cand.hex(), tried, time.time() - t0))
            return cand, True
        if tried % 1000 == 0:
            print('  ... tried %d (%.1fs)' % (tried, time.time() - t0))
    print('[!] key not found in %d candidates (%.1fs)' %
          (tried, time.time() - t0))

    # fallback: try without HW constraint (all uncertain bits free)
    print('[+] retrying without HW constraint...')
    from itertools import product as iproduct
    for combo in iproduct([0, 1], repeat=n_uncertain):
        cand = PRED.copy()
        for k, c in enumerate(sorted(uncertain_bits)):
            cand[c] = combo[k]
        key = bytes(cand.reshape(16, 8) @ (1 << np.arange(8)))
        # Actually rebuild key bytes from bits
        key = np.zeros(16, dtype=np.uint8)
        for c in range(128):
            key[c // 8] |= np.uint8(cand[c] << (c % 8))
        key = bytes(key)
        ok, _, _ = lq.verify_key(key)
        if ok:
            print('[KEY CRACKED] %s (no HW constraint)' % key.hex())
            return key, True
    print('[!] key not found')
    return None, False


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('profile', help='compute per-bit templates from npz')
    p.add_argument('--npz', required=True)

    a = sub.add_parser('attack', help='live per-bit + HW brute-force attack')
    a.add_argument('--npz', required=True)
    a.add_argument('--key', required=True, help='attack key hex (16 bytes)')
    a.add_argument('--bitstream', default='vivado_ascon/ascon_cw305_top.bit')
    a.add_argument('--crypto-mhz', type=float, default=2.5)
    a.add_argument('--gain', type=int, default=25)
    a.add_argument('--M', type=int, default=512, help='traces to average')
    a.add_argument('--conf-threshold', type=float, default=1.0,
                   help='SNR threshold for certain bits (sigma units)')
    a.add_argument('--max-candidates', type=int, default=100000,
                   help='max brute-force candidates')

    args = ap.parse_args()
    if args.cmd == 'profile':
        cmd_profile(args)
    elif args.cmd == 'attack':
        cmd_attack(args)


if __name__ == '__main__':
    main()
