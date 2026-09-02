#!/usr/bin/env python3
r"""hw_attack.py — per-byte HW template + HW-constrained brute-force key recovery.

prof16sc_m32 measured: S-box leakage at floor (r < 0.062, noise floor 0.062).
Key-load HW leakage is real: per-byte val r = 0.16-0.48, mean 0.257.
Per-bit leakage exists (88/128 above noise) but r = 0.06-0.14, too weak
for single-trace bit classification.

Strategy:
  1. Profile: per-byte HW classifier (9-class logistic regression on load
     transient window) from random-key M-averaged traces
  2. Live: capture M traces of fixed attack key, average → high-SNR
  3. Predict per-byte HW (9 classes) from the averaged trace
  4. HW-constrained brute-force: for each byte, enumerate values with
     HW == predicted HW (±tol); verify_key each candidate
  5. Search space = product of C(8, hw_i) per byte

At M=32 profiling, HW top-1 = 28%, top-3 = 72%.
At M=512 live (16x more), expected top-1 ~ 70%, top-3 ~ 95%.
  - top-1 correct: 11/16 bytes → 23^11 * 256^5 = 2^89 (too big)
  - With M=4096: per-byte r = 0.25 * sqrt(4096/32) = 1.8 → >99% top-1
    → 50^16 = 2^90 (still too big with perfect HW)

BUT: the per-bit r at M=4096: 0.08*sqrt(128) = 0.9, 0.14*sqrt(128) = 1.6
  → per-bit accuracy 82-95%. With 112 leaking bits at >82%:
  expected wrong = 112*0.18 = 20 bits → 2^20 candidates (feasible!).

The combined attack:
  1. Per-bit template prediction (strong bits, conf > threshold)
  2. Per-byte HW constrains the uncertain bytes
  3. Brute-force the residual (uncertain bits within HW-consistent values)

Usage:
  .venv/bin/python training/hw_attack.py profile --npz training/data/prof16sc_m32.npz
  .venv/bin/python training/hw_attack.py attack --npz training/data/prof16sc_m32.npz \
      --key <hex> --M 4096 --bitstream vivado_ascon/ascon_cw305_top.bit
"""
import argparse
import os
import sys
import time
import numpy as np
from itertools import product as iproduct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def compute_bit_templates(traces, keys):
    r"""Per-bit (peak_sample, sign, r) from profiling data."""
    n = len(traces)
    X = (traces.astype(np.float64) - traces.mean(0)) / (traces.std(0) + 1e-12)
    B = np.zeros((n, 128))
    for b in range(16):
        for j in range(8):
            B[:, b * 8 + j] = (keys[:, b] >> j) & 1
    peaks = np.zeros(128, dtype=np.int64)
    signs = np.zeros(128)
    rs = np.zeros(128)
    for c in range(128):
        z = (B[:, c] - B[:, c].mean()) / (B[:, c].std() + 1e-12)
        r = z @ X / n
        pk = int(np.abs(r).argmax())
        peaks[c] = pk
        signs[c] = np.sign(r[pk])
        rs[c] = r[pk]
    return peaks, signs, rs


def compute_hw_templates(traces, keys, half_width=10):
    r"""Per-byte (peak_sample, ridge_model, sigma) for HW classification."""
    from sklearn.linear_model import Ridge
    n = len(traces)
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], float)
    X = (traces.astype(np.float64) - traces.mean(0)) / (traces.std(0) + 1e-12)
    split = int(0.8 * n)
    peaks = np.zeros(16, dtype=np.int64)
    models = []
    sigmas = []
    col_mus = []
    col_sds = []
    for b in range(16):
        z = (hw[:split, b] - hw[:split, b].mean()) / (hw[:split, b].std() + 1e-12)
        r = z @ X[:split] / split
        pk = int(np.abs(r).argmax())
        peaks[b] = pk
        lo = max(0, pk - half_width)
        w = 2 * half_width + 1
        Xb = traces[:split, lo:lo + w].astype(np.float64)
        mu, sd = Xb.mean(0), Xb.std(0) + 1e-12
        Xs = (Xb - mu) / sd
        m = Ridge(alpha=3.0).fit(Xs, hw[:split, b])
        models.append(m)
        Xva = traces[split:, lo:lo + w].astype(np.float64)
        Xvs = (Xva - mu) / sd
        pred = m.predict(Xvs)
        sigmas.append(max(float(np.sqrt(((pred - hw[split:, b]) ** 2).mean())), 0.25))
        col_mus.append(mu)
        col_sds.append(sd)
    return peaks, models, sigmas, col_mus, col_sds, half_width


