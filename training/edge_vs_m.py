#!/usr/bin/env python3
r"""edge_vs_m.py — live-board template evidence edge vs M-averaging (one pass).

Captures the SAME nonce up to M_max times (retry-fixed flat handling), then
measures the linear-template (LDA) hypothesis edge at M = 1, 2, 4, ..., M_max
by align-averaging the first M captures per nonce. Also reports the
residual-noise reduction factor — the direct proof the M-pool averaging is
actually delivering ~1/sqrt(M).

Why this is the decisive lever test for the new unmasked core:
  * edge(M=1)            -> does the core leak first-order S-box signal at all?
  * edge(M) / edge(1)    -> does averaging scale as ~sqrt(M) (independent noise)?
  * edge(M=64) > 0.1 nats -> the template attack is viable at this operating point.

If edge ~ 0 at M=1 AND M=64, the core is not leaking (capture timing, gain, or
RTL problem), not an attack problem. Sim mode is a smoke test only — the sim
noise model is self-inconsistent for templates (edge comes out negative).

Usage:
    .venv/bin/python training/edge_vs_m.py --profile-h5 Dataset/gain35_500.h5 \
        --gain 35 --M-max 64 --nonces 30 [--crypto-mhz 10]
"""
import argparse
import os
import sys
from datetime import datetime

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import labels as lab
from live_loop_transformer import TemplateEngine, N_COLS, N_HYPS


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--profile-h5', required=True,
                    help='template fit source (flat traces/keys/nonces h5)')
    ap.add_argument('--bitstream', default=os.path.join(
        ROOT, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--gain', type=int, default=35)
    ap.add_argument('--samples', type=int, default=1200)
    ap.add_argument('--M-max', type=int, default=64,
                    help='max traces averaged per nonce')
    ap.add_argument('--nonces', type=int, default=30,
                    help='distinct nonces to capture')
    ap.add_argument('--flat-tol', type=int, default=60,
                    help='consecutive flat traces tolerated before skip')
    ap.add_argument('--fit-k', type=int, default=300)
    ap.add_argument('--crypto-mhz', type=float, default=10.0)
    ap.add_argument('--sim', action='store_true',
                    help='use SimBoard (smoke test only, NOT a validation)')
    ap.add_argument('--out', default=None, help='raw capture h5')
    args = ap.parse_args()

    eng = TemplateEngine(args.profile_h5, fit_k=args.fit_k, window=args.samples)
    print(f'[+] template: {N_COLS} cols, mean alpha energy '
          f'{np.abs(eng.alphas).max(axis=1).mean():.4f}')

    key = os.urandom(16)
    if args.sim:
        from sim_board import SimBoard
        lq = SimBoard(args.profile_h5, key, column=0, amp=1.0, seed=1,
                      target='sbox64')
        print('[+] sim mode (SMOKE TEST ONLY)')
    else:
        import live_query
        lq = live_query.LiveQuery(args.bitstream, key, samples=args.samples,
                                  gain=args.gain, crypto_mhz=args.crypto_mhz)
        print(f'[+] live: gain {args.gain}, crypto {args.crypto_mhz} MHz, '
              f'samples {args.samples}, key {key.hex()[:8]}…')

    # ---- capture M_max traces per nonce (retry-fixed flat handling) ----
    rng = np.random.default_rng(0)
    cap = np.zeros((args.nonces, args.M_max, args.samples), dtype=np.float32)
    nonces = np.zeros((args.nonces, 16), dtype=np.uint8)
    n_good = np.zeros(args.nonces, dtype=int)
    for i in range(args.nonces):
        nonce = rng.integers(0, 256, 16, dtype=np.uint8).tobytes()
        pool, flat = [], 0
        while len(pool) < args.M_max and flat < args.flat_tol:
            trace, _ct = lq.query(nonce)
            if trace is None:
                flat += 1
                continue
            flat = 0
            pool.append(np.asarray(trace, dtype=np.float32))
        if not pool:
            print(f'  [!] nonce {i}: no good trace after {args.flat_tol} '
                  f'flats, skipping')
            continue
        n_good[i] = len(pool)
        for j in range(n_good[i]):
            cap[i, j] = pool[j]
        nonces[i] = np.frombuffer(nonce, np.uint8)
        print(f'  nonce {i:2d}: collected {n_good[i]:3d}/{args.M_max}', flush=True)

    if args.sim:
        lq.close()

    # ---- score at each M ----
    from preprocess import align_trace
    Ms = [1] + [2 ** e for e in range(1, 20) if 2 ** e <= args.M_max]
    hyps = lab.all_hypotheses()
    bits = np.unpackbits(np.frombuffer(key, np.uint8), bitorder='little')
    truth = (bits[:64].astype(int) << 1) | bits[64:].astype(int)   # (64,)

    edges = {M: [] for M in Ms}
    accs = {M: np.zeros(N_COLS) for M in Ms}
    noise = {M: [] for M in Ms}
    for i in range(args.nonces):
        n_g = int(n_good[i])
        if n_g < 2:
            continue
        al = np.stack([align_trace(cap[i, j], eng.mu) for j in range(n_g)])
        R = al - al.mean(0, keepdims=True)
        s1 = float(R.std())
        nb = nonces[i][None]
        for M in Ms:
            if M > n_g:
                continue
            avg = al[:M].mean(axis=0)
            ev = eng.evidence_all(avg, nb.tobytes())
            if ev is None:
                continue
            for c in range(N_COLS):
                llh = ev[c]
                edges[M].append(float(
                    llh[truth[c]] - llh[np.arange(N_HYPS) != truth[c]].mean()))
                accs[M][c] += int(llh.argmax() == truth[c])
            noise[M].append(float(R[:M].mean(0).std()) / max(s1, 1e-12))

    print()
    print(f'{"M":>4} {"edge(nats)":>12} {"argmax%":>9} {"noise_ratio":>12} '
          f'{"n_nonces":>9}')
    best = 0.0
    for M in Ms:
        if not edges[M]:
            continue
        em = float(np.mean(edges[M]))
        am = 100.0 * accs[M].mean() / args.nonces
        nm = float(np.mean(noise[M])) if noise[M] else float('nan')
        best = max(best, em)
        print(f'{M:>4} {em:>12.4f} {am:>8.1f}% {nm:>12.3f} '
              f'{len(edges[M]) // N_COLS:>9}')

    # ---- save raw captures ----
    import h5py
    out = args.out or os.path.join(
        ROOT, 'Dataset', 'edge_vs_m_%s.h5' % datetime.now().strftime('%Y%m%d_%H%M%S'))
    with h5py.File(out, 'w') as f:
        f.create_dataset('traces', data=cap)
        f.create_dataset('nonces', data=nonces)
        f.create_dataset('n_good', data=n_good)
        f.attrs['key'] = np.frombuffer(key, np.uint8)
        f.attrs['gain'] = args.gain
        f.attrs['crypto_mhz'] = args.crypto_mhz
        f.attrs['M_max'] = args.M_max
        f.attrs['profile_h5'] = args.profile_h5
    print(f'\n[+] raw captures saved: {out}')

    e1 = float(np.mean(edges[1])) if edges[1] else float('nan')
    e64 = float(np.mean(edges[args.M_max])) if edges.get(args.M_max) else float('nan')
    n64 = float(np.mean(noise[args.M_max])) if noise.get(args.M_max) else float('nan')
    a64 = 100.0 * accs[args.M_max].mean() / args.nonces if edges.get(args.M_max) \
        else float('nan')
    print(f'\nRESULT gain={args.gain} crypto_mhz={args.crypto_mhz} '
          f'edge_m1={e1:.4f} edge_m{args.M_max}={e64:.4f} '
          f'noise_ratio_m{args.M_max}={n64:.3f} '
          f'argmax_m{args.M_max}={a64:.1f} best_edge={best:.4f}')
    if args.crypto_mhz >= 10.0:
        print('DECISION: ' + (
            'VIABLE -> full template attack at this gain' if e64 > 0.1
            else ('MARGINAL -> try M_max=256 or lower crypto clock'
                  if e64 > 0.02 else 'NOT LEAKING -> capture-timing/RTL problem')))


if __name__ == '__main__':
    main()
