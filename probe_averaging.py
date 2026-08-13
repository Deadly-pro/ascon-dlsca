#!/usr/bin/env python3
r"""probe_averaging.py — Phase 0: validate the nonce-repetition averaging SNR lever.

Captures the SAME separating nonce 64 times per round, then subsamples and
averages at M in {1, 4, 16, 64} to measure:

  noise_std  : mean per-sample std across the M captures (noise floor at M)
  gain dB    : measured noise reduction vs M=4, vs theory 10*log10(4/M)
  rank1      : fraction of rounds where the true 2-bit key hypothesis tops the score
  mean_rank  : average rank of the true hypothesis (1 best .. 4 worst)
  lr_margin  : mean log-score of true hyp minus best other hyp (nats; >0 = discrimination)

The M=1 numbers are the amp=1 baseline (per-trace rank-1 ~ chance, which is why
ACPPA locked onto wrong bits). If averaging buys ~10*log10(M) dB, rank1 should
climb toward 1.0 and lr_margin toward positive at M=16-64.

Usage (board session, gain from pilot_gain):
    python3 probe_averaging.py -b vivado_ascon/ascon_cw305_top.bit --gain 15
"""
import argparse
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from adaptive import Profile, score_trace, pick_separating_nonce
import labels as lab


def noise_std(captures):
    """Mean over samples of the std across captures (per-sample noise floor)."""
    return float(np.std(np.stack(captures), axis=0).mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('-b', '--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--model', default=os.path.join(ROOT, 'training', 'models',
                    'main_unmasked_merged_c0_sbox_cnn1.pt'))
    ap.add_argument('--npz', default=os.path.join(ROOT, 'training', 'data',
                    'main_unmasked_merged.npz'))
    ap.add_argument('--key', default='000102030405060708090a0b0c0d0e0f')
    ap.add_argument('--column', type=int, default=0)
    ap.add_argument('--gain', type=int, default=15)
    ap.add_argument('--rounds', type=int, default=16)
    ap.add_argument('--M', default='1 4 16 64')
    args = ap.parse_args()

    Ms = [int(m) for m in args.M.split()]
    assert Ms[0] == 1, 'M list must start at 1 (baseline)'
    M_pool = max(Ms)
    prof = Profile(args.model, args.npz)
    col = args.column
    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('--key must be 16 bytes hex')

    hyps = lab.all_hypotheses()
    k0 = (key[col // 8] >> (col % 8)) & 1
    k1 = (key[8 + col // 8] >> (col % 8)) & 1
    true_hyp = int(np.flatnonzero((hyps[:, 0] == k0) & (hyps[:, 1] == k1))[0])

    import live_query
    lq = live_query.LiveQuery(args.bitstream, key, gain=args.gain)
    try:
        rng = np.random.default_rng(0)
        nonces = [pick_separating_nonce(col, prof.support, rng)
                  for _ in range(args.rounds)]
        print(f'[+] probe: col {col}, {args.rounds} rounds x {M_pool} captures, '
              f'M in {Ms}, gain {args.gain} dB')
        print(f'    key bits k[{col % 8}]={k0}, k[8+col%8]={k1}  ->  true hyp {true_hyp}')
        print(f'    profile {prof.arch}  support {prof.classes}  window {prof.window}')
        print(f'  {"M":>3} {"noise_std":>10} {"gain(dB)":>9} {"rank1":>6} '
              f'{"mean_rank":>9} {"lr_margin":>10}  [s]')

        pools = []          # per round: list of M_pool raw captures
        t_start = time.time()
        for r, nonce in enumerate(nonces):
            pool = []
            while len(pool) < M_pool:
                tr, _ct = lq.query(nonce)
                if tr is None:
                    continue
                pool.append(tr.astype(np.float64))
            pools.append(pool)

        noise4 = None
        for M in Ms:
            ranks, margins, noises = [], [], []
            t0 = time.time()
            for nonce, pool in zip(nonces, pools):
                caps = pool[:M]
                avg = np.mean(caps, axis=0)
                if M > 1:
                    noises.append(noise_std(caps))
                t = prof.preprocess(avg)
                if t is None:
                    continue
                logp = prof.log_probs(t[None])[0]
                sc = score_trace(logp, nonce, col, prof.classes)
                order = np.argsort(sc)[::-1]
                ranks.append(int(np.flatnonzero(order == true_hyp)[0]) + 1)
                margins.append(float(sc[true_hyp] - sc[order[0]]))
            noise = float(np.mean(noises)) if noises else float('nan')
            if M == 4:
                noise4 = noise
            gain = -10.0 * np.log10(noise / noise4) if (M > 4 and noise4) else 0.0
            print(f'  {M:>3} {noise:>10.5f} {gain:>9.1f} '
                  f'{np.mean([r_ == 1 for r_ in ranks]):>6.2f} '
                  f'{np.mean(ranks):>9.2f} {np.mean(margins):>10.3f} '
                  f'[{time.time() - t0:.0f}s]')
        print(f'[+] done in {time.time() - t_start:.0f}s; '
              f'theory gain vs M=4: +6 dB @16, +12 dB @64')
    finally:
        lq.close()


if __name__ == '__main__':
    main()