def cmd_profile(args):
    d = np.load(args.npz, allow_pickle=True)
    traces, keys = d['traces'], d['keys']
    n = len(traces)
    split = int(0.8 * n)

    # bit templates
    peaks, signs, rs = compute_bit_templates(traces[:split], keys[:split])
    leaking = (np.abs(rs) > 0.062).sum()
    print('[+] bit templates: %d/128 bits leak (r > 0.062)' % leaking)
    print('[+] r range: %.3f - %.3f (median %.3f)' %
          (np.abs(rs).min(), np.abs(rs).max(), np.median(np.abs(rs))))

    # HW templates
    from sklearn.linear_model import LogisticRegression
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys])
    for ws in [25, 50]:
        accs, top3s = [], []
        for b in range(16):
            y = hw[:split, b]
            lr = LogisticRegression(max_iter=500, C=0.1)
            lr.fit(traces[:split, :ws], y)
            pred = lr.predict(traces[split:, :ws])
            accs.append((pred == hw[split:, b]).mean())
            proba = lr.predict_proba(traces[split:, :ws])
            classes = lr.classes_
            top3 = 0
            for i in range(len(proba)):
                top3_idx = np.argsort(-proba[i])[:3]
                if hw[split + i, b] in classes[top3_idx]:
                    top3 += 1
            top3s.append(top3 / len(proba))
        print('[+] HW window=%d: top-1 %.1f%% (chance 11%%), top-3 %.1f%%' %
              (ws, 100 * np.mean(accs), 100 * np.mean(top3s)))

    # search space estimate at various M
    peaks_hw, models, sigmas, mus, sds, hww = compute_hw_templates(traces, keys)
    # per-byte HW-class accuracy at M=32 (current data)
    from sklearn.linear_model import LogisticRegression
    for M_live in [32, 128, 512, 2048, 4096]:
        # r scales as sqrt(M_live / M_profile) where M_profile=32
        r_eff = np.abs(rs) * np.sqrt(M_live / 32)
        from scipy.stats import norm
        p_bit = norm.cdf(r_eff)
        exp_wrong_bits = int((1 - p_bit).sum())
        # HW top-1 accuracy scales similarly: at M=32 it's 28%
        # at M_live: ~ norm.cdf(r_hw * sqrt(M_live/32)) where r_hw ~ 0.25
        r_hw = 0.25
        p_hw = norm.cdf(r_hw * np.sqrt(M_live / 32))
        # expected wrong bytes (HW top-1 wrong)
        exp_wrong_bytes = int(16 * (1 - p_hw))
        # search space: wrong bytes get 256 values, correct bytes get C(8, hw) ~ 50
        from scipy.special import comb
        space = float(50 ** (16 - exp_wrong_bytes) * 256 ** exp_wrong_bytes)
        print('  M=%4d: exp wrong bits %3d, wrong bytes %2d, '
              'search ~%.2e (2^%.1f)' %
              (M_live, exp_wrong_bits, exp_wrong_bytes,
               space, np.log2(space) if space > 0 else 0))

    # save
    out = os.path.join(os.path.dirname(args.npz),
                       'hw_attack_' + os.path.basename(args.npz))
    np.savez(out, peaks=peaks, signs=signs, rs=rs,
             hw_peaks=peaks_hw, hw_sigmas=sigmas, hw_half_width=hww,
             hw_coefs=np.array([m.coef_ for m in models]),
             hw_intercepts=np.array([m.intercept_ for m in models]),
             hw_col_mus=np.array(mus), hw_col_sds=np.array(sds))
    print('[+] saved hw_attack templates -> %s' % out)


