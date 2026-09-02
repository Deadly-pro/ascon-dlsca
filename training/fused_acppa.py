#!/usr/bin/env python3
r"""Fused ACPPA: per-column S-box profiles + key-load HW-ridge joint attack.

Two independent physical witnesses per key bit:
  1. S-box round-1 switching (per-column profile, the board-proven engine)
  2. Key-load byte HW leakage (ridge regression on the load window — the
     same window the SAKURA-G cross-validation confirmed at r~0.21/byte
     with M=32 averaging)

Fusion mechanism (feasibility-checked on avg32 held-out data):
  - HW evidence alone: +0.105 nats/byte/trace discrimination at sigma=1.32,
    scaling ~M (needs M~2048 alone — NOT the primary engine)
  - As JOINT evidence at attack time: every query under the FIXED attack key
    re-estimates the byte HWs; hypothesis scores get
    score(h) += Q * HW_LL(bits of h) with Q = evidence weight
  - As PRIOR: per-bit entropy after HW fusion drops to 0.91 bits (M=32)

Joint structure: columns come in byte-pairs — column c depends on bit
(c%8) of key bytes (c//8) and (8 + c//8). Byte HW couples all 8 columns of
a byte pair: knowing bytes narrows all 8 columns' 4 hypotheses at once.

Usage:
  # fit + offline validate the HW ridges on the profiling npz
  python3 training/fused_acppa.py fit --npz training/data/prof16sc_m32.npz

  # full fused attack against the live board
  python3 training/fused_acppa.py attack --npz training/data/prof16sc_m32.npz \
      --model-dir training/models/prof16sc/ --key <attack_key_hex>
"""
import argparse
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labels as lab  # noqa: E402


# ---------------------------------------------------------------------------
# HW ridge: fit per-byte HW regression on the key-load window
# ---------------------------------------------------------------------------

def find_load_window(traces, keys, half_width=12):
    r"""Locate the key-load window: the sample maximizing mean |corr| with
    byte-HW across all 16 key bytes. Random-key profiling data required
    (fixed keys have zero HW variance)."""
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys],
                  np.float64)
    X = (traces.astype(np.float64) - traces.mean(0)) / (traces.std(0) + 1e-12)
    n = len(X)
    acc = np.zeros(X.shape[1])
    for b in range(16):
        z = (hw[:, b] - hw[:, b].mean()) / (hw[:, b].std() + 1e-12)
        acc += np.abs(z @ X / n)
    peak = int(acc.argmax())
    lo = max(0, peak - half_width)
    return lo, 2 * half_width + 1, peak


def find_byte_windows(traces, keys, half_width=10):
    r"""Per-byte peak samples (the load transient is NOT one shared window —
    measured peaks fall at samples ~25, ~398 and ~621 on prof16sc_m32).
    Returns (16,) peak sample indices, each validated on the train split."""
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys],
                  np.float64)
    X = (traces.astype(np.float64) - traces.mean(0)) / (traces.std(0) + 1e-12)
    n = len(X)
    peaks = np.empty(16, dtype=np.int64)
    for b in range(16):
        z = (hw[:, b] - hw[:, b].mean()) / (hw[:, b].std() + 1e-12)
        r = z @ X / n
        peaks[b] = int(np.abs(r).argmax())
    return peaks, half_width


class HWRidge:
    r"""16 per-byte ridge regressors, EACH on its own load-transient window
    (per-byte peak ± half_width — bytes peak at different samples), plus
    residual sigma per byte for Gaussian likelihood scoring."""

    def __init__(self, peaks, half_width):
        self.peaks = np.asarray(peaks, dtype=np.int64)
        self.half_width = half_width
        self.width = 2 * half_width + 1
        self.models = []
        self.sigmas = []

    @classmethod
    def fit(cls, traces, keys, peaks, half_width):
        obj = cls(peaks, half_width)
        hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys],
                      np.float64)
        n = len(traces)
        split = int(0.8 * n)
        from sklearn.linear_model import Ridge
        obj.col_mu, obj.col_sd, obj.val_r = [], [], []
        for b in range(16):
            lo = max(0, int(obj.peaks[b]) - half_width)
            X = traces[:split, lo:lo + obj.width].astype(np.float64)
            # dataset-level per-column stats (per-trace standardization
            # breaks the train/infer distribution match)
            mu, sd = X.mean(axis=0), X.std(axis=0) + 1e-12
            Xs = (X - mu) / sd
            obj.col_mu.append(mu)
            obj.col_sd.append(sd)
            m = Ridge(alpha=3.0).fit(Xs, hw[:split, b])
            obj.models.append(m)
            # held-out sigma + val r (fit split stats on train, evaluate val
            # using the SAME train stats — the attack-time condition)
            Xva = traces[split:, lo:lo + obj.width].astype(np.float64)
            Xvs = (Xva - mu) / sd
            pred = m.predict(Xvs)
            resid = pred - hw[split:, b]
            obj.sigmas.append(max(float(np.sqrt((resid ** 2).mean())), 0.25))
            sd_y = hw[split:, b].std() + 1e-12
            obj.val_r.append(float(np.corrcoef(pred, hw[split:, b])[0, 1]))
        return obj

    def hat(self, trace_row):
        r"""One aligned+z-scored trace -> 16 HW estimates."""
        out = np.empty(16)
        for b in range(16):
            lo = max(0, int(self.peaks[b]) - self.half_width)
            w = trace_row[lo:lo + self.width].astype(np.float64)
            ws = (w - self.col_mu[b]) / self.col_sd[b]
            out[b] = self.models[b].predict(ws[None])[0]
        return out

    def log_lik_bytes(self, hats):
        """(16,) HW estimates -> (16, 256) log-likelihood per byte value."""
        hw256 = np.array([bin(x).count('1') for x in range(256)], np.float64)
        out = np.empty((16, 256))
        for b in range(16):
            s = self.sigmas[b]
            out[b] = -0.5 * (hats[b] - hw256) ** 2 / (s ** 2)
        return out


