#!/usr/bin/env python3
r"""step5_mavg_eval.py — M-averaged full-key recovery evaluation.

The method this evaluates (designed after the offline low-SNR verdict showed
per-trace M=1 signal sits at the permutation null):

  Phase A (profiling):  M-averaged traces at RANDOM keys. Train per-column
                        profiles in the averaged domain (LDA on SOST POI
                        features, pooled covariance + shrinkage).
  Phase B (attack):     M-averaged traces at a few FIXED keys, many nonces
                        each. For each key/column, score the 4 key-bit
                        hypotheses by summed log-likelihood over the nonces,
                        assemble top-1 (+ bounded brute over weak columns),
                        VERIFY against the stored ciphertext readback.

Both phases come from the SAME capture session, so the profiling-domain gap
that killed the Sep-9 run is designed out. Pure numpy/scipy — no torch —
so it runs anywhere (including the WSL board PC venv).

Inputs (collect_dataset.py schema, M>1 stored means):
  --phaseA  h5 with random keys (--avg-m M)
  --phaseB  one or more h5 globs, each captured with --key <fixed> (same M)
Outputs:
  results/step5_mavg_eval.json + console verdict per key.

Usage:
  .venv/bin/python training/step5_mavg_eval.py \
      --phaseA board_session/mavg/phaseA_randomkeys.h5 \
      --phaseB 'board_session/mavg/phaseB_key*.h5' \
      [--window 2000] [--poi 64] [--max-weak 12]
"""
import argparse
import glob
import itertools
import json
import os
import sys
import time

import h5py
import numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import ascon_ref as ar                       # noqa: E402
import labels as lab                         # noqa: E402
from preprocess import align, zscore         # noqa: E402
from step1_cpa_hd import col_bits, sbox5, true_hyp  # noqa: E402

AD = b'\x00' * 4
PT = b'\x00' * 4


# ---------------------------------------------------------------- data loading
def load_h5(path, window):
    with h5py.File(path, 'r') as f:
        tr = f['traces'][:].astype(np.float64)
        keys = f['keys'][:]
        nonces = f['nonces'][:]
        cts = f['ciphertexts'][:] if 'ciphertexts' in f else None
        m_avg = int(f.attrs.get('avg_m', 1))
    tr, ref, shifts, lo, hi = align(tr, k=min(200, len(tr)))
    win = min(window, tr.shape[1])
    tr = zscore(tr[:, :win]).astype(np.float32)
    return dict(traces=tr, keys=keys, nonces=nonces, cts=cts,
                avg_m=m_avg, ref=ref.astype(np.float32), window=win)


def hw_pred(keys, nonces, c):
    """(N, 4) predicted round-1 S-box output HW per hypothesis h=2*b0+b1."""
    n = len(keys)
    out = np.empty((n, 4))
    for h in range(4):
        b0, b1 = (h >> 1) & 1, h & 1
        kk = keys.copy()
        m = np.uint8(1 << (c % 8))
        kk[:, c % 8] = (kk[:, c % 8] | m) if b0 else (kk[:, c % 8] & np.uint8(255 - int(m)))
        kk[:, 8 + c % 8] = (kk[:, 8 + c % 8] | m) if b1 else (kk[:, 8 + c % 8] & np.uint8(255 - int(m)))
        S = lab.load_state(kk, nonces)
        S[:, 2] ^= np.uint64(0xF0)
        cols = sbox5(col_bits(S, c))
        out[:, h] = np.array([bin(int(v)).count('1') for v in cols])
    return out


# ---------------------------------------------------------------- profile (A)
def sost_pois(traces, classes, k):
    t = traces.astype(np.float64)
    t -= t.mean(axis=0, keepdims=True)
    us = np.unique(classes)
    mu = np.stack([t[classes == u].mean(axis=0) for u in us])
    d2 = np.zeros(traces.shape[1])
    for i in range(len(us)):
        for j in range(i + 1, len(us)):
            d2 += (mu[i] - mu[j]) ** 2
    return np.argsort(-d2)[:k]


