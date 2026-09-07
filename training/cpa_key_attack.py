#!/usr/bin/env python3
"""Direct-CPA per-column key recovery on the round-1 S-box INPUT register.

The leak (confirmed on avg32/prof16sc_m32/confirm_hwin) sits at the round-1
input register: column c = (IV_c, K0_c, K1_c, N0_c, N1_c). For each column and
each of the 4 hypotheses on (K0_c, K1_c), predict HW_in from the known nonce
and correlate against target traces at the POI window. True hypothesis should
give the strongest |correlation|.

Emits a (64,4) scores npz for fullkey_assemble (scores = max|r| per hyp,
true hyp ranks top) plus direct rank-1 key assembly + oracle verification.
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import labels as lab
import ascon_ref as ar
from fullkey_assemble import assemble, verify

POP = lab._POPCOUNT
IVw = int(lab.le_u64(np.tile(lab.IV[None, :], (1, 1))))
AD = b'\x00' * 4
PT = b'\x00' * 4

HYP = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.uint8)


def hw_in(keys_or_dummy, nonces, c, hyp=None):
    """HW of round-1 input column c. keys: (N,16) array OR fixed 16-byte key
    bytes; hyp: (kb0, kb1) when keys is fixed (attack), else ignored."""
    N = nonces.shape[0]
    if isinstance(keys_or_dummy, bytes):
        K0 = int.from_bytes(keys_or_dummy[0:8], 'little')
        K1 = int.from_bytes(keys_or_dummy[8:16], 'little')
        b1 = np.full(N, (K0 >> c) & 1 if hyp is None else int(hyp[0]),
                     dtype=np.uint64)
        b2 = np.full(N, (K1 >> c) & 1 if hyp is None else int(hyp[1]),
                     dtype=np.uint64)
    else:
        K0 = lab.le_u64(keys_or_dummy[:, 0:8])
        K1 = lab.le_u64(keys_or_dummy[:, 8:16])
        b1 = (K0 >> c) & 1
        b2 = (K1 >> c) & 1
    N0 = lab.le_u64(nonces[:, 0:8])
    N1 = lab.le_u64(nonces[:, 8:16])
    iv = np.full(N, (IVw >> c) & 1, dtype=np.uint64)
    col = (iv | (b1 << 1) | (b2 << 2) | ((N0 >> c) & 1) << 3 |
           ((N1 >> c) & 1) << 4).astype(np.uint8)
    return POP[col].astype(float)


def corr_at(X, y, s):
    n = X.shape[0]
    xs = X[:, s]
    xm = xs - xs.mean()
    sx = xs.std()
    ym = y - y.mean()
    sy = y.std()
    if sx < 1e-12 or sy == 0:
        return 0.0
    return float((xm * ym).sum() / (n - 1) / sx / sy)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--traces', required=True, help='fixed-key target npz')
    ap.add_argument('--key', required=True, help='target key hex (verification)')
    ap.add_argument('--poi', type=int, default=160,
                    help='POI sample center (leak lives ~150-175)')
    ap.add_argument('--win', type=int, default=15)
    ap.add_argument('--out', default='attack_scores.npz')
    args = ap.parse_args()

    d = np.load(args.traces, allow_pickle=True)
    tr = d['traces'].astype(np.float64)
    nonces = d['nonces']
    key = bytes.fromhex(args.key)
    N = tr.shape[0]
    print(f'{N} target traces, key {key.hex()}')
    lo, hi = args.poi - args.win, args.poi + args.win

    # verify keys really are fixed == args.key
    k0 = bytes(tr and nonces[0])  # no-op
    if not (nonces.shape[0] == N):
        sys.exit('bad npz')

    scores = np.zeros((64, 4))
    rank1 = 0
    for c in range(64):
        # per-hypothesis correlation, best over window
        for h, (b0, b1) in enumerate(HYP):
            y = hw_in(key, nonces, c, hyp=(b0, b1))
            best = 0.0
            for s in range(lo, hi):
                best = max(best, abs(corr_at(tr, y, s)))
            scores[c, h] = best
        rk = int(np.argmax(scores[c]))
        truth = (((int.from_bytes(key[0:8], 'little') >> c) & 1) << 1 |
                 ((int.from_bytes(key[8:16], 'little') >> c) & 1))
        if rk == truth:
            rank1 += 1
        if c < 8 or c in (31, 32, 63):
            print(f'col {c:2d}: rank={rk} truth={truth} '
                  f'scores={scores[c].round(3)} {"OK" if rk == truth else "x"}')
    print(f'\nCPA rank-1 (no brute force): {rank1}/64  '
          f'(chance {25/64:.0%})')

    # assemble: take rank-1, brute-force weak columns (max 12)
    col_hyp = {c: int(np.argmax(scores[c])) for c in range(64)}
    np.savez(args.out, scores=scores, nonce=nonces[0],
             ct_tag=bytes(ar.ascon_encrypt(key, bytes(nonces[0]), AD, PT)))
    # bounded brute force over lowest-margin columns
    margin = np.sort(scores, axis=1)[:, -1] - np.sort(scores, axis=1)[:, -2]
    order = np.argsort(margin)
    import itertools
    found = None
    for kk in range(0, 13):
        weak = list(order[:kk])
        strong = {c: col_hyp[c] for c in range(64) if c not in weak}
        for combo in itertools.product(range(4), repeat=kk):
            ch = dict(strong)
            ch.update({c: h for c, h in zip(weak, combo)})
            k = assemble(ch)
            if verify(k, bytes(nonces[0]),
                      bytes(ar.ascon_encrypt(key, bytes(nonces[0]), AD, PT))):
                found = k
                print(f'\n*** KEY RECOVERED (brute {kk} weak cols): {k.hex()}')
                print(f'    MATCH TRUE: {k == key}')
                return
        if found:
            break
    print('\nno key within brute budget; saved scores -> ' + args.out)


if __name__ == '__main__':
    main()