# ---------------------------------------------------------------------------
# Column <-> key bit structure
# ---------------------------------------------------------------------------

def column_key_bits(c):
    """Column c depends on bit (c%8) of key bytes c//8 and 8+c//8."""
    byte0, byte1, bit = c // 8, 8 + c // 8, c % 8
    return byte0, byte1, bit


def bits_from_byte(val, bit):
    return (int(val) >> bit) & 1


# ---------------------------------------------------------------------------
# Fused scoring
# ---------------------------------------------------------------------------

def hw_ll_for_hypotheses(hw_ll_bytes, column, known_bits=None):
    r"""Per-column: (4,) HW log-likelihood of the 2 key bits.

    hw_ll_bytes : (16, 256) per-byte-value log-likelihood (HWRidge).
    known_bits  : optional dict {(byte, bit): 0/1} of bits already pinned by
                  sibling columns. With k of the byte's 8 bits pinned, the
                  HW marginal shrinks from 128 values to 2^(7-k) — the LL gap
                  between the two candidate bits widens accordingly. This is
                  the joint-fusion lever: siblings narrow, HW confirms.
    """
    byte0, byte1, bit = column_key_bits(column)
    out = np.empty(4)
    for h, (b0, b1) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)]):
        out[h] = (_byte_marginal(hw_ll_bytes[byte0], byte0, bit, b0, known_bits)
                  + _byte_marginal(hw_ll_bytes[byte1], byte1, bit, b1, known_bits))
    return out


def _byte_marginal(ll, byte, bit, want, known_bits=None):
    vals = np.arange(256)
    mask = ((vals >> bit) & 1) == want
    if known_bits:
        for (b_, bit_), v_ in known_bits.items():
            if b_ != byte or bit_ == bit:
                continue
            mask &= ((vals >> bit_) & 1) == v_
    if not mask.any():
        return -np.inf
    return np.logaddexp.reduce(ll[mask])


def assemble_key(bits_per_column):
    """(64,) recovered bit pairs -> 16-byte key, or None on conflict."""
    key = np.zeros(16, dtype=np.uint8)
    seen = {}
    for c in range(64):
        byte0, byte1, bit = column_key_bits(c)
        b0, b1 = bits_per_column[c]
        for byte, b in ((byte0, b0), (byte1, b1)):
            if (byte, bit) in seen and seen[(byte, bit)] != b:
                return None
            seen[(byte, bit)] = b
            key[byte] |= np.uint8(b << bit)
    return bytes(key)


# ---------------------------------------------------------------------------
# Offline fit + validation
# ---------------------------------------------------------------------------

