#!/usr/bin/env python3
r"""offline_template_attack.py — full key-recovery simulation of the linear
template attack on REAL held-out board traces (key-disjoint episode split).

Fits the per-column sbox64 template on the first N_FIT_EP episodes of a flat
traces/keys/nonces h5, then replays the naive-Bayes accumulation over each
held-out episode (fresh random key, 60 traces each) exactly as the live loop
would: evidence_all -> log-evidence accumulation -> argmax hypothesis per
column -> compare to the true 2 key bits.

This is the honest offline number for the next board session: at gain 55 M=1
the session traces were captured on the real unmasked core, so a positive
crack rate here transfers to the board. M-averaging is NOT in this data
(nonces all distinct); its sqrt(M) edge gain was measured separately in
probe_averaging.py.

Usage:
    .venv/bin/python training/offline_template_attack.py \
        --h5 Dataset/session_unmasked_flat.h5 --fit-eps 30
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from live_loop_transformer import TemplateEngine, N_COLS, N_HYPS


def episode_bounds(keys):
    k = keys.reshape(len(keys), -1).view('S16').ravel()
    b = np.where(k[1:] != k[:-1])[0]
    return np.concatenate([[0], b + 1, [len(keys)]])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--h5', default=os.path.join(ROOT, 'Dataset',
                                                 'session_unmasked_flat.h5'))
    ap.add_argument('--fit-eps', type=int, default=30,
                    help='first N episodes used to fit the template')
    args = ap.parse_args()

    import h5py
    with h5py.File(args.h5, 'r', locking=False) as f:
        traces = f['traces'][:].astype(np.float64)
        keys = f['keys'][:]
        nonces = f['nonces'][:]
    n, T = traces.shape
    bounds = episode_bounds(keys)
    n_ep = len(bounds) - 1
    assert n_ep >= args.fit_eps + 1, \
        f'{n_ep} episodes found, need >= {args.fit_eps + 1}'
    print(f'[+] {n} traces x {T} samples, {n_ep} episodes '
          f'({np.diff(bounds)[0]} traces each)')
    fit0, fit1 = bounds[0], bounds[args.fit_eps]
    atk0, atk1 = fit1, bounds[-1]
    print(f'[+] fit template on {args.fit_eps} eps ({fit1 - fit0} traces), '
          f'attack {n_ep - args.fit_eps} eps ({atk1 - atk0} traces), '
          f'KEY-DISJOINT')

    eng = TemplateEngine.from_arrays(traces[fit0:fit1], keys[fit0:fit1],
                                     nonces[fit0:fit1], window=T)
    print(f'[+] template fit: {N_COLS} cols, mean alpha energy '
          f'{np.abs(eng.alphas).max(axis=1).mean():.4f}')

    # truth per trace: hypothesis index = 2*bit(c) + bit(64+c)
    bits = np.unpackbits(np.frombuffer(keys.tobytes(), np.uint8),
                         bitorder='little').reshape(-1, 128)
    truth = (bits[:, :64] << 1) | bits[:, 64:]                 # (n,64)

    match_curve = np.full((n_ep - args.fit_eps, 60), np.nan)
    cracked = np.zeros((n_ep - args.fit_eps, 60), dtype=int)
    ep_keys = np.unique(keys[atk0:atk1], axis=0)
    acc = np.zeros((N_COLS, N_HYPS))                            # log-evidence
    n_done = 0
    for ei, ep in enumerate(range(args.fit_eps, n_ep)):
        acc[:] = 0.0
        a, b = bounds[ep], bounds[ep + 1]
        for q in range(b - a):
            tr = traces[a + q]
            nn = nonces[a + q]
            ev = eng.evidence_all(tr, nn.tobytes())
            if ev is None:
                match_curve[ei, q:] = np.nan
                continue
            acc += ev
            top = acc.argmax(axis=1)                            # (64,)
            tq = truth[a + q]
            m = 100.0 * (1 - (top != tq).sum() / N_COLS)
            match_curve[ei, q] = m
            cracked[ei, q] = int((top == tq).sum())
        done_q = next((qq for qq in range(b - a)
                       if cracked[ei, qq] == N_COLS), None)
        ok = cracked[ei, -1]
        if ok == N_COLS:
            n_done += 1
        print(f'  ep {ep:2d}  key {bytes(ep_keys[ei]).hex()[:8]}…  '
              f'cracked {ok:2d}/64  at-q {done_q}', flush=True)

    mean = np.nanmean(match_curve, axis=0)
    n_held = match_curve.shape[0]
    print(f'\n[+] M=1, gain-55 held-out real traces '
          f'({args.fit_eps}-ep template):')
    for q in (10, 20, 30, 40, 50, 59):
        print(f'  q {q:2d}: mean bit-match {mean[q]:5.1f}%  '
              f'full-key cracked {n_done}/{n_held}')
    print(f'[+] mean over last q: {mean[-1]:.1f}% (chance 25%)')
    print(f'[+] full keys cracked: {n_done}/{n_held}')
    print(f'[+] M-averaging (nonce repeat, align-before-avg) buys ~sqrt(M) '
          f'edge: M=64 target ~23 q/col per probe_averaging scaling')


if __name__ == '__main__':
    main()
