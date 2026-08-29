#!/usr/bin/env python3
r"""labels.py — ground-truth intermediate computation for DL-SCA profiling.

Computes, purely in software, the Hamming weight of the round-1 S-box output
of the ASCON-128 initialization permutation for every (key, nonce) pair.

    round-1 S-box output (column c):
        S = IV || key || nonce            (5 x 64-bit words, loaded state)
        S[2] ^= round_constant(r=0)       (0xf0)
        S = substitution_layer(S)         (bit-sliced, exactly ascon_ref)
        out[c] = 5-bit column c of S      ->  HW in {0..5}  (6 classes)

Column c's S-box input depends on exactly TWO unknown key bits (bit c of
key[0:8] and bit c of key[8:16]) plus known IV/nonce bits. So a per-column
attack has only 4 key hypotheses — that is what attack.py uses for key rank.

The substitution layer used here is verified to be bit-identical to
ascon_ref.py (which itself matches the CW305 hardware 5/5 on KATs), so labels
are exact ground truth — masking affects what a single trace leaks, not what
the label is.

Usage:
    python3 training/labels.py            # self-test against ascon_ref
"""
import numpy as np

# ASCON-128 AEAD IV = to_bytes([1,0,(8<<4)+12]) + int_to_bytes(128,2) + to_bytes([16,0,0])
IV = np.array([1, 0, 0x8C, 0x80, 0, 0x10, 0, 0], dtype=np.uint8)

_POPCOUNT = np.zeros(32, dtype=np.uint8)
for _v in range(32):
    _POPCOUNT[_v] = bin(_v).count('1')


def le_u64(b):
    """(N,8) uint8 little-endian bytes -> (N,) uint64 words."""
    b = b.astype(np.uint64)
    out = b[:, 0].copy()
    for i in range(1, 8):
        out |= b[:, i] << (8 * i)
    return out


def load_state(keys, nonces):
    """(N,16) keys, (N,16) nonces -> (N,5) uint64 initial state words."""
    S = np.empty((len(keys), 5), dtype=np.uint64)
    S[:, 0] = le_u64(np.tile(IV[None, :], (len(keys), 1)))
    S[:, 1] = le_u64(keys[:, 0:8])
    S[:, 2] = le_u64(keys[:, 8:16])
    S[:, 3] = le_u64(nonces[:, 0:8])
    S[:, 4] = le_u64(nonces[:, 8:16])
    return S


def chi_only(S):
    """aff1 + chi on (N,5) uint64, for the round-1 exposed intermediate.

    Matches the sim-verified formula and the RTL amplifier's sb_chi_val. The
    full ASCON S-box additionally applies affine2 (x1^=x0; x0^=x4; x3^=x2;
    x2^=~x2); that step is NOT part of the algebra the round-1 per-column
    amplifier exposes, so labels for it must use this shorter chain. The
    KADD path (real cipher state) still uses the full substitution_layer.
    """
    x = S.copy()
    x[:, 0] ^= x[:, 4]
    x[:, 4] ^= x[:, 3]
    x[:, 2] ^= x[:, 1]
    t = ~x & np.roll(x, -1, axis=1)          # T[i] = ~x[i] & x[(i+1)%5]
    x ^= np.roll(t, -1, axis=1)              # x[i] ^= T[(i+1)%5]
    return x


def substitution_layer(S):
    """Bit-sliced ASCON substitution layer on (N,5) uint64, == ascon_ref."""
    x = S.copy()
    x[:, 0] ^= x[:, 4]
    x[:, 4] ^= x[:, 3]
    x[:, 2] ^= x[:, 1]
    t = ~x & np.roll(x, -1, axis=1)          # T[i] = ~S[i] & S[(i+1)%5]
    x ^= np.roll(t, -1, axis=1)              # S[i] ^= T[(i+1)%5]
    x[:, 1] ^= x[:, 0]
    x[:, 0] ^= x[:, 4]
    x[:, 3] ^= x[:, 2]
    x[:, 2] ^= np.uint64(0xFFFFFFFFFFFFFFFF)
    return x


def _rotr(x, r):
    return (x >> r) | (x << (64 - r))


def linear_diffusion(S):
    x = S.copy()
    x[:, 0] ^= _rotr(x[:, 0], 19) ^ _rotr(x[:, 0], 28)
    x[:, 1] ^= _rotr(x[:, 1], 61) ^ _rotr(x[:, 1], 39)
    x[:, 2] ^= _rotr(x[:, 2], 1) ^ _rotr(x[:, 2], 6)
    x[:, 3] ^= _rotr(x[:, 3], 10) ^ _rotr(x[:, 3], 17)
    x[:, 4] ^= _rotr(x[:, 4], 7) ^ _rotr(x[:, 4], 41)
    return x


