#!/usr/bin/env python3
r"""byte_hw_attack.py — per-byte HW load-leakage attack (Phase 2+3).

The unmasked core leaks the HW of each key byte at its register-load
transient (verified: per-byte correlation peaks 2-8x noise floor on M=64
averaged captures, byte-distinguishable peak samples). This tool:
  1. finds each byte's peak sample + neighborhood on profiling data
  2. trains an 8-class HW classifier per byte (leakage-model evidence)
  3. scores evidence over the 8 hypotheses per byte, per trace
  4. accumulates posterior over hypotheses; key rank via product
  5. (board) adaptive nonce choice + oracle verify of the assembled key

Usage:
  # profile + self-eval on an npz (random keys, M-averaged):
  .venv/bin/python training/byte_hw_attack.py training/data/avg32.npz

  # attack a fixed key with a live board connection:
  python3 training/byte_hw_attack.py training/data/avg32.npz \
      --attack --key <hex> --gain 35 --bitstream vivado_ascon/ascon_cw305_top.bit
"""
import argparse
import os
import sys
import time

import numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))


def byte_hw_labels(keys):
    """(N,16) u8 -> (N,16) u8: popcount of each key byte."""
    keys = np.asarray(keys, dtype=np.uint8)
    return np.array([[bin(int(b)).count('1') for b in row] for row in keys],
                    dtype=np.uint8)


def regress_drift(traces, idle_lo=1500, idle_hi=2000, ncomp=3,
                  return_model=False):
    """Remove capture-time drift: PCA on the idle region (no crypto
    activity) gives the drift subspace; project it out of every sample.
    Without this, between-capture drift masks the byte-HW leak (measured:
    held-out rho 2/16 -> 10/16 usable bytes on avg32).
    With return_model=True, also returns (B, Vt, ncomp) so a single live
    trace can be drift-corrected with the same model (live_drift_fix)."""
    Xc = np.asarray(traces - traces.mean(0), dtype=np.float64)
    idle = np.ascontiguousarray(Xc[:, idle_lo:idle_hi])
    U, S, Vt = np.linalg.svd(idle, full_matrices=False)
    drift = U[:, :ncomp] * S[:ncomp]
    A = np.concatenate([np.ones((len(traces), 1)), drift], axis=1)
    B = np.linalg.lstsq(A, Xc, rcond=None)[0]
    out = Xc - A @ B
    if return_model:
        return out, (B, Vt[:ncomp], ncomp)
    return out



def align_to_profile(trace, profile_mean, max_shift=32):
    """Cross-correlate a live trace against the profile mean trace and roll
    it into register. The new core's transient is ~3 samples wide: even a
    few samples of trigger jitter zeroes the template projection (measured:
    shift 3 -> HW err 1.4). Profiling data is already aligned (preprocess.py
    reported 0.0-sample jitter), so the LIVE capture is the one to fix."""
    ref = profile_mean[:len(trace)]
    t = trace - trace.mean()
    c = signal.correlate(t, ref - ref.mean(), mode='full', method='fft')
    mid = len(trace) - 1
    shift = int(np.argmax(c[mid - max_shift:mid + max_shift + 1])) - max_shift
    return np.roll(trace, -shift)

def find_peaks(traces, labels, half=15):
    """Per byte: correlation peak sample + neighborhood, fit set only."""
    n = len(traces)
    Xc = traces - traces.mean(0)
    Xc = Xc / (Xc.std(0) + 1e-12)
    peaks = np.zeros(16, dtype=int)
    strength = np.zeros(16)
    for b in range(16):
        y = labels[:, b].astype(np.float64)
        z = (y - y.mean()) / (y.std() + 1e-12)
        r = np.abs(z @ Xc / n)
        i = int(r.argmax())
        peaks[b] = i
        strength[b] = float(r[i])
    return peaks, strength


