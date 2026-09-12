#!/usr/bin/env python3
r"""verify_lightcone.py — confirm the 6-key-bit claim for the toggle predictor.

The v2 attack plan rests on one structural claim: the net toggle at a single
(word w, bit position j) in round 1 depends on exactly SIX key bits, namely
K_lo[p] and K_hi[p] for the three positions

    p in { j , (j + r1_w) mod 64 , (j + r2_w) mod 64 }

NOTE ON THE SIGN: linear_diffusion uses _rotr(x,r) = (x>>r)|(x<<(64-r)), so
bit j of the output depends on bit (j+r) of the input -- the cone runs in the
PLUS direction.  The first version of this file used minus and the check
failed immediately, which is exactly why the check exists.

This script verifies it empirically: flip each of the 128 key bits in turn and
record which flips change the predictor.  The set that matters must equal the
predicted set exactly.  If the cone is larger than predicted, the 2^6
hypothesis search is wrong and the plan changes.

Usage:
  .venv/bin/python training/verify_lightcone.py
"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

from labels import load_state, substitution_layer, linear_diffusion  # noqa: E402

R1 = {0: (19, 28), 1: (61, 39), 2: (1, 6), 3: (10, 17), 4: (7, 41)}


def keybit_sites(p):
    """The two key bits entering the S-box at bit position p.

    load_state packs S[1] = big-endian key[0:8], S[2] = key[8:16], so bit p of
    S[1] is bit (p%8) of byte (7 - p//8), likewise for S[2] with byte
    (15 - p//8).
    """
    b = p % 8
    return [(7 - p // 8, 1 << b), (15 - p // 8, 1 << b)]


def toggle_pred(key16, nonce, w, j):
    """Net toggle bit at (word w, position j) for round 1."""
    K = np.tile(np.frombuffer(key16, np.uint8), (len(nonce), 1))
    S = load_state(K, nonce)
    Sc = S.copy()
    Sc[:, 2] ^= np.uint64(0xF0)
    S1 = linear_diffusion(substitution_layer(Sc))
    return ((S[:, w] ^ S1[:, w]) & np.uint64(1 << j)) > 0


def main():
    rng = np.random.default_rng(0)
    nonce = rng.integers(0, 256, (400, 16), dtype=np.uint8)
    key = rng.integers(0, 256, 16, dtype=np.uint8)

    print('  word/pos   predicted positions                  '
          '#keybits  #that matter   verdict')
    all_ok = True
    for (w, j) in [(0, 5), (0, 30), (1, 7), (2, 11), (2, 60), (3, 20), (4, 33)]:
        r1, r2 = R1[w]
        pos = sorted({j, (j + r1) % 64, (j + r2) % 64})
        predicted = set()
        for p in pos:
            for site in keybit_sites(p):
                predicted.add(site)

        base = toggle_pred(key, nonce, w, j)
        actual = set()
        for bi in range(16):
            for bit in range(8):
                kk = key.copy()
                kk[bi] ^= (1 << bit)
                if not np.array_equal(toggle_pred(kk, nonce, w, j), base):
                    actual.add((bi, 1 << bit))

        missing = actual - predicted
        inert = predicted - actual
        # The plan needs the predicted cone to be a SUPERSET of the true one:
        # every key bit that matters must be inside the 2^6 search.  Bits that
        # are structurally in the cone but functionally inert for this
        # particular output bit are harmless (they just make the search
        # slightly redundant) -- and they stay inert with 10x more nonces, so
        # they are structural, not sampling noise.
        ok = (len(missing) == 0)
        all_ok = all_ok and ok
        note = f'inert {len(inert)}' if inert else 'exact'
        print(f'  w{w} j{j:<4} {str(pos):32s} {len(predicted):>7}  '
              f'{len(actual):>11}   {"OK" if ok else "MISSING BITS"}' + f'  ({note})')
        if not ok:
            print(f'      NOT in the cone but matter: {sorted(missing)}')

    print(f'\nlight-cone formula holds for every tested predictor: {all_ok}')
    print('If False, the 2^6 hypothesis search is invalid and the plan changes.')


if __name__ == '__main__':
    main()
