#!/usr/bin/env python3
r"""kadd_acppa.py — full-key ACPPA: eliminate candidate keys with a beam search
driven by the KADD intermediate, terminate on ciphertext match.

The model reads an 8-byte HW fingerprint of the KADD state (S[3] after the
12-round init permutation + key XOR) from each power trace. A candidate full
key K predicts an 8-dim HW vector for any nonce (via the oracle). We keep a
beam of the top-K candidates by accumulated log-likelihood, mutate the losers,
and stop when the top candidate's ciphertext matches the board's — the loop the
user described: eliminate guessed keys by choosing the next input to the board.

Flow per query:
    select nonce (maximize predicted-HW separation across the beam)
    board -> trace + ciphertext
    model -> per-byte log-probs (8 x 9)
    score each candidate K: sum_b logP_b(HW_b(K, nonce) | trace)
    keep top beam, mutate losers, verify top candidate's ct vs board ct
    terminate: ct matches, or --max-queries exhausted

Usage:
    # virtual board (no hardware; gate before board time)
    .venv/bin/python training/kadd_acppa.py --attack --sim \
        --npz training/data/main_unmasked_merged.npz \
        --models 'training/models/main_unmasked_merged_c%i_kadd_mlp.pt' \
        --key 000102030405060708090a0b0c0d0e0f --max-queries 200
    # real board
    .venv/bin/python training/kadd_acppa.py --attack \
        --npz training/data/main_unmasked_merged.npz \
        --models 'training/models/main_unmasked_merged_c%i_kadd_mlp.pt' \
        --key <16-byte-hex> --max-queries 1000
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import labels as lab
from train import CNN, MLP
from attack import build_input
from ascon_ref import ascon_encrypt


class KaddProfiles:
    """8 per-byte KADD HW profiles: log_probs(byte, traces) -> (N, 9)."""

    def __init__(self, model_path_fmt, npz_path):
        self.models = []
        self.window = None
        for b in range(8):
            ckpt = torch.load(model_path_fmt % b, map_location='cpu')
            arch = ckpt['arch']
            n_out = len(ckpt['classes'])
            if arch == 'cnn2':
                m = CNN(3, n_out, [8, 16, 32, 32], 128)
            elif arch == 'cnn1':
                m = CNN(1, n_out, [8, 16, 32], 128)
            else:
                mlp_in = ckpt['state_dict']['net.0.weight'].shape[1]
                m = MLP(mlp_in, ckpt['hidden'], n_out)
            m.load_state_dict(ckpt['state_dict'])
            m.eval()
            self.models.append(m)
            self.window = ckpt['window']
        d = np.load(npz_path, allow_pickle=True)
        self.ref = d.get('ref')
        if self.ref is None:
            self.ref = d['traces'].mean(axis=0).astype(np.float32)
        self.arch = arch
        self.npz = npz_path

    def log_probs_all(self, trace):
        """(2000,) aligned+z-scored trace -> (8, 9) per-byte log-probs."""
        t = trace.astype(np.float64)
        if self.ref is not None:
            from preprocess import align_trace
            t = align_trace(t, self.ref)
        from preprocess import zscore
        t = zscore(t).astype(np.float32)[:self.window]
        out = np.empty((8, 9))
        for b, m in enumerate(self.models):
            with torch.no_grad():
                X = build_input(t[None], self.arch, self.window, m)
                out[b] = torch.log_softmax(m(X), dim=1)[0].numpy()
        return out


def candidate_hw(candidate_keys, nonce):
    """(C,16) uint8 candidate keys + (16,) nonce -> (C, 8) KADD byte HW."""
    n = np.frombuffer(bytes(nonce), dtype=np.uint8)[None]
    return lab.kadd_words_hw(candidate_keys, np.repeat(n, len(candidate_keys), axis=0))


def score_beam(logp_all, hw):
    """logp_all (8,9) per-byte; hw (C,8) predicted HW per candidate -> (C,) log-score."""
    C = len(hw)
    score = np.zeros(C)
    for b in range(8):
        score += logp_all[b, hw[:, b]]
    return score


def pick_separating_nonce(candidates, rng, n_tries=50):
    """Pick a nonce whose predicted KADD HW vectors separate the beam most.

    Candidates (C,16) uint8. Enumerate random nonces; pick max sum of pairwise
    HW-vector L1 distance across the beam (a query that makes the candidates
    look different carries the most evidence).
    """
    best, best_score = None, -1.0
    for _ in range(n_tries):
        nonce = rng.bytes(16)
        hw = candidate_hw(candidates, nonce)              # (C,8)
        spread = float(np.abs(hw[:, None, :] - hw[None, :, :]).sum())
        if spread > best_score:
            best, best_score = nonce, spread
    return best


def mutate(candidates, rng, flip=2):
    """Child of a parent key: flip `flip` random bits."""
    out = candidates.copy()
    for i in range(len(out)):
        nflip = rng.integers(1, flip + 1)
        for _ in range(nflip):
            b = rng.integers(0, 16)
            bit = rng.integers(0, 8)
            out[i, b] ^= (1 << bit)
    return out


def run_attack(prof, query, key, max_queries, beam=256,
               n_seed=1024, seed=0, quiet=False):
    """One attack: returns (cracked: bool, queries: int, top_correct: bool)."""
    rng = np.random.default_rng(seed)
    t0 = time.time()
    # initial beam: random keys
    cand = rng.integers(0, 256, size=(n_seed, 16), dtype=np.uint8)
    key_b = np.frombuffer(bytes(key), dtype=np.uint8)[None]
    log_acc = np.full(n_seed, 0.0)

    for q in range(1, max_queries + 1):
        if len(cand) > beam:
            keep_idx = np.argsort(log_acc)[-beam:]
            cand, log_acc = cand[keep_idx], log_acc[keep_idx]
        nonce = pick_separating_nonce(cand, rng)
        trace, ct = query(nonce)
        if trace is None:
            continue
        logp = prof.log_probs_all(trace)
        hw = candidate_hw(cand, nonce)
        log_acc += score_beam(logp, hw)
        # verify top candidate against the board's ciphertext
        top = int(np.argmax(log_acc))
        try:
            exp = ascon_encrypt(bytes(cand[top]), bytes(nonce),
                                b'\x00' * 4, b'\x00' * 16)
            if bytes(ct) == exp:
                if not quiet:
                    print(f'[+] CRACKED at query {q}: key {bytes(cand[top]).hex()} '
                          f'[{time.time()-t0:.0f}s]')
                return True, q, True
        except Exception:
            pass
        # replace the worst half with mutated survivors
        n = len(cand)
        if q % 5 == 0:
            k = max(8, n // 2)
            kids = mutate(cand[np.argsort(log_acc)[-k:]], rng)
            replace = np.argsort(log_acc)[:k]
            cand[replace] = kids
            log_acc[replace] = log_acc[np.argsort(log_acc)[-k:]] * 0.9
        if not quiet and (q % 25 == 0 or q <= 3):
            top_bits = sum(
                (bytes(cand[top])[b] == key_b[0, b]) for b in range(16))
            print(f'  q {q:4d}  beam {n:3d}  top-byte-match {top_bits}/16  '
                  f'[{time.time()-t0:.0f}s]')

    top = int(np.argmax(log_acc))
    top_correct = bool(np.array_equal(cand[top], key_b[0]))
    return False, max_queries, top_correct


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--attack', action='store_true')
    ap.add_argument('--npz', default='training/data/main_unmasked_merged.npz')
    ap.add_argument('--models', required=True,
                    help='printf format with %i for the byte (0..7)')
    ap.add_argument('--key', required=True)
    ap.add_argument('--max-queries', type=int, default=1000)
    ap.add_argument('--beam', type=int, default=256)
    ap.add_argument('--n-seed', type=int, default=1024)
    ap.add_argument('--nkeys', type=int, default=1,
                    help='number of random keys to attack (eval mode)')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--sim', action='store_true')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset',
                                                     'main_unmasked_merged.h5'))
    ap.add_argument('--sim-amp', type=float, default=1.0)
    ap.add_argument('--gain', type=int, default=-2)
    ap.add_argument('--offset', type=int, default=700)
    ap.add_argument('--std-floor', type=float, default=0.01)
    args = ap.parse_args()

    prof = KaddProfiles(args.models, args.npz)
    print(f'[+] KADD profiles loaded (window {prof.window}, {prof.arch})')

    if args.sim:
        from sim_board import SimBoard
        key0 = bytes.fromhex(args.key)
        lq = SimBoard(args.sim_h5, key0, column=0, amp=args.sim_amp,
                      seed=args.seed, samples=2000)
        print(f'[+] SIM BOARD amp {args.sim_amp}x — '
              f'gate before burning board time')
        print(f'[!] NOTE: SimBoard currently models S-box leakage; KADD '
              f'leakage extension required for a faithful gate')
    else:
        import live_query
        lq = live_query.LiveQuery(args.bitstream, bytes.fromhex(args.key),
                                  gain=args.gain, offset=args.offset,
                                  std_floor=args.std_floor)

    results = []
    for i in range(args.nkeys):
        key = bytes.fromhex(args.key) if args.nkeys == 1 else os.urandom(16)
        if args.nkeys > 1:
            print(f'\n=== attacking key {i+1}/{args.nkeys}: {key.hex()} ===')
        cracked, queries, top_correct = run_attack(
            prof, lq.query, key, args.max_queries, args.beam, seed=args.seed + i)
        results.append({'key': key.hex(), 'cracked': bool(cracked),
                        'queries': int(queries), 'top_correct': bool(top_correct)})
        print(f'  -> cracked={cracked} queries={queries} top_correct={top_correct}')

    lq.close()
    out = os.path.join(ROOT, 'training', 'results', 'kadd_acppa.json')
    with open(out, 'w') as f:
        json.dump({'nkeys': len(results), 'max_queries': args.max_queries,
                   'beam': args.beam, 'sim': bool(args.sim),
                   'sim_amp': args.sim_amp if args.sim else None,
                   'results': results}, f, indent=2)
    if len(results) > 1:
        rate = sum(r['cracked'] for r in results) / len(results)
        mean_q = np.mean([r['queries'] for r in results if r['cracked']] or [0])
        print(f'\n[+] crack rate {rate*100:.1f} % over {len(results)} keys, '
              f'mean queries-to-crack {mean_q:.0f}')
    print(f'[+] wrote {out}')


if __name__ == '__main__':
    main()