def permutation_round(S, r):
    S[:, 2] ^= np.uint64(0xF0 - r * 0x10 + r * 0x1)
    S = substitution_layer(S)
    return linear_diffusion(S)


def kadd_words_hw(keys, nonces):
    """(N,16) uint8 -> (N, 8) uint8: HW of each byte of S[3] after init + KADD.

    S[3] is the state word XORed with key[0:8] after the 12-round init
    permutation — a real, key-dependent intermediate. Note this depends on the
    FULL key (not factorable per byte), so it is used for profiled
    intermediate-recovery, not per-byte key rank.
    """
    S = load_state(keys, nonces)
    for r in range(12):
        S = permutation_round(S, r)
    S[:, 3] ^= le_u64(keys[:, 0:8])     # KADD: S[3] ^= key[0:8]
    hw = np.empty((len(keys), 8), dtype=np.uint8)
    w = S[:, 3]
    for b in range(8):
        hw[:, b] = np.unpackbits(
            (w & 0xFF).astype(np.uint8)[:, None], bitorder='little',
            axis=1).sum(axis=1)
        w >>= 8
    return hw


def round1_sbox_hw(keys, nonces):
    """(N,16) uint8 arrays -> (N, 64) uint8: HW of round-1 S-box output per
    column.

    Column c input bits = (S0_c, S1_c, S2_c, S3_c, S4_c) with the round-0
    constant already XORed into S2, then the FULL substitution layer. This
    is the exposed intermediate of the stock unmasked rprimas core. The
    amplifier designs expose only aff1+chi — use chi_only() for those.
    """
    S = load_state(keys, nonces)
    S[:, 2] ^= np.uint64(0xF0)                # round-0 constant
    out = substitution_layer(S)
    hw = np.empty((len(keys), 64), dtype=np.uint8)
    for c in range(64):
        col = ((out[:, 0] >> c) & 1) | (((out[:, 1] >> c) & 1) << 1) | \
              (((out[:, 2] >> c) & 1) << 2) | (((out[:, 3] >> c) & 1) << 3) | \
              (((out[:, 4] >> c) & 1) << 4)
        hw[:, c] = _POPCOUNT[col]
    return hw


def _sbox_col(v):
    """5-bit full ASCON S-box on a single column value (== stock core's
    round-1 exposed intermediate; verified == ascon_ref)."""
    v = int(v)  # numpy scalar uint64 >> int can raise under some builds
    b0 = (v >> 0) & 1
    b1 = (v >> 1) & 1
    b2 = (v >> 2) & 1
    b3 = (v >> 3) & 1
    b4 = (v >> 4) & 1
    b0 ^= b4
    b4 ^= b3
    b2 ^= b1
    t0 = (~b0) & b1
    t1 = (~b1) & b2
    t2 = (~b2) & b3
    t3 = (~b3) & b4
    t4 = (~b4) & b0
    b0 ^= t1
    b1 ^= t2
    b2 ^= t3
    b3 ^= t4
    b4 ^= t0
    b1 ^= b0
    b0 ^= b4
    b3 ^= b2
    b2 ^= 1
    return b0 | (b1 << 1) | (b2 << 2) | (b3 << 3) | (b4 << 4)


def _sbox_col_chi(v):
    """5-bit aff1+chi on a single column value (verified == the chip's
    round-1 exposed intermediate). Affine2 is deliberately omitted."""
    v = int(v)  # numpy scalar uint64 >> int can raise under some builds
    b0 = (v >> 0) & 1
    b1 = (v >> 1) & 1
    b2 = (v >> 2) & 1
    b3 = (v >> 3) & 1
    b4 = (v >> 4) & 1
    b0 ^= b4
    b4 ^= b3
    b2 ^= b1
    t0 = (~b0) & b1
    t1 = (~b1) & b2
    t2 = (~b2) & b3
    t3 = (~b3) & b4
    t4 = (~b4) & b0
    b0 ^= t1
    b1 ^= t2
    b2 ^= t3
    b3 ^= t4
    b4 ^= t0
    return b0 | (b1 << 1) | (b2 << 2) | (b3 << 3) | (b4 << 4)