class ColumnProfile:
    """LDA (pooled covariance, shrunk) on POI features for one column."""

    def __init__(self, feats, classes, shrink=0.1):
        self.us = np.unique(classes)
        self.mu = np.stack([feats[classes == u].mean(axis=0) for u in self.us])
        cov = np.zeros((feats.shape[1], feats.shape[1]))
        for i, u in enumerate(self.us):
            Xc = feats[classes == u] - self.mu[i]
            cov += Xc.T @ Xc
        cov /= max(1, len(feats) - len(self.us))
        # shrink toward diagonal (Ledoit-Wolf style, fixed intensity)
        diag = np.diag(cov).copy()
        cov = (1 - shrink) * cov + shrink * np.diag(diag)
        cov += 1e-6 * np.eye(cov.shape[0])
        self.cov_inv = np.linalg.inv(cov)
        self.logdet = np.linalg.slogdet(cov)[1]
        self.prior = np.array([(classes == u).mean() for u in self.us])

    def loglik(self, feats):
        """(N, C) log p(class u | x) up to a constant, classes in self.us."""
        d = feats[:, None, :] - self.mu[None, :, :]        # (N, C, D)
        q = np.einsum('ncd,de,nce->nc', d, self.cov_inv, d)
        return -0.5 * q - 0.5 * self.logdet + np.log(self.prior)[None, :]

    def class_loglik_for(self, feats, class_idx):
        """log p(x | class) for arbitrary class labels (mapped into self.us;
        -inf where the class was unseen in profiling). class_idx: (N, 4)
        array whose entries are HW class indices (0..5)."""
        pos = {int(u): i for i, u in enumerate(self.us)}
        out = self.loglik(feats)                          # (N, C)
        N = out.shape[0]
        ci = np.asarray(class_idx)
        assert ci.shape == (N, 4), f'class_idx shape {ci.shape} vs N={N}'
        res = np.full((N, 4), -np.inf)
        for j in range(4):
            for n in range(N):
                i = pos.get(int(ci[n, j]))
                if i is not None:
                    res[n, j] = out[n, i]
        return res


def hyp_pois(traces, keys, nonces, c, k):
    """Multivariate POI for column c: rank samples by between-hypothesis
    variance / within-hypothesis variance (F-ratio) using the TRUE key-bit
    hypothesis of each Phase-A trace (keys are known here). This targets
    key-bit discrimination directly, unlike 6-class HW SOST which is
    dominated by the other 63 columns' activity."""
    th = true_hyp(keys, c).astype(int)                    # (N,) 0..3
    t = traces.astype(np.float64)
    us = np.unique(th)
    mu = np.stack([t[th == u].mean(axis=0) for u in us])  # (4, S)
    # within-hyp variance per sample
    wv = np.zeros(traces.shape[1])
    for u in us:
        wv += t[th == u].var(axis=0)
    wv /= max(1, len(t))
    # between-hyp variance per sample
    bv = mu.var(axis=0)
    fr = bv / np.maximum(wv, 1e-12)
    return np.argsort(-fr)[:k]


def train_profiles(A, poi_k, max_train=4000):
    """Train 64 column profiles on Phase-A averaged traces."""
    traces, keys, nonces = A['traces'], A['keys'], A['nonces']
    labels = lab.round1_sbox_hw(keys, nonces)             # (N, 64)
    profiles, pois = {}, {}
    t0 = time.time()
    for c in range(64):
        poi = hyp_pois(traces, keys, nonces, c, poi_k)
        y = labels[:, c]
        pois[c] = poi
        profiles[c] = ColumnProfile(traces[:max_train][:, poi], y[:max_train])
        if c % 16 == 0:
            print(f'  profile col {c:2d}  poi {poi_k}  ({time.time()-t0:.0f}s)',
                  flush=True)
    return profiles, pois, labels


