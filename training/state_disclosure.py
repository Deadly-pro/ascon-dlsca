#!/usr/bin/env python3
r"""state_disclosure.py — recover the ASCON-128 key from a frozen mid-init state.

Premise: ASCON-128 init loads S = IV || K0 || K1 || N0 || N1 into the state
registers, then runs p^12. Every round is invertible (pC is an XOR, pS has an
inverse S-box, pL is a linear map per word). So a state snapshot taken after
r init rounds can be inverted r times to yield IV || K || N — and the recovery
is SELF-VERIFYING: word 0 must equal the public IV constant and words 3,4 must
equal the chosen nonce. If both check out, words 1,2 ARE the key.

Attack use (board): clock-glitch hang (glitch_only) mid-init freezes both the
core and the latched REG_CRYPT_STATEOUT (0x0e, 320 bits). Read it, try
r = 0..12, and output the key when the IV+nonce check passes.

Usage:
  self-test (no hardware):  .venv/bin/python training/state_disclosure.py
  board snapshot:           .venv/bin/python training/state_disclosure.py \
      --state <80 hex chars> --nonce <32 hex chars>
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ascon_ref as ar
from dfa_bitflip import sbox5

SBOX = [sbox5(x) for x in range(32)]
SBOX_INV = [0] * 32
for x in range(32):
    SBOX_INV[SBOX[x]] = x

# ── inverse linear layer (per word) ─────────────────────────────────────────
def _build_lin_inv(r1, r2):
    M = [[0]*64 for _ in range(64)]
    for i in range(64):
        M[i][i] ^= 1
        M[i][(i + r1) % 64] ^= 1
        M[i][(i + r2) % 64] ^= 1
    A = [row[:] + [1 if i == j else 0 for j in range(64)]
         for i, row in enumerate(M)]
    for col in range(64):
        for r in range(col, 64):
            if A[r][col]:
                A[col], A[r] = A[r], A[col]
                break
        for r in range(64):
            if r != col and A[r][col]:
                for c in range(col, 128):
                    A[r][c] ^= A[col][c]
    inv = [row[64:] for row in A]
    def apply_inv(x):
        bits = [(x >> i) & 1 for i in range(64)]
        out = 0
        for i in range(64):
            s = 0
            for j in range(64):
                s ^= inv[i][j] & bits[j]
            out |= s << i
        return out
    return apply_inv

LIN_INV = {w: _build_lin_inv(r1, r2) for w, (r1, r2) in
           enumerate([(19, 28), (61, 39), (1, 6), (10, 17), (7, 41)])}

def _inv_substitution(S):
    """Invert the 5-bit S-box layer, column by column."""
    for col in range(64):
        y = sum(((S[j] >> col) & 1) << j for j in range(5))
        x = SBOX_INV[y]
        for j in range(5):
            if (x >> j) & 1:
                S[j] |= (1 << col)
            else:
                S[j] &= ~(1 << col) & ((1 << 64) - 1)

def inv_round(S, r):
    """Invert round r (0-based): pL^-1 -> pS^-1 -> pC^-1."""
    for w in range(5):
        S[w] = LIN_INV[w](S[w])
    _inv_substitution(S)
    S[2] ^= (0xf0 - r*0x10 + r*0x1)

def round_const(r):
    return 0xf0 - r*0x10 + r*0x1

def iv_word():
    """ASCON-128 IV: bytes [k, rate*8, a, b, 0,0,0,0] = 0x004c000100... big-end."""
    iv = ar.to_bytes([128, 8*8, 12, 6, 0, 0, 0, 0])
    return ar.bytes_to_int(iv)

IV = iv_word()

def forward_init_state(key, nonce, nrounds):
    """State after nrounds init rounds (for testing)."""
    iv = ar.to_bytes([128, 64, 12, 6, 0, 0, 0, 0])
    S = ar.bytes_to_state(iv + bytes(key) + bytes(nonce))
    from dfa_bitflip import _round
    for r in range(nrounds):
        _round(S, r)
    return S

def disclose(state, nonce, max_rounds=12):
    """Given a frozen 5-word state and the public nonce, try every count of
    executed init rounds; return (key_bytes, rounds) when IV+nonce verify.
    Returns (None, None) if no r works (snapshot not from the init phase)."""
    S = [int(v) & ((1 << 64) - 1) for v in state]
    n_int = ar.bytes_to_int(bytes(nonce))
    for r in range(max_rounds, -1, -1):
        T = [v for v in S]
        for rr in range(r - 1, -1, -1):
            inv_round(T, rr)
        if T[0] == IV and T[3] == n_int >> 64 \
           and T[4] == n_int & ((1 << 64) - 1):
            key = ar.int_to_bytes(T[1], 8) + ar.int_to_bytes(T[2], 8)
            return key, r
    return None, None

# ── self-test ───────────────────────────────────────────────────────────────
def selftest():
    import random
    rng = random.Random(0)
    ok = 0
    trials = 40
    for t in range(trials):
        key = bytes(rng.randrange(256) for _ in range(16))
        nonce = bytes(rng.randrange(256) for _ in range(16))
        r = rng.randrange(0, 13)          # freeze anywhere in init
        S = forward_init_state(key, nonce, r)
        rk, rr = disclose(S, nonce)
        if rk == key and rr == r:
            ok += 1
        else:
            print(f'  FAIL t={t} r={r}: recovered {rk.hex() if rk else None} '
                  f'(rounds {rr}) vs true {key.hex()}')
    print(f'state disclosure self-test: {ok}/{trials} full-key recoveries '
          f'from frozen mid-init states')
    return ok == trials

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--state', type=str,
                    help='frozen 320-bit state as 80 hex chars (5 words x '
                         '16 hex, word0..word4)')
    ap.add_argument('--nonce', type=str, help='16-byte nonce hex (32 chars)')
    ap.add_argument('--words', type=str,
                    help='alternative to --state: 5 comma-separated 64-bit '
                         'hex words, e.g. "0x..,0x..,..."')
    args = ap.parse_args()
    if args.selftest:
        sys.exit(0 if selftest() else 1)
    if not args.nonce:
        ap.error('need --nonce (the query nonce)')
    nonce = bytes.fromhex(args.nonce)
    if args.words:
        S = [int(w, 0) for w in args.words.split(',')]
    elif args.state:
        h = args.state.strip()
        S = [int.from_bytes(bytes.fromhex(h[i:i+16]), 'big')
             for i in range(0, 80, 16)]
    else:
        ap.error('need --state or --words')
    key, r = disclose(S, nonce)
    if key:
        print(f'rounds executed: {r}')
        print(f'RECOVERED KEY: {key.hex()}')
        print('(verified: IV word matches ASCON-128 constant and words 3,4 '
              'match the nonce)')
    else:
        print('[!] No init-phase match for this state — snapshot is not from '
              'the init rounds (try AD/PT/finalization phases, or check the '
              'word/byte order of the register read).')

if __name__ == '__main__':
    main()