class ByteProfile:
    """Per-byte 8-class HW classifier on the peak neighborhood."""

    def __init__(self, traces, labels, peaks, half=15):
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        n, W = traces.shape
        Xc = traces - traces.mean(0)
        Xc = Xc / (Xc.std(0) + 1e-12)
        self.half = half
        self.peaks = peaks
        self.clfs = []
        self.classes = []
        self.floors = np.zeros(16)
        self.val_acc = np.zeros(16)
        sp = int(0.75 * n)
        for b in range(16):
            i = int(peaks[b])
            lo, hi = max(0, i - half), min(W, i + half)
            F = Xc[:, lo:hi]
            y = labels[:, b].astype(int)
            # train only on classes present in the fit set
            self.floors[b] = 100.0 * np.bincount(y[:sp], minlength=8).max() / sp
            clf = LogisticRegression(max_iter=500, C=0.5)
            clf.fit(F[:sp], y[:sp])
            acc = 100.0 * (clf.predict(F[sp:]) == y[sp:]).mean()
            self.clfs.append(clf)
            self.classes.append(clf.classes_)
            self.val_acc[b] = acc

    def evidence(self, trace):
        """(16, 8) log-probs for one trace (already aligned+z-scored).
        Classes absent from the fit set get -1e3 (impossible)."""
        t = (trace - trace.mean()) / (trace.std() + 1e-12)
        out = np.full((16, 9), -1e3)
        for b in range(16):
            i = self.peaks[b]
            lo, hi = max(0, i - self.half), min(len(trace), i + self.half)
            f = t[lo:hi][None, :]
            lp = self.clfs[b].predict_log_proba(f)[0]
            for c, v in zip(self.classes[b], lp):
                out[b, int(c)] = v
        return out


def accumulate(ev_batch, prior=None):
    """Bayesian accumulation over a batch of evidence (T,16,8)."""
    post = np.full((16, 8), 0.0) if prior is None else prior.copy()
    log = np.log(np.maximum(post, 1e-12)) if prior is not None else None
    acc = np.zeros((16, 8)) if log is None else log.copy()
    for ev in ev_batch:
        acc += ev
    return acc


def self_eval(npz, verbose=True):
    """Profile on 75%, evaluate byte-HW accuracy + key rank on held-out 25%."""
    d = np.load(npz, allow_pickle=True)
    traces = d['traces'].astype(np.float64)
    keys = d['keys']
    labels = byte_hw_labels(keys)
    n = len(traces)
    sp = int(0.75 * n)
    Xres = traces  # RAW traces: drift regression smeared the transient
    drift_model = None
    peaks, strength = find_peaks(Xres[:sp], labels[:sp])
    if verbose:
        print('[+] per-byte correlation strength (fit set):')
        for b in range(16):
            print(f'  key[{b:2d}]: r={strength[b]:.3f} @ {peaks[b]}')
    prof = ByteProfile(Xres, labels, peaks)
    if verbose:
        print('[+] per-byte 8-class held-out accuracy (floor+5 = usable):')
        for b in range(16):
            ok = 'USABLE' if prof.val_acc[b] > prof.floors[b] + 5 else 'floor'
            print(f'  key[{b:2d}]: acc {prof.val_acc[b]:5.1f}%  floor '
                  f'{prof.floors[b]:5.1f}%  {ok}')
    # ---- key rank on held-out traces (byte-wise posterior product) ----
    ranks = []
    for t in range(sp, n):
        ev = prof.evidence(Xres[t])
        # rank of the true byte HW class per byte (by log-prob)
        rr = []
        for b in range(16):
            cls = labels[t, b]
            order = np.argsort(-ev[b])
            rr.append(int(np.where(order == cls)[0][0]))
        ranks.append(rr)
    ranks = np.array(ranks)
    ge = (ranks == 0).mean(0)
    if verbose:
        print('[+] held-out byte top-1 rate (random-key, no adaptation):')
        print('  ' + ' '.join(f'{v:.2f}' for v in ge))
        print(f'  mean top-1 {ge.mean():.3f} (chance ~1/8=0.125 for 8 classes)')
    return prof, ge