# ---------------------------------------------------------------- scoring (B)
def cpa_check(traces, keys, nonces, c):
    """Profile-free per-key CPA at column c. Returns per-key dict of
    true-hyp rank + best |r| + permuted null p-value."""
    th = true_hyp(keys, c)
    p = hw_pred(keys, nonces, c)                          # (N, 4)
    out = []
    rng = np.random.default_rng(0)
    for k in np.unique([bytes(x.tobytes()) for x in keys]):
        idx = np.array([i for i, kk in enumerate(keys)
                        if kk.tobytes() == k])
        for h in range(4):
            pass
        preds = {h: p[idx, h].astype(np.float64) for h in range(4)}
        res = {}
        for h in range(4):
            v = preds[h] - preds[h].mean()
            t = traces[idx].astype(np.float64)
            t -= t.mean(axis=0, keepdims=True)
            ts = t.std(axis=0)
            ts[ts < 1e-12] = np.inf
            r = np.abs(t.T @ v / (np.maximum(v.std(), 1e-12) *
                                  np.sqrt(len(idx)) * ts))
            res[h] = r
        # null: permute nonce order (destroys hyp<->trace link)
        nullmax = []
        for _ in range(20):
            perm = rng.permutation(len(idx))
            v = preds[0][perm] - preds[0][perm].mean()
            t = traces[idx].astype(np.float64)
            t -= t.mean(axis=0, keepdims=True)
            ts = t.std(axis=0)
            ts[ts < 1e-12] = np.inf
            nullmax.append(np.abs(t.T @ v / (np.maximum(preds[0].std(), 1e-12) *
                                              np.sqrt(len(idx)) * ts)).max())
        maj = int(np.bincount(th[idx], minlength=4).argmax())
        best = {h: float(res[h].max()) for h in range(4)}
        rank = int(sum(1 for h in range(4) if best[h] > best[maj])) + 1
        out.append(dict(rank=rank, best_r=best, null_p99=float(
            np.quantile(nullmax, 0.99)), true_maj=maj))
    return out