def hypothesis_labels(column, nonces, key_bits):
    """Predicted HW class per key hypothesis for attack scoring.

    column : int 0..63
    nonces : (N,16) uint8
    key_bits : (H,2) uint8  the two candidate key bits (bit `column` of
              key[0:8] and of key[8:16]) for each hypothesis

    Returns (N, H) uint8: HW class the model should output for each trace
    under each hypothesis. IV and nonce are known; only the 2 key bits vary.
    """
    S = load_state(np.zeros((len(nonces), 16), dtype=np.uint8), nonces)
    iv_bits = (S[:, 0] >> column) & 1
    n1_bits = (S[:, 3] >> column) & 1
    n2_bits = (S[:, 4] >> column) & 1
    rc_bit = (0xF0 >> column) & 1 if column < 8 else 0

    labels = np.empty((len(nonces), len(key_bits)), dtype=np.uint8)
    for h, (kb0, kb1) in enumerate(key_bits):
        b0 = iv_bits
        b1 = np.full(len(nonces), kb0, dtype=np.uint64)
        b2 = (np.full(len(nonces), kb1, dtype=np.uint64) ^ rc_bit) & 1
        col = b0 | (b1 << 1) | (b2 << 2) | (n1_bits << 3) | (n2_bits << 4)
        out = np.vectorize(_sbox_col)(col)
        labels[:, h] = _POPCOUNT[out]
    return labels


def all_hypotheses():
    """All 4 two-bit key hypotheses as (4,2) uint8 rows."""
    return np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.uint8)


def _self_test():
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import ascon_ref

    rng = np.random.default_rng(0)
    n = 50
    keys = rng.integers(0, 256, size=(n, 16)).astype(np.uint8)
    nonces = rng.integers(0, 256, size=(n, 16)).astype(np.uint8)

    hw = round1_sbox_hw(keys, nonces)

    # Reference: replicate ascon_ref init + round-0 constant + FULL S-box
    ivb = ascon_ref.to_bytes([1, 0, (8 << 4) + 12]) + \
        ascon_ref.int_to_bytes(128, 2) + ascon_ref.to_bytes([16, 0, 0])
    bad = 0
    for i in range(n):
        S = ascon_ref.bytes_to_state(ivb + bytes(keys[i]) + bytes(nonces[i]))
        S[2] ^= 0xF0
        S[0] ^= S[4]; S[4] ^= S[3]; S[2] ^= S[1]
        T = [(S[j] ^ 0xFFFFFFFFFFFFFFFF) & S[(j + 1) % 5] for j in range(5)]
        for j in range(5):
            S[j] ^= T[(j + 1) % 5]
        S[1] ^= S[0]; S[0] ^= S[4]; S[3] ^= S[2]; S[2] ^= 0xFFFFFFFFFFFFFFFF
        for c in range(64):
            col = ((S[0] >> c) & 1) | (((S[1] >> c) & 1) << 1) | \
                  (((S[2] >> c) & 1) << 2) | (((S[3] >> c) & 1) << 3) | \
                  (((S[4] >> c) & 1) << 4)
            if hw[i, c] != bin(col).count('1'):
                bad += 1
    print(f'self-test: round1_sbox_hw vs ascon_ref  {n*64} checks, {bad} mismatches')

    # KADD byte labels vs ascon_ref.ascon_initialize
    import ascon_ref as ar
    khw = kadd_words_hw(keys, nonces)
    kbad = 0
    for i in range(n):
        S = [0, 0, 0, 0, 0]
        ar.ascon_initialize(S, 128, 16, 12, 8, 1, bytes(keys[i]), bytes(nonces[i]))
        w3 = int(S[3])
        for b in range(8):
            if khw[i, b] != bin(w3 & 0xFF).count('1'):
                kbad += 1
            w3 >>= 8
    print(f'self-test: kadd_words_hw vs ascon_initialize  {n*8} checks, {kbad} mismatches')
    assert kbad == 0

    # hypothesis_labels: for the true key bits, predicted class must equal truth
    true = np.zeros((n, 2), dtype=np.uint8)
    true[:, 0] = (keys[:, 0] >> 0) & 1
    true[:, 1] = (keys[:, 8] >> 0) & 1
    hyp = all_hypotheses()
    lab = hypothesis_labels(0, nonces, hyp)
    idx = np.all(hyp[None, :, :] == true[:, None, :], axis=2).argmax(axis=1)
    match = (lab[np.arange(n), idx] == hw[:, 0]).mean()
    print(f'self-test: hypothesis_labels(true hyp) == truth: {match*100:.1f}%')
    assert bad == 0 and match == 1.0


if __name__ == '__main__':
    _self_test()
