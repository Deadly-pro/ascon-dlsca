#!/usr/bin/env python3
r"""offline_model_id.py — identify which fault model the eo=31 glitch produced.

Known data (fixed key+nonce, ct intact, deterministic faulty tag):
  key  = 8826d916cdfb21c6c1ff91a761565a70
  nonce= 000102030405060708090a0b0c0d0e0f
  T    = 2d71712fea84f2711c6ec3d8dac3abc6   (correct tag)
  Tf   = 3cff06998e6602b98dccf1c7c9cc9821   (faulty tag @ eo=31, off=3359, w=67)

Tests each candidate deterministic fault model against Tf:
  A. skip final key-XOR            -> tag' = Y3||Y4 raw
  B. skip init key-XOR             -> finalization without S1,S2 ^= K
  C. skip round r (r=0..11)        -> 11 of 12 finalization rounds
  D. truncate at round r           -> early-done: only r rounds, then tag
  E. key-reg bit flip at entry     -> S1/S2 ^= K with one key bit flipped
  F. key-reg bit flip at final XOR -> tag ^= K with one key bit flipped
  G. bit flip at round-r S-box input (r=0..11), any word/bit
  H. word zeroing at round r
  I. bit flip in output state Y (post round-12, pre key-XOR)

A match converts the eo axis into a ROUND MAP: eo=31 -> round r*.
Then round 11 (the DFA target) = eo extrapolated from the map.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))
import ascon_ref as ar
from dfa_bitflip import _state_before_final_perm, _round, _substitution, _pL11

KEY   = bytes.fromhex('8826d916cdfb21c6c1ff91a761565a70')
NONCE = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
AD    = b'\x00' * 4
PT    = b'\x00' * 4
T     = bytes.fromhex('2d71712fea84f2711c6ec3d8dac3abc6')
Tf    = bytes.fromhex('3cff06998e6602b98dccf1c7c9cc9821')
K0 = ar.bytes_to_int(KEY[0:8])
K1 = ar.bytes_to_int(KEY[8:16])

def tag_of(S, final_key=True):
    if final_key:
        return (ar.int_to_bytes(S[3] ^ K0, 8) + ar.int_to_bytes(S[4] ^ K1, 8))
    return ar.int_to_bytes(S[3], 8) + ar.int_to_bytes(S[4], 8)

def finalize(S0, skip_round=None, nrounds=12, init_key=True):
    X = [v for v in S0]
    if init_key:
        X[1] ^= K0; X[2] ^= K1
    for r in range(nrounds):
        if skip_round == r:
            continue
        _round(X, r)
    return X

def rounds_then_flip(S0, r_flip, w, b, nrounds=12):
    """Flip bit (w,b) at the S-box INPUT of round r_flip (after pC of that round)."""
    X = [v for v in S0]
    X[1] ^= K0; X[2] ^= K1
    for r in range(nrounds):
        X[2] ^= (0xf0 - r*0x10 + r*0x1)      # pC
        if r == r_flip:
            X[w] ^= (1 << b)                 # fault at S-box input
        _substitution(X); _pL11(X)
    return X

S0 = _state_before_final_perm(KEY, NONCE, AD, PT)

# sanity: correct tag
assert tag_of(finalize(S0)) == T, 'correct-tag model broken!'
print(f'correct-tag model verified: {tag_of(finalize(S0)).hex()}')
print(f'HW(T ^ Tf) = {(int.from_bytes(T,"big") ^ int.from_bytes(Tf,"big")).bit_count()} bits')
print()

hits = []

# A: skip final key-XOR
if tag_of(finalize(S0), final_key=False) == Tf:
    hits.append('A: skip final key-XOR  => K = T ^ Tf DIRECTLY')
print('A skip-final-key-XOR:', tag_of(finalize(S0), final_key=False) == Tf)

# B: skip init key-XOR
X = [v for v in S0]
for r in range(12):
    _round(X, r)
if tag_of(X) == Tf:
    hits.append('B: skip init key-XOR of finalization')
print('B skip-init-key-XOR:', tag_of(X) == Tf)

# C: skip round r
for r in range(12):
    if tag_of(finalize(S0, skip_round=r)) == Tf:
        hits.append(f'C: round {r} SKIPPED in finalization')
        print(f'C skip round {r}: MATCH')
    else:
        print(f'C skip round {r}: no') if r < 2 else None

# D: truncate at r rounds (early done)
for r in range(1, 12):
    if tag_of(finalize(S0, nrounds=r)) == Tf:
        hits.append(f'D: finalization TRUNCATED at {r} rounds (early done)')
        print(f'D truncate at {r} rounds: MATCH')

# E: key-register bit flipped at finalization entry (S1/S2 ^= K' )
for w, K in ((1, K0), (2, K1)):
    for b in range(64):
        X = [v for v in S0]
        X[1] ^= K0 ^ ((1 << b) if w == 1 else 0)
        X[2] ^= K1 ^ ((1 << b) if w == 2 else 0)
        for r in range(12):
            _round(X, r)
        if tag_of(X) == Tf:
            hits.append(f'E: key bit w{w} b{b} flipped at finalization entry')
            print(f'E keyflip entry w{w} b{b}: MATCH')

# F: key-register bit flipped only in the FINAL tag XOR
for b in range(128):
    e = 1 << b
    t = tag_of(finalize(S0))
    tf = (int.from_bytes(t, 'big') ^ (e if b < 64 else 0)).to_bytes(16, 'big')
    # bit b of the 128-bit XOR mask (K0||K1)
    t_int = int.from_bytes(t, 'big')
    mask = int.from_bytes((ar.int_to_bytes(K0,8)+ar.int_to_bytes(K1,8)), 'big') ^ e
    cand = (t_int ^ mask ^ (int.from_bytes((ar.int_to_bytes(K0,8)+ar.int_to_bytes(K1,8)),'big'))).to_bytes(16,'big') if False else None
for w,K in ((0,K0),(1,K1)):
    for b in range(64):
        Kf = K ^ (1 << b)
        t = finalize(S0)
        cand = ar.int_to_bytes(t[3] ^ (Kf if w==0 else K0), 8) + ar.int_to_bytes(t[4] ^ (Kf if w==1 else K1), 8)
        if cand == Tf:
            hits.append(f'F: key bit w{w} b{b} flipped in final tag XOR (1-bit diff — eo=45 class)')
            print(f'F keyflip final-xor w{w} b{b}: MATCH')

# G: bit flip at round-r S-box input
found_g = []
for r in range(12):
    for w in range(5):
        for b in range(64):
            if tag_of(rounds_then_flip(S0, r, w, b)) == Tf:
                found_g.append((r, w, b))
                hits.append(f'G: bit flip w{w} b{b} at round-{r} S-box input')
                print(f'G bitflip round {r} w{w} b{b}: MATCH')
print(f'G bitflip sweep: {len(found_g)} matches')

# H: word zeroing at round r
for r in range(12):
    for w in range(5):
        X = [v for v in S0]
        X[1] ^= K0; X[2] ^= K1
        for rr in range(12):
            X[2] ^= (0xf0 - rr*0x10 + rr*0x1)
            if rr == r:
                X[w] = 0
            _substitution(X); _pL11(X)
        if tag_of(X) == Tf:
            hits.append(f'H: word {w} zeroed at round {r}')
            print(f'H wordzero round {r} w{w}: MATCH')

# I: bit flip in output state Y (post round-12)
Y = finalize(S0)
for w in (3, 4):
    for b in range(64):
        Yf = [v for v in Y]
        Yf[w] ^= (1 << b)
        if tag_of(Yf) == Tf:
            hits.append(f'I: bit flip in OUTPUT state word {w} bit {b} (post-round, pre-XOR)')
            print(f'I output-state flip w{w} b{b}: MATCH')

print()
print('=' * 60)
if hits:
    print('FAULT MODEL IDENTIFIED:')
    for h in hits:
        print('  *', h)
else:
    print('NO model matched — the eo=31 fault is something more exotic')
    print('(e.g. multi-bit, FSM mis-sequence, or a fault in the PT/AD phase')
    print(' after the ct beat was latched). Needs the stateout read on board.')