def score_key(traces, keys, nonces, cts, profiles, pois):
    """Per-column hypothesis scores for one fixed key; assemble + verify."""
    n = len(traces)
    scores = np.zeros((64, 4))
    percol = []
    for c in range(64):
        p = hw_pred(keys, nonces, c)                      # (N, 4) classes
        prof = profiles[c]
        ll = prof.class_loglik_for(traces[:, pois[c]], p)  # (N, 4)
        scores[c] = ll.sum(axis=0)
        srt = np.sort(scores[c])[::-1]
        percol.append(dict(margin=float(srt[0] - srt[1]),
                           top=int(scores[c].argmax())))
    # true hyp ranks (for diagnostics when the key is known to us)
    w1 = int(ar.bytes_to_int(keys[0][0:8]))
    w2 = int(ar.bytes_to_int(keys[0][8:16]))
    true_h = np.array([(((w1 >> c) & 1) << 1) | ((w2 >> c) & 1)
                       for c in range(64)])
    top = scores.argmax(axis=1)
    n_correct = int((top == true_h).sum())

    # assembly with bounded brute force over the weakest columns,
    # verified against the stored 16-byte readback of nonce[0]
    def verify_ct16(cand_key):
        try:
            return bytes(ar.fpga_expected(bytes(cand_key),
                                          bytes(nonces[0]))) == \
                bytes(cts[0].tobytes())
        except Exception:
            return False

    srt = np.sort(scores, axis=1)
    margin = srt[:, -1] - srt[:, -2]
    order = np.argsort(margin)                            # weakest first
    recovered, n_verify, k_weak = None, 0, None
    for kk in range(0, 13):
        weak = list(order[:kk])
        strong = {c: int(top[c]) for c in range(64) if c not in weak}
        for combo in itertools.product(range(4), repeat=kk):
            col_hyp = dict(strong)
            col_hyp.update({cc: h for cc, h in zip(weak, combo)})
            w1c = w2c = 0
            for cc in range(64):
                w1c |= ((col_hyp[cc] >> 1) & 1) << cc
                w2c |= (col_hyp[cc] & 1) << cc
            cand = ar.int_to_bytes(w1c, 8) + ar.int_to_bytes(w2c, 8)
            n_verify += 1
            if verify_ct16(cand):
                recovered = cand
                k_weak = kk
                break
        if recovered:
            break
    return dict(n_correct_top1=n_correct, true_h=true_h.tolist(),
                top=top.tolist(), margins=[p['margin'] for p in percol],
                recovered=(recovered.hex() if recovered else None),
                n_verify=n_verify, k_weak=k_weak)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--phaseA', required=True)
    ap.add_argument('--phaseB', required=True, help='glob of fixed-key h5s')
    ap.add_argument('--window', type=int, default=2000)
    ap.add_argument('--poi', type=int, default=64)
    ap.add_argument('--max-weak', type=int, default=12)
    ap.add_argument('--out', default='results/step5_mavg_eval.json')
    args = ap.parse_args()

    print(f'[1/4] loading Phase A: {args.phaseA}')
    A = load_h5(args.phaseA, args.window)
    print(f'  {len(A["traces"])} traces x {A["window"]} avg_m={A["avg_m"]}')
    print(f'[2/4] training 64 column profiles (POI={args.poi})')
    profiles, pois, labelsA = train_profiles(A, args.poi)

    # Phase-A held-out sanity: per-column top-1 accuracy vs majority floor
    nA = len(A['traces'])
    half = nA // 2
    accs, floors = [], []
    for c in range(64):
        poi = pois[c]
        y = labelsA[:, c]
        prof = ColumnProfile(A['traces'][:half][:, poi], y[:half])
        ll = prof.loglik(A['traces'][half:][:, poi])
        pred = prof.us[ll.argmax(axis=1)]
        accs.append(float((pred == y[half:]).mean()))
        floors.append(float(np.bincount(y[half:]).max() / (nA - half)))
    accs, floors = np.array(accs), np.array(floors)
    gate_above = int((accs > floors + 0.05).sum())
    print(f'[gate] Phase-A held-out: mean acc {accs.mean()*100:.1f}% vs '
          f'floor {floors.mean()*100:.1f}%  |  cols >floor+5pts: '
          f'{gate_above}/64  ->  {"GO" if gate_above >= 8 else "NO-GO"}')

    print(f'[3/4] scoring Phase B keys: {args.phaseB}')
    res = {'phaseA': {'n': nA, 'avg_m': A['avg_m'], 'poi': args.poi,
                      'mean_acc': float(accs.mean()),
                      'mean_floor': float(floors.mean()),
                      'cols_above_floor5': gate_above,
                      'accs': accs.round(4).tolist()},
           'keys': []}
    bfiles = sorted(glob.glob(args.phaseB))
    if not bfiles:
        sys.exit(f'no Phase B files match {args.phaseB}')
    for bf in bfiles:
        B = load_h5(bf, args.window)
        key = bytes(B['keys'][0])
        print(f'  key {key.hex()}  ({len(B["traces"])} nonces, '
              f'avg_m={B["avg_m"]})')
        entry = {'file': bf, 'key': key.hex(), 'n_nonces': len(B['traces'])}
        # profile-free CPA diagnostics (column 0..3 sample + all-col summary)
        cpa_ranks = []
        for c in range(64):
            ck = cpa_check(B['traces'], B['keys'], B['nonces'], c)
            cpa_ranks.append(ck[0]['rank'])
        entry['cpa_rank1_cols'] = int((np.array(cpa_ranks) == 1).sum())
        entry['cpa_ranks'] = cpa_ranks
        # profiled scoring + assembly + verification
        r = score_key(B['traces'], B['keys'], B['nonces'], B['cts'],
                      profiles, pois)
        entry.update(r)
        entry['recovered'] = r['recovered']
        status = ('RECOVERED (verified by re-encryption)'
                  if r['recovered'] == key.hex() else
                  ('recovered-MISMATCH' if r['recovered'] else 'not recovered'))
        print(f'    top-1 columns correct: {r["n_correct_top1"]}/64  '
              f'CPA rank-1: {entry["cpa_rank1_cols"]}/64  -> {status} '
              f'(verify oracle calls: {r["n_verify"]}, weak brute {r["k_weak"]})')
        res['keys'].append(entry)

    nk = len(res['keys'])
    nrec = sum(1 for k in res['keys'] if k['recovered'] == k['key'])
    ncol = [k['n_correct_top1'] for k in res['keys']]
    res['summary'] = {
        'n_keys': nk, 'keys_recovered': nrec,
        'mean_cols_correct_top1': float(np.mean(ncol)) if ncol else 0.0,
        'bits_recovered_top1_mean': float(np.mean(ncol) * 2) if ncol else 0.0,
    }
    os.makedirs(os.path.dirname(args.out) or '.', exist_ok=True)
    with open(args.out, 'w') as f:
        json.dump(res, f, indent=1)
    print(f'\n[4/4] SUMMARY: {nrec}/{nk} keys FULLY RECOVERED  |  '
          f'mean top-1 columns {res["summary"]["mean_cols_correct_top1"]:.1f}'
          f'/64 ({res["summary"]["bits_recovered_top1_mean"]:.0f} bits)  |  '
          f'Phase-A gate {gate_above}/64 cols above floor+5')
    print(f'-> {args.out}')


if __name__ == '__main__':
    main()