def cmd_fit(args):
    d = np.load(args.npz, allow_pickle=True)
    traces, keys = d['traces'], d['keys']
    n = len(traces)
    split = int(0.8 * n)
    peaks, half_width = find_byte_windows(traces[:split], keys[:split])
    print(f'[+] per-byte peak samples: {peaks.tolist()}')
    ridge = HWRidge.fit(traces, keys, peaks, half_width)
    print(f'[+] per-byte val r: '
          + ' '.join(f'{r:.2f}' for r in ridge.val_r))
    mean_r = float(np.mean(ridge.val_r))
    print(f'[+] mean val r = {mean_r:.3f} '
          f'({"GOOD" if mean_r > 0.15 else "WEAK — raise M"})')
    # true-vs-random discrimination on held-out (the honest fusion metric:
    # LL gain of the TRUE byte value minus LL gain of a random byte value)
    rng = np.random.RandomState(0)
    rand_keys = rng.randint(0, 256, size=(300, 16))
    g_true, g_rand = [], []
    va = list(range(split, min(split + 300, n)))
    for j, i in enumerate(va):
        hats = ridge.hat(traces[i])
        ll = ridge.log_lik_bytes(hats)
        for b in range(16):
            lls = ll[b]
            g_true.append(lls[int(keys[i, b])] - np.logaddexp.reduce(lls))
            g_rand.append(lls[rand_keys[j % 300, b]] - np.logaddexp.reduce(lls))
    disc = float(np.mean(g_true) - np.mean(g_rand))
    print(f'[+] true-vs-random discrimination: {disc:+.3f} nats/byte '
          f'({16*disc:+.1f} nats/trace; need +89 for HW-alone full key)')
    # END-TO-END probe: multi-query byte-HW attack on held-out — can we
    # rank the true byte in top-1/top-8 given K independent queries?
    for K in (8, 32, 128):
        top1 = top8 = 0
        for t0 in range(0, min(1200, n - split) - K, 300):
            va_idx = range(t0, t0 + K)
            acc = np.zeros((16, 256))
            for i in va_idx:
                ll = ridge.log_lik_bytes(ridge.hat(traces[split + i]))
                acc += ll
            acc -= acc.max(axis=1, keepdims=True)
            acc -= np.logaddexp.reduce(acc, axis=1, keepdims=True)
            w = np.exp(acc)
            for b in range(16):
                order = np.argsort(-w[b])
                rank = int(np.where(order == int(keys[split + t0, b]))[0][0])
                top1 += rank == 0
                top8 += rank < 8
        tot = ((min(1200, n - split) - K) // 300 + 1) * 16
        print(f'[+] multi-query K={K:3d}: byte top-1 {100*top1/tot:.1f}% '
              f'top-8 {100*top8/tot:.1f}% (chance 0.4/3.1%)')
    np.savez(os.path.join(os.path.dirname(args.npz),
                          'hwridge_' + os.path.basename(args.npz)),
             peaks=peaks, half_width=half_width,
             sigmas=ridge.sigmas, coef=np.array([m.coef_ for m in ridge.models]),
             intercept=np.array([m.intercept_ for m in ridge.models]),
             val_r=ridge.val_r,
             col_mu=np.array(ridge.col_mu), col_sd=np.array(ridge.col_sd))
    print('[+] saved hwridge npz next to the profiling npz')


# ---------------------------------------------------------------------------
# Live fused attack
# ---------------------------------------------------------------------------

def cmd_attack(args):
    import torch  # noqa: F401  (Profile needs it)
    from adaptive import Profile, pick_separating_nonce
    from preprocess import align_trace, zscore
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from live_query import LiveQuery

    d = np.load(args.npz, allow_pickle=True)
    ref = d['ref'].astype(np.float64)
    offset = int(d['offset']) if 'offset' in d else 0
    keys_prof = d['keys']
    traces_prof = d['traces']

    # HW ridge (fit fresh on the profiling data, or reuse the saved one)
    ridge_path = os.path.join(os.path.dirname(args.npz),
                              'hwridge_' + os.path.basename(args.npz))
    if os.path.exists(ridge_path):
        rd = np.load(ridge_path)
        peaks = rd['peaks']
        ridge = HWRidge(peaks, int(rd['half_width']))
        ridge.col_mu = list(rd['col_mu'])
        ridge.col_sd = list(rd['col_sd'])
        from sklearn.linear_model import Ridge as _R
        for b in range(16):
            m = _R()
            m.coef_ = rd['coef'][b]
            m.intercept_ = float(rd['intercept'][b])
            ridge.models.append(m)
        ridge.sigmas = list(rd['sigmas'])
        print(f'[+] HW ridge loaded from {os.path.basename(ridge_path)}')
    else:
        traces_prof = d['traces']
        keys_prof = d['keys']
        peaks, half_width = find_byte_windows(traces_prof, keys_prof)
        ridge = HWRidge.fit(traces_prof, keys_prof, peaks, half_width)
        print(f'[+] HW ridge fitted fresh (peaks {peaks.tolist()[:4]}...)')

    # per-column profiles (train.py naming: <name>_c<col>_sbox_<arch>.pt,
    # plus a plain col<c>.pt alias if you rename them)
    import glob as _glob
    hyps = lab.all_hypotheses()
    profiles = {}
    val_accs = {}
    for c in range(64):
        p = None
        for pat in (f'*_c{c}_sbox_*.pt', f'col{c}.pt'):
            hits = sorted(_glob.glob(os.path.join(args.model_dir, pat)))
            if hits:
                p = hits[0]
                break
        if p is not None:
            profiles[c] = Profile(p, args.npz)
            val_accs[c] = float(torch.load(p, map_location='cpu')['best_val_acc'])
    print(f'[+] loaded {len(profiles)}/64 column profiles from {args.model_dir}')
    if len(profiles) < 8:
        sys.exit('too few profiles — train per-column models first')

    attack_key = bytes.fromhex(args.key)
    lq = LiveQuery(args.bitstream, attack_key, crypto_mhz=args.crypto_mhz,
                    gain=args.gain, samples=2000, offset=0)

    # per-column posterior (4 hyps)
    logpost = {c: np.zeros(4) for c in range(64)}
    Q = args.hw_weight

    def query_M(nonce, M):
        """Average M captures of the same nonce; each capture retries
        internally on flat/short (lq.query returns None)."""
        pool = []
        attempts = 0
        while len(pool) < M and attempts < M + 8:
            attempts += 1
            tr, ct = lq.query(nonce)
            if tr is not None:
                pool.append(tr)
        if not pool:
            return None
        return np.mean(pool, axis=0)

    order = sorted(profiles.keys(), key=lambda c: -val_accs[c])
    print(f'[+] attack order (by profile quality): {order[:8]} ...')

    t0 = time.time()
    total_q = 0
    known_bits = {}
    for c in order:
        prof = profiles[c]
        byte0, byte1, bit = column_key_bits(c)
        kb = {k: v for k, v in known_bits.items()}
        for qi in range(args.max_q):
            nonce = pick_separating_nonce(c, prof.support, post=np.exp(logpost[c]))
            tr = query_M(nonce, args.M)
            total_q += 1
            if tr is None:
                continue
            # locked preprocessing order: align FULL -> z-score FULL -> crop
            atr = zscore(align_trace(tr.astype(np.float64), ref))
            atr = atr[offset:offset + traces_prof.shape[1]]
            # witness 1: sbox profile
            logp = prof.log_probs(atr[None].astype(np.float32))
            from adaptive import score_trace
            sc = score_trace(logp[0], nonce, c, prof.classes)
            # witness 2: HW ridge on the same trace (joint fusion: known
            # sibling bits narrow the byte marginal)
            hats = ridge.hat(atr)
            hwll = hw_ll_for_hypotheses(ridge.log_lik_bytes(hats), c, kb)
            hwll -= np.logaddexp.reduce(hwll)  # normalize (removes prior)
            logpost[c] += sc + Q * hwll
            logpost[c] -= np.logaddexp.reduce(logpost[c])
            post = np.exp(logpost[c])
            if post.max() > args.threshold:
                break
        b0, b1 = hyps[int(np.argmax(logpost[c]))]
        known_bits[(byte0, bit)] = int(b0)
        known_bits[(byte1, bit)] = int(b1)
        print(f'  col {c:2d}: bits ({b0},{b1}) post {np.exp(logpost[c]).max():.3f} '
              f'q={qi+1} elapsed {time.time()-t0:.0f}s')

    # assemble + verify
    bits = {}
    for c in order:
        h = int(np.argmax(logpost[c]))
        bits[c] = tuple(hyps[h])
    missing = [c for c in range(64) if c not in bits]
    for c in missing:
        bits[c] = (0, 0)
    cand = assemble_key([bits[c] for c in range(64)])
    print(f'[+] candidate key: {cand.hex()}')
    ok, ct_o, ct_f = lq.verify_key(cand)
    print(f'[{"KEY CRACKED" if ok else "verify failed"}] total queries {total_q}')
    return cand, ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)

    f = sub.add_parser('fit', help='fit+validate HW ridges on profiling npz')
    f.add_argument('--npz', required=True)

    a = sub.add_parser('attack', help='fused ACPPA against the live board')
    a.add_argument('--npz', required=True)
    a.add_argument('--model-dir', required=True)
    a.add_argument('--key', required=True, help='attack key hex (16 bytes)')
    a.add_argument('--bitstream', default='vivado_ascon/ascon_cw305_top.bit')
    a.add_argument('--crypto-mhz', type=float, default=2.5)
    a.add_argument('--gain', type=int, default=25)
    a.add_argument('--M', type=int, default=64, help='traces averaged per query')
    a.add_argument('--max-q', type=int, default=24, help='queries per column')
    qhelp = ('HW evidence weight per query; 1.0 = full Gaussian LL. '
             'Measured discrimination is weak at M=1, so default is low.')
    a.add_argument('--hw-weight', type=float, default=0.25)
    a.add_argument('--threshold', type=float, default=0.995)
    a.set_defaults(func=cmd_attack)
    f.set_defaults(func=cmd_fit)

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