def cmd_attack(args):
    d = np.load(args.npz, allow_pickle=True)
    traces, keys = d['traces'], d['keys']
    n = len(traces)
    split = int(0.8 * n)

    # load templates
    tpl_path = os.path.join(os.path.dirname(args.npz),
                            'hw_attack_' + os.path.basename(args.npz))
    if not os.path.exists(tpl_path):
        print('[!] no templates found, profiling first...')
        cmd_profile(args)
    t = np.load(tpl_path)
    peaks = t['peaks']; signs = t['signs']; rs = t['rs']
    hw_peaks = t['hw_peaks']; hw_sigmas = t['hw_sigmas']
    hw_half = int(t['hw_half_width'])
    hw_coefs = t['hw_coefs']; hw_intercepts = t['hw_intercepts']
    hw_mus = t['hw_col_mus']; hw_sds = t['hw_col_sds']

    # connect to board
    from live_query import LiveQuery
    from preprocess import align_trace, zscore
    attack_key = bytes.fromhex(args.key)
    lq = LiveQuery(args.bitstream, attack_key, crypto_mhz=args.crypto_mhz,
                   gain=args.gain, samples=2000, offset=0)
    ref = d['ref'].astype(np.float64) if 'ref' in d else traces.mean(0)
    offset = int(d['offset']) if 'offset' in d else 0

    # capture M traces of the fixed key, average
    print('[+] capturing %d traces...' % args.M)
    pool = []
    for _ in range(args.M):
        tr, ct = lq.query(os.urandom(16))
        if tr is not None:
            pool.append(tr)
    if len(pool) < args.M // 2:
        print('[!] only %d/%d captures' % (len(pool), args.M))
    avg = np.mean(pool, axis=0)
    avg = zscore(align_trace(avg.astype(np.float64), ref))
    avg = avg[offset:offset + traces.shape[1]]
    M_eff = len(pool)
    print('[+] averaged %d traces (SNR boost %.1fx vs M=32)' %
          (M_eff, np.sqrt(M_eff / 32)))

    # --- Phase 1: per-bit template prediction ---
    mu_peak = traces[:split].mean(0)[peaks]
    # delta = E[sample | bit=1] - E[sample | bit=0] at peak (from profiling)
    B = np.zeros((split, 128))
    for b in range(16):
        for j in range(8):
            B[:, b * 8 + j] = (keys[:split, b] >> j) & 1
    Xtr = (traces[:split].astype(np.float64) - traces[:split].mean(0)) / \
          (traces[:split].std(0) + 1e-12)
    deltas = np.zeros(128)
    for c in range(128):
        bit = B[:, c]
        deltas[c] = Xtr[bit == 1, peaks[c]].mean() - Xtr[bit == 0, peaks[c]].mean()

    # predict bits from the averaged trace
    pred_bits = np.zeros(128, dtype=np.uint8)
    conf_bits = np.zeros(128)
    for c in range(128):
        val = avg[peaks[c]]
        thr = mu_peak[c] + deltas[c] / 2
        diff = (val - thr) * signs[c]
        pred_bits[c] = 1 if diff > 0 else 0
        # confidence in SNR units
        sigma = Xtr[:, peaks[c]].std()
        conf_bits[c] = abs(diff) / (sigma / np.sqrt(M_eff / 32) + 1e-12)

    # --- Phase 2: per-byte HW estimate ---
    hw_est = np.zeros(16)
    for b in range(16):
        lo = max(0, int(hw_peaks[b]) - hw_half)
        w = 2 * hw_half + 1
        row = avg[lo:lo + w]
        ws = (row - hw_mus[b]) / hw_sds[b]
        hw_est[b] = hw_intercepts[b] + ws @ hw_coefs[b]
    hw_round = np.clip(np.round(hw_est), 0, 8).astype(int)
    print('[+] HW estimates: %s' % ' '.join('%d' % h for h in hw_round))

    # --- Phase 3: HW-constrained brute-force ---
    # For each byte: the predicted bits give a base value. The HW estimate
    # gives a target HW. If predicted bits' HW != target HW, flip the
    # least-confident bits to match.
    true_hw = np.array([bin(int(k)).count('1') for k in
                        bytes.fromhex(args.key)])  # for debugging only
    print('[+] true HW  : %s' % ' '.join('%d' % h for h in true_hw))
    print('[+] pred HW  : %s' % ' '.join('%d' % h for h in
                                          [bin(int(np.sum(pred_bits[b*8:(b+1)*8]))).count('1') for b in range(16)]))

    # For each byte, enumerate all values consistent with:
    # 1. HW == hw_round[b] (primary constraint)
    # 2. Bits predicted with high confidence are fixed
    # The search space per byte = C(8, hw) but with high-conf bits pinned
    from scipy.special import comb as C8

    # confidence-based bit pinning
    threshold = args.conf_threshold
    certain = conf_bits > threshold
    n_certain = certain.sum()
    print('[+] bits certain (conf > %.1f): %d / 128' % (threshold, n_certain))

    # per-byte: pin certain bits, enumerate uncertain bits that match target HW
    byte_candidates = []
    for b in range(16):
        target_hw = hw_round[b]
        # fixed bits from template prediction
        fixed = 0
        fixed_count = 0
        uncertain_positions = []
        for j in range(8):
            c = b * 8 + j
            if certain[c]:
                fixed |= (pred_bits[c] << j)
                fixed_count += 1
            else:
                uncertain_positions.append(j)
        fixed_hw = bin(fixed).count('1')
        remaining_hw = target_hw - fixed_hw
        n_unc = len(uncertain_positions)
        if remaining_hw < 0 or remaining_hw > n_unc:
            # HW constraint violated; widen to ±1
            for target_hw in [hw_round[b] - 1, hw_round[b] + 1]:
                if 0 <= target_hw <= 8:
                    remaining_hw = target_hw - fixed_hw
                    if 0 <= remaining_hw <= n_unc:
                        break
            else:
                remaining_hw = max(0, min(n_unc, target_hw - fixed_hw))

        # enumerate all C(n_unc, remaining_hw) bit assignments
        cands = []
        for combo in iproduct([0, 1], repeat=n_unc):
            if sum(combo) != remaining_hw:
                continue
            val = fixed
            for k, j in enumerate(uncertain_positions):
                val |= (combo[k] << j)
            cands.append(val)
        byte_candidates.append(cands)

    total = 1
    for b in range(16):
        total *= len(byte_candidates[b])
    print('[+] brute-force search space: %d candidates' % total)

    if total > args.max_candidates:
        print('[!] search space too large (> %d), raising confidence threshold' %
              args.max_candidates)
        for thr in [2.0, 3.0, 5.0, 10.0, 20.0]:
            certain = conf_bits > thr
            byte_candidates = []
            for b in range(16):
                target_hw = hw_round[b]
                fixed = 0
                uncertain_positions = []
                for j in range(8):
                    c = b * 8 + j
                    if certain[c]:
                        fixed |= (pred_bits[c] << j)
                    else:
                        uncertain_positions.append(j)
                fixed_hw = bin(fixed).count('1')
                remaining_hw = target_hw - fixed_hw
                remaining_hw = max(0, min(len(uncertain_positions), remaining_hw))
                cands = []
                for combo in iproduct([0, 1], repeat=len(uncertain_positions)):
                    if sum(combo) != remaining_hw:
                        continue
                    val = fixed
                    for k, j in enumerate(uncertain_positions):
                        val |= (combo[k] << j)
                    cands.append(val)
                byte_candidates.append(cands)
            total = 1
            for b in range(16):
                total *= len(byte_candidates[b])
            print('  conf > %.1f: %d certain, %d candidates' %
                  (thr, certain.sum(), total))
            if total <= args.max_candidates:
                break
        else:
            print('[!] cannot reduce below %d, aborting' % total)
            return None, False

    # enumerate and verify
    t0 = time.time()
    tried = 0
    for combo in iproduct(*byte_candidates):
        key = bytes(combo)
        tried += 1
        ok, ct_o, ct_f = lq.verify_key(key)
        if ok:
            print('[KEY CRACKED] %s after %d candidates (%.1fs)' %
                  (key.hex(), tried, time.time() - t0))
            return key, True
        if tried % 1000 == 0:
            print('  ... tried %d (%.1fs)' % (tried, time.time() - t0))
    print('[!] key not found in %d candidates (%.1fs)' %
          (tried, time.time() - t0))
    return None, False


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('profile', help='compute bit + HW templates from npz')
    p.add_argument('--npz', required=True)

    a = sub.add_parser('attack', help='live HW + bit-template brute-force attack')
    a.add_argument('--npz', required=True)
    a.add_argument('--key', required=True, help='attack key hex (16 bytes)')
    a.add_argument('--bitstream', default='vivado_ascon/ascon_cw305_top.bit')
    a.add_argument('--crypto-mhz', type=float, default=2.5)
    a.add_argument('--gain', type=int, default=25)
    a.add_argument('--M', type=int, default=4096, help='traces to average')
    a.add_argument('--conf-threshold', type=float, default=1.0,
                   help='SNR threshold for certain bits')
    a.add_argument('--max-candidates', type=int, default=100000,
                   help='max brute-force candidates')

    args = ap.parse_args()
    if args.cmd == 'profile':
        cmd_profile(args)
    elif args.cmd == 'attack':
        cmd_attack(args)


if __name__ == '__main__':
    main()