def build_candidates(hw_est, hw_conf, width=256):
    """Expand per-byte HW estimates to ordered candidate values.
    hw_est: (16,) continuous HW estimates. Returns (16, width) candidate
    byte values sorted by |HW(cand) - hw_est| (closest first)."""
    hw_table = np.array([bin(v).count('1') for v in range(256)], np.float64)
    cands = np.zeros((16, width), dtype=np.uint8)
    for b in range(16):
        order = np.argsort(np.abs(hw_table - hw_est[b]))
        cands[b] = order[:width].astype(np.uint8)
    return cands


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('npz', help='profiling npz (random keys, M-averaged)')
    ap.add_argument('--attack', action='store_true',
                    help='run the live board attack (fixed key, oracle verify)')
    ap.add_argument('--key', default=None, help='target key hex (attack mode)')
    ap.add_argument('--gain', type=int, default=35)
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--window', type=int, default=640,
                    help='trace window used for scoring')
    ap.add_argument('--max-queries', type=int, default=64)
    ap.add_argument('--M', type=int, default=600,
                    help='same-key captures per query batch (HW RMSE 0.44 '
                         'at M=10, 0.20 at M=50)')
    ap.add_argument('--weak-cols', type=int, default=14,
                    help='enumerate top-2 alternatives for the N least '
                         'confident columns (2^N offline verifies)')
    ap.add_argument('--beam', type=int, default=100000,
                    help='max offline ASCON verifications')
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon',
                                         'ascon_cw305_top.bit'))
    args = ap.parse_args()

    d = np.load(args.npz, allow_pickle=True)
    traces = d['traces'].astype(np.float64)
    keys = d['keys']
    labels = byte_hw_labels(keys)
    n = len(traces)
    sp = int(0.75 * n)
    Xres = traces  # RAW traces: drift regression smeared the transient
    drift_model = None
    peaks, strength = find_peaks(Xres[:sp], labels[:sp])
    prof = ByteProfile(Xres, labels, peaks)
    # HW regression coefficients per byte (the value-recovery model)
    hw_coefs = []
    # Full-projection scalar: project the trace on the per-byte signed
    # correlation template (keeps the sharp 1-3 sample transient; a +-15
    # sample mean washes the signal out to r~0.02 - the bug that made every
    # live HW estimate collapse to the population mean 4.0).
    for b in range(16):
        hw_fit = labels[:sp, b].astype(np.float64)
        z = (hw_fit - hw_fit.mean()) / (hw_fit.std() + 1e-12)
        r_prof = (z @ Xres[:sp] / sp)[:args.window]
        s_fit = Xres[:sp, :args.window] @ r_prof
        A1 = np.stack([np.ones(sp), s_fit], 1)
        coef, *_ = np.linalg.lstsq(A1, hw_fit, rcond=None)
        hw_coefs.append((coef, r_prof))
    nn = d['nonces']
    sb_labels = d['labels_sbox'] if 'labels_sbox' in d else d['labels']
    print('[+] profile ready: 16 byte-HW templates + HW regressions')

    if not args.attack:
        print('[+] offline eval only (pass --attack --key <hex>)')
        return

    # ---------------- live board attack ----------------
    import live_query
    from ascon_ref import ascon_encrypt
    # --key omitted: the script draws a random key (oracle role) and the
    # attack must recover it blind; the true key prints only at the end.
    key = bytes.fromhex(args.key) if args.key else os.urandom(16)
    lq = live_query.LiveQuery(args.bitstream, key, gain=args.gain,
                              crypto_mhz=10.0, samples=2000)
    lq.set_key(key)
    rng = np.random.default_rng(0)
    t0 = time.time()

    # Phase 1: M captures per nonce, HW estimate per byte accumulates
    hw_est = np.zeros(16)
    hw_n = 0
    nonce = os.urandom(16)
    last_ct = None
    pool = []
    while len(pool) < args.M:
        tr, ct = lq.query(nonce)
        if tr is None:
            continue
        pool.append(tr.astype(np.float64)[:2000])
        last_ct = ct
    tr_mean = np.mean(pool, axis=0)
    tr_mean = align_to_profile(tr_mean, Xres[:sp].mean(0))
    t_res = tr_mean  # RAW traces: no drift projection (it smeared the transient)
    for b in range(16):
        coef, r_prof = hw_coefs[b]
        s = t_res[:args.window] @ r_prof
        hw_est[b] = coef[0] + coef[1] * s
    hw_n = args.M
    true_hw = byte_hw_labels(np.frombuffer(key, np.uint8)[None])[0]
    print(f'[+] HW estimates from M={args.M} captures:')
    for b in range(16):
        d_hw = hw_est[b] - true_hw[b]
        mark = 'OK' if abs(d_hw) < 0.5 else ('~' if abs(d_hw) < 1.0 else 'MISS')
        print(f'  key[{b:2d}]: est {hw_est[b]:5.2f}  true {true_hw[b]}  '
              f'diff {d_hw:+5.2f}  {mark}')
    # Phase 2: per-column separating-nonce reads (round-1 S-box, 2-class)
    # The round-1 S-box HW at a FIXED (n0,n1) group is a 2-3 class problem
    # (measured: nonce(0,1) gives only classes {2,3}). Pooled probes sat at
    # floor because the group mixture destroyed separability. Each group
    # read + M-capture averaging gives an independent vote on the 2 key
    # bits; two groups x 64 columns, combined with the byte-HW constraint.
    import labels as lab
    hyps = lab.all_hypotheses()
    col_bits = np.zeros((64, 4))           # log-evidence per hypothesis
    sbox_prof = {}
    from sklearn.linear_model import LogisticRegression
    for c in range(64):
        for (n0, n1) in ((0, 1), (1, 0)):
            m_fit = (((nn[:sp, c // 8] >> (c % 8)) & 1) == n0) & \
                    (((nn[:sp, 8 + c // 8] >> (c % 8)) & 1) == n1)
            y_fit = sb_labels[:sp, c][m_fit]
            if m_fit.sum() < 60 or len(np.unique(y_fit)) < 2:
                continue
            clf = LogisticRegression(max_iter=200)
            clf.fit(Xres[:sp][m_fit][:, :args.window], y_fit)
            sbox_prof[(c, n0, n1)] = (clf, [int(v) for v in np.unique(y_fit)])
    print(f'[+] sbox group templates: {len(sbox_prof)}/128 fitted')
    last_ct = None
    for (n0, n1) in ((0, 1), (1, 0)):
        nonce2 = bytearray(os.urandom(16))
        for c in range(64):
            if n0:
                nonce2[c // 8] |= (1 << (c % 8))
            else:
                nonce2[c // 8] &= ~(1 << (c % 8)) & 0xFF
            if n1:
                nonce2[8 + c // 8] |= (1 << (c % 8))
            else:
                nonce2[8 + c // 8] &= ~(1 << (c % 8)) & 0xFF
        nonce2 = bytes(nonce2)
        pool = []
        while len(pool) < args.M:
            tr, ct = lq.query(nonce2)
            if tr is None:
                continue
            pool.append(tr.astype(np.float64)[:2000])
            last_ct = ct
        tr_mean2 = np.mean(pool, axis=0)
        tr_mean2 = align_to_profile(tr_mean2, Xres[:sp].mean(0))
        t_res2 = tr_mean2  # RAW traces: no drift projection
        for c in range(64):
            if (c, n0, n1) not in sbox_prof:
                continue
            clf, classes = sbox_prof[(c, n0, n1)]
            p = clf.predict_proba(t_res2[None, :])[0]
            pred = lab.hypothesis_labels(
                c, np.frombuffer(nonce2, np.uint8)[None], hyps)[0]
            for h in range(4):
                cls = int(pred[h])
                if cls in classes:
                    idx = classes.index(cls)
                    col_bits[c, h] += np.log(max(p[idx], 1e-9))
    print('[+] separating-nonce reads done')

    # Phase 3: direct assembly, then weak-column product search.
    # The sbox evidence is per-column independent; the ML estimate is the
    # per-column argmax. Wrong columns concentrate in the low-confidence
    # tail - enumerate their top-2 alternatives as a product (2^k combos)
    # and verify each with one offline ASCON.
    post = np.exp(col_bits - col_bits.max(1, keepdims=True))
    post /= post.sum(1, keepdims=True)
    base = np.array([int(post[c].argmax()) for c in range(64)])

    def assemble(hyps):
        k = bytearray(16)
        for c in range(64):
            k[c // 8] |= ((int(hyps[c]) >> 1) & 1) << (c % 8)
            k[8 + c // 8] |= (int(hyps[c]) & 1) << (c % 8)
        return bytes(k)

    def check(k):
        return ascon_encrypt(k, nonce, bytes(4), bytes(4))[:4] == last_ct[:4]

    cand = assemble(base)
    if check(cand):
        print(f'[+] KEY FOUND (direct sbox assembly): {cand.hex()}')
        print(f'[+] true key: {key.hex()}  match={cand == key}')
        lq.close()
        return
    print('[!] direct assembly wrong -> weak-column product search')
    n_weak = args.weak_cols
    conf_order = np.argsort(post.max(1))
    weak = conf_order[:n_weak]
    alts = {c: list(np.argsort(-post[c])[:2]) for c in weak}
    import itertools
    tries = 0
    found = False
    for pattern in itertools.product(*[alts[c] for c in weak]):
        hyps = base.copy()
        for i, c in enumerate(weak):
            hyps[c] = pattern[i]
        tries += 1
        if check(assemble(hyps)):
            k = assemble(hyps)
            print(f'[+] KEY FOUND after {tries} combos: {k.hex()}')
            print(f'[+] true key: {key.hex()}  match={k == key}')
            found = True
            break
    if not found:
        print(f'[!] no key in {tries} combos - widen --weak-cols')
    print(f'[+] elapsed {(time.time()-t0):.0f}s')
    lq.close()


if __name__ == '__main__':
    main()