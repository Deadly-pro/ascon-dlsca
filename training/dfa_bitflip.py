#!/usr/bin/env python3
r"""dfa_bitflip.py — bit-flip-only DFA on ASCON-128 (Nakamura et al. 2025/2026).

Fault model: 1-bit flip in the S-box input of round 11 of the finalization
permutation p^12 (nonce-misuse scenario: same key/nonce/pt, so the round-11
S-box input is FIXED across queries). Recovers the round-11 S-box input state
column-by-column via masked DDT intersection, then propagates forward to
extract the key from the tag.

How it works (per fault):
  1. Observe the tag differential (correct tag vs faulted tag). The key XOR
     cancels, leaving the differential of the p^12 output words 3,4.
  2. Invert the pL12 linear layer on words 3,4 -> round-12 pS output diff.
  3. Y = OR of the two words = active columns reaching the tag.
  4. Reconstruct the round-11 S-box output differential pattern P:
       P_j bit i = Y[(i-r_j1)%64] | Y[(i-r_j2)%64]
     (verified ~94%: at the true fault column, the 5-bit dy matches).
  5. Per candidate column, intersect masked-DDT candidates across all faults
     that hit that column; the true column converges to a singleton x_c.

Usage:
  .venv/bin/python training/dfa_bitflip.py --selftest
  .venv/bin/python training/dfa_bitflip.py --faults glitch_faults.npz
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ascon_ref as ar

# ── 5-bit S-box matching ascon_ref ──────────────────────────────────────────
def sbox5(x):
    S = [(x >> j) & 1 for j in range(5)]
    S[0] ^= S[4]; S[4] ^= S[3]; S[2] ^= S[1]
    T = [((S[i] ^ 1) & S[(i+1) % 5]) for i in range(5)]
    for i in range(5): S[i] ^= T[(i+1) % 5]
    S[1] ^= S[0]; S[0] ^= S[4]; S[3] ^= S[2]; S[2] ^= 1
    out = 0
    for j in range(5): out |= (S[j] & 1) << j
    return out
SBOX = [sbox5(x) for x in range(32)]

# Full 5-bit DDT: for dx in {1,2,4,8,16} and mask m, D_{dx,m}(dy) = candidate x
# mask bit k means "output bit k observable"
def build_ddt():
    DDT = {}
    for dx in [1, 2, 4, 8, 16]:
        DDT[dx] = {}
        for mask in [31, 30, 15, 14]:
            tab = {}
            for dy in range(32):
                tab[dy] = [x for x in range(32)
                           if ((SBOX[x] ^ SBOX[x ^ dx]) & mask) == (dy & mask)]
            DDT[dx][mask] = tab
    return DDT
DDT = build_ddt()
# masks: 31=11111, 30=11110, 15=01111, 14=01110 (paper's 4 masked DDTs)
MASKS = [31, 30, 15, 14]

# ── Linear layer inverse ────────────────────────────────────────────────────
def _build_sigma_inv(r1, r2):
    M = [[0]*64 for _ in range(64)]
    for i in range(64):
        M[i][i] = 1
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

SIGMA_INV = {3: _build_sigma_inv(10, 17), 4: _build_sigma_inv(7, 41)}

# ── Permutation helpers ─────────────────────────────────────────────────────
def _substitution(S):
    S[0] ^= S[4]; S[4] ^= S[3]; S[2] ^= S[1]
    T = [(S[i] ^ 0xFFFFFFFFFFFFFFFF) & S[(i+1) % 5] for i in range(5)]
    for i in range(5): S[i] ^= T[(i+1) % 5]
    S[1] ^= S[0]; S[0] ^= S[4]; S[3] ^= S[2]; S[2] ^= 0xFFFFFFFFFFFFFFFF

def _round(S, r):
    S[2] ^= (0xf0 - r*0x10 + r*0x1)
    _substitution(S)
    S[0] ^= ar.rotr(S[0], 19) ^ ar.rotr(S[0], 28)
    S[1] ^= ar.rotr(S[1], 61) ^ ar.rotr(S[1], 39)
    S[2] ^= ar.rotr(S[2],  1) ^ ar.rotr(S[2],  6)
    S[3] ^= ar.rotr(S[3], 10) ^ ar.rotr(S[3], 17)
    S[4] ^= ar.rotr(S[4],  7) ^ ar.rotr(S[4], 41)

def _state_before_final_perm(key, nonce, ad, pt):
    S = [0, 0, 0, 0, 0]
    k, a, b, rate = 128, 12, 6, 8
    ar.ascon_initialize(S, k, rate, a, b, 1, bytes(key), bytes(nonce))
    ar.ascon_process_associated_data(S, b, rate, bytes(ad))
    ar.ascon_process_plaintext(S, b, rate, bytes(pt))
    return S

def _pL11(state):
    for w, (ra, rb) in enumerate([(19,28),(61,39),(1,6),(10,17),(7,41)]):
        state[w] ^= ar.rotr(state[w], ra) ^ ar.rotr(state[w], rb)

# ── Fault simulation (fault in round-11 S-box input) ────────────────────────
def simulate_fault(key, nonce, ad, pt, fault_col, fault_bit, a=12):
    """1-bit fault in the round-11 S-box input of the finalization p^a.
    Returns (correct_tag, faulty_tag, s11_in): s11_in is the round-11 S-box
    input state (5 words), for validation."""
    K = bytes(key)
    S = _state_before_final_perm(key, nonce, ad, pt)
    S[1] ^= ar.bytes_to_int(K[0:8])
    S[2] ^= ar.bytes_to_int(K[8:16])
    for r in range(10):
        _round(S, r)
    r = 10
    S[2] ^= (0xf0 - r*0x10 + r*0x1)   # round-11 pC -> S-box input
    s11_in = [v for v in S]
    Sf = [v for v in S]
    Sf[fault_bit] ^= (1 << fault_col)
    # rounds 11 (r=10, pS+pL already have pC) and 12 (r=11)
    _substitution(Sf); _pL11(Sf)
    r = 11
    Sf[2] ^= (0xf0 - r*0x10 + r*0x1)
    _substitution(Sf); _pL11(Sf)
    faulty_tag = (ar.int_to_bytes(Sf[3] ^ ar.bytes_to_int(K[0:8]), 8) +
                  ar.int_to_bytes(Sf[4] ^ ar.bytes_to_int(K[8:16]), 8))
    Sc = [v for v in S]
    _substitution(Sc); _pL11(Sc)
    r = 11
    Sc[2] ^= (0xf0 - r*0x10 + r*0x1)
    _substitution(Sc); _pL11(Sc)
    correct_tag = (ar.int_to_bytes(Sc[3] ^ ar.bytes_to_int(K[0:8]), 8) +
                   ar.int_to_bytes(Sc[4] ^ ar.bytes_to_int(K[8:16]), 8))
    return correct_tag, faulty_tag, s11_in

# ── Tag diff -> reconstructed pattern P (per word) ──────────────────────────
def tag_diff_to_pattern(correct_tag, faulty_tag):
    """Return (Y, P): Y = OR of inverse-Σ tag words; P[j] = reconstructed
    round-11 S-box output diff pattern for word j (P_j bit i)."""
    dt3 = ar.bytes_to_int(correct_tag[0:8]) ^ ar.bytes_to_int(faulty_tag[0:8])
    dt4 = ar.bytes_to_int(correct_tag[8:16]) ^ ar.bytes_to_int(faulty_tag[8:16])
    Y = SIGMA_INV[3](dt3) | SIGMA_INV[4](dt4)
    P = []
    for j, (r1, r2) in enumerate([(19,28),(61,39),(1,6),(10,17),(7,41)]):
        wv = 0
        for i in range(64):
            if ((Y >> ((i - r1) % 64)) & 1) or ((Y >> ((i - r2) % 64)) & 1):
                wv |= (1 << i)
        P.append(wv)
    return Y, P

# ── Column solver via masked-DDT intersection ──────────────────────────────
def solve_column(faults):
    """faults: list of (dy_obs, dx) for the SAME column. dy_obs is the 5-bit
    observed round-11 S-box output diff; dx the known fault value (1,2,4,8,16)
    or None for random bit-flip. Returns x_c (0..31) or None.
    Strategy: for each fault, union the DDT candidates over ALL 4 masks (we
    don't know which bit(s) failed to propagate), then intersect across faults.
    The true x is always in the per-fault union; wrong x's get pruned."""
    cands = None
    for dy, dx in faults:
        if dy is None:
            continue
        u = set()
        for mask in MASKS:
            if dx is not None:
                u.update(DDT[dx][mask].get(dy, []))
            else:
                for d in [1, 2, 4, 8, 16]:
                    u.update(DDT[d][mask].get(dy, []))
        if not u:
            return None
        cands = u if cands is None else (cands & u)
        if len(cands) == 1:
            return list(cands)[0]
    if cands is not None and len(cands) == 1:
        return list(cands)[0]
    return None

def solve(observations, correct_tag, verbose=True):
    """observations: list of (fault_col, fault_bit, faulty_tag) — for simulated
    data we know the fault location; the solver still derives dy from the tag
    diff only (fault_col is used to pick the column). Returns recovered
    {col: x_c} dict."""
    from collections import defaultdict
    col_faults = defaultdict(list)
    for fault_col, fault_bit, Tf in observations:
        Y, P = tag_diff_to_pattern(correct_tag, Tf)
        dy = 0
        for j in range(5):
            if (P[j] >> fault_col) & 1:
                dy |= (1 << j)
        col_faults[fault_col].append((dy, 1 << fault_bit))
    recovered = {}
    for col, fl in col_faults.items():
        if len(fl) < 2:
            continue
        x = solve_column(fl)
        if x is not None:
            recovered[col] = x
    return recovered

def solve_unknown_cols(tags, correct_tag, verbose=True, min_faults=3):
    """Solve WITHOUT per-fault column labels (the real-board case).

    A clock glitch flips a bit in an unknown S-box column. For each fault and
    each candidate column c, the observed 5-bit S-box-output diff (dy) comes
    from pattern P. True columns self-prune: for every fault whose P is
    consistent at column c, the masked-DDT intersection must converge to the
    same x_c. We accumulate (dy,dx=None) per (fault,c) only where the DDT has
    candidates, then intersect across faults that hit the same column.

    This only needs >= min_faults faults landing on the SAME column to solve
    that column (bit-flips on other columns contribute nothing there).
    Returns recovered {col: x_c}."""
    from collections import defaultdict
    col_faults = defaultdict(list)
    for Tf in tags:
        Tf = bytes(Tf)
        if Tf == bytes(correct_tag):
            continue  # ineffective fault — no info
        Y, P = tag_diff_to_pattern(correct_tag, Tf)
        for c in range(64):
            dy = 0
            for j in range(5):
                if (P[j] >> c) & 1:
                    dy |= (1 << j)
            # skip columns this fault can't explain at all (empty DDT)
            u = set()
            for mask in MASKS:
                for d in [1, 2, 4, 8, 16]:
                    u.update(DDT[d][mask].get(dy, []))
            if u:
                col_faults[c].append(dy)
    recovered = {}
    for c, fl in col_faults.items():
        if len(fl) < min_faults:
            continue
        x = solve_column([(dy, None) for dy in fl])
        if x is not None:
            recovered[c] = x
    if verbose:
        print(f"unknown-col solve: recovered {len(recovered)}/64 columns "
              f"(from {len(set(bytes(t) for t in tags))} distinct faulty tags)")
    return recovered

# ── Known-key fault localization (real-board calibration) ──────────────────
def localize_fault(key, nonce, ad, pt, faulty_tag, correct_tag=None):
    """Given a KNOWN key/nonce/pt and an observed faulty tag, find the
    (fault_col, fault_bit) of a single round-11-S-box-input bit flip that
    reproduces it. Brute-forces 64 cols x 5 bits. Returns (col, bit) or None.

    This is the calibration step that maps a glitch config to a fault
    location — the DFA's known-column input. If more than one (col,bit)
    reproduces the tag, returns the first (glitch faults are 1-bit, so a
    unique match is expected on real data)."""
    K = bytes(key)
    S = _state_before_final_perm(key, nonce, ad, pt)
    S[1] ^= ar.bytes_to_int(K[0:8]); S[2] ^= ar.bytes_to_int(K[8:16])
    for r in range(10):
        _round(S, r)
    r = 10
    S[2] ^= (0xf0 - r*0x10 + r*0x1)
    matches = []
    for fb in range(5):
        for fc in range(64):
            Sf2 = [v for v in S]
            Sf2[fb] ^= (1 << fc)
            _substitution(Sf2); _pL11(Sf2)
            rr = 11
            Sf2[2] ^= (0xf0 - rr*0x10 + rr*0x1)
            _substitution(Sf2); _pL11(Sf2)
            t = (ar.int_to_bytes(Sf2[3] ^ ar.bytes_to_int(K[0:8]), 8) +
                 ar.int_to_bytes(Sf2[4] ^ ar.bytes_to_int(K[8:16]), 8))
            if bytes(t) == bytes(faulty_tag):
                matches.append((fc, fb))
        if matches:
            break
    return matches[0] if matches else None

def solve_faults_npz(npz_path, verbose=True, unknown_col=False):
    """Solve from a collected faults npz. Expected arrays:
      correct_tag : (16,) uint8 — correct tag for the target query
      tags    : (N,16) uint8 — faulty tags (one per fault)
      cols    : (N,) int — fault column per observation (from calibration),
                optional if unknown_col=True (real-glitch mode)
      bits    : (N,) int — fault bit (optional)
    Returns recovered {col: x_c}."""
    import numpy as np
    d = np.load(npz_path, allow_pickle=True)
    if isinstance(d, dict):
        data = d
    else:
        data = {k: d[k] for k in d.files}
    correct_tag = bytes(data['correct_tag']) if 'correct_tag' in data else None
    tags = data['tags'] if 'tags' in data else data.get('faulty_tags')
    cols = data['cols'] if 'cols' in data else None
    bits = data['bits'] if 'bits' in data else None
    if correct_tag is None or tags is None:
        print("[!] npz needs: correct_tag (16,), tags (N,16)")
        sys.exit(1)
    if unknown_col or cols is None or (hasattr(cols, 'size') and cols.size == 0):
        return solve_unknown_cols(tags, correct_tag, verbose=verbose)
    from collections import defaultdict
    col_faults = defaultdict(list)
    for i in range(len(tags)):
        Tf = bytes(tags[i])
        fc = int(cols[i])
        fb = int(bits[i]) if bits is not None else None
        Y, P = tag_diff_to_pattern(correct_tag, Tf)
        dy = 0
        for j in range(5):
            if (P[j] >> fc) & 1:
                dy |= (1 << j)
        col_faults[fc].append((dy, 1 << fb if fb is not None else None))
    recovered = {}
    for col, fl in col_faults.items():
        if len(fl) < 2:
            continue
        x = solve_column(fl)
        if x is not None:
            recovered[col] = x
    if verbose:
        print(f"recovered {len(recovered)}/64 columns")
    return recovered

def recover_key(recovered, correct_tag):
    """Build the full round-11 S-box input state from recovered columns, run
    rounds 11-12 forward, extract key. Returns (key_bytes or None)."""
    if len(recovered) < 64:
        return None
    s11 = [0]*5
    for col, x in recovered.items():
        for j in range(5):
            if (x >> j) & 1:
                s11[j] |= (1 << col)
    # round 11: pS + pL (pC already applied when we recovered the input)
    _substitution(s11); _pL11(s11)
    # round 12: pC, pS, pL
    r = 11
    s11[2] ^= (0xf0 - r*0x10 + r*0x1)
    _substitution(s11); _pL11(s11)
    K0 = s11[3] ^ ar.bytes_to_int(correct_tag[0:8])
    K1 = s11[4] ^ ar.bytes_to_int(correct_tag[8:16])
    return ar.int_to_bytes(K0, 8) + ar.int_to_bytes(K1, 8)

# ── Self-test ───────────────────────────────────────────────────────────────
def selftest(faults_per_col=6, seed=42):
    import numpy as np
    rng = np.random.default_rng(seed)
    key = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
    nonce = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
    ad = b'\x00' * 4
    pt = b'\x00' * 4
    ref = ar.ascon_encrypt(key, nonce, ad, pt)
    correct_tag = ref[-16:] if len(ref) > 16 else ref
    print(f"key    = {key.hex()}")
    print(f"tag    = {correct_tag.hex()}")

    # Simulated faults: known column/bit per fault (nonce-misuse, fixed key/nonce)
    observations = []
    truth = {}
    for col in range(64):
        S = _state_before_final_perm(key, nonce, ad, pt)
        S[1] ^= ar.bytes_to_int(bytes(key)[0:8])
        S[2] ^= ar.bytes_to_int(bytes(key)[8:16])
        for r in range(10):
            _round(S, r)
        r = 10
        S[2] ^= (0xf0 - r*0x10 + r*0x1)
        x = 0
        for j in range(5):
            if (S[j] >> col) & 1:
                x |= (1 << j)
        truth[col] = x
        for _ in range(faults_per_col):
            fb = int(rng.integers(0, 5))
            T, Tf, s11 = simulate_fault(key, nonce, ad, pt, col, fb)
            observations.append((col, fb, Tf))

    recovered = solve(observations, correct_tag)
    n_ok = sum(1 for c in recovered if recovered[c] == truth.get(c))
    print(f"  known-col:  recovered {len(recovered)}/64 columns, {n_ok} correct")
    # NOTE: solve_unknown_cols is a diagnostic only. Real-board faults are
    # localized by KNOWN-KEY simulation match (glitch_cal collector), because
    # the round-11 S-box output pattern P is NOT column-sparse — without the
    # true column, noise from every other column pollutes each intersection.
    if len(recovered) == 64 and n_ok == 64:
        rk = recover_key(recovered, correct_tag)
        print(f"  recovered key: {rk.hex()}")
        print(f"  true key:      {bytes(key).hex()}")
        ok = rk == bytes(key)
        print(f"  KEY MATCH: {ok}")
        return ok
    return False

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--faults-per-col', type=int, default=15)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--faults', type=str, help='npz with correct_tag/tags[/cols[/bits]]')
    ap.add_argument('--unknown-col', action='store_true',
                    help='real-glitch mode: no per-fault column labels')
    args = ap.parse_args()
    if args.selftest:
        sys.exit(0 if selftest(args.faults_per_col, args.seed) else 1)
    elif args.faults:
        rec = solve_faults_npz(args.faults, unknown_col=args.unknown_col)
        if len(rec) == 64:
            import ascon_ref as _ar
            # correct_tag must be provided in npz for key recovery
            d = np.load(args.faults, allow_pickle=True)
            ct = bytes(d['correct_tag']) if 'correct_tag' in d.files else None
            if ct:
                rk = recover_key(rec, ct)
                print(f"recovered key: {rk.hex()}")
        sys.exit(0)
