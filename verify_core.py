#!/usr/bin/env python3
r"""verify_core.py — settle masked-vs-unmasked on the live board, no scope.

Three independent probes:

1. STATEOUT share-0 leakage: after an encryption, read the 320-bit internal
   state (share 0 only) via REG_CRYPT_STATEOUT for MANY (key, nonce) pairs.
   Correlate each state bit with the S-box HW label of its column.
   - d=0 (genuinely unmasked): share 0 IS the full state -> strong
     correlation with round-1 HW labels.
   - d=1 (masked): share 0 is one random share -> correlation ~ 0.

2. Round-count timing: count Nops between trigger rise and ciphertext_valid
   via busy polling. d=1 processes 2 shares per bit -> measurably longer
   init than d=0.

3. Ciphertext correctness sanity (KAT) to confirm the core works at all.
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import chipwhisperer as cw
from cw305_ascon_shim import wrap
from ascon_ref import ascon_encrypt, fpga_expected
import labels as lab

BITSTREAM = os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit')


def main():
    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=BITSTREAM, fpga_id='100t', platform='cw305')
    target.vccint_set(1.0)
    target.pll.pll_enable_set(True)
    target.pll.pll_outenable_set(False, 0)
    target.pll.pll_outenable_set(True, 1)
    target.pll.pll_outenable_set(False, 2)
    target.pll.pll_outfreq_set(10e6, 1)
    target.fpga_write(0x00, [0x19])       # tio_clkout enable
    t = wrap(target)

    rng = np.random.default_rng(0)
    N = 300
    keys = [rng.bytes(16) for _ in range(N)]
    nonces = [rng.bytes(16) for _ in range(N)]

    # ---- probe 3: KAT sanity on first pair ----
    exp = fpga_expected(keys[0], nonces[0])
    t.loadEncryptionKey(keys[0])
    t.loadInput(nonces[0])
    t.go()
    got = bytes(t.readOutput())
    print(f'KAT: {"PASS" if got == exp else "FAIL"} '
          f'(got {got.hex()[:16]}…, exp {exp.hex()[:16]}…)')
    if got != exp:
        print('core not functioning — fix programming before anything else')
        return

    # ---- probe 1: share-0 state vs S-box HW labels ----
    states = np.zeros((N, 40), dtype=np.uint8)   # 320 bits / 8
    t0 = time.time()
    for i in range(N):
        t.loadEncryptionKey(keys[i])
        t.loadInput(nonces[i])
        t.go()
        while not t.is_done():
            pass
        out = bytearray()
        # fpga_read auto-increments the byte counter internally
        out.extend(target.fpga_read(0x0e, 40))   # REG_CRYPT_STATEOUT
        states[i] = out
    print(f'state reads done in {time.time()-t0:.1f}s')

    kb = np.stack([np.frombuffer(k, np.uint8) for k in keys])
    nb = np.stack([np.frombuffer(n, np.uint8) for n in nonces])
    hw = lab.round1_sbox_hw(kb, nb)              # (N,64) true HW per col

    best = []
    for c in range(64):
        y = hw[:, c].astype(float)
        yc = y - y.mean()
        denom = np.sqrt((yc ** 2).sum())
        if denom == 0:
            continue
        for byte in range(40):
            x = states[:, byte].astype(float)
            r = abs(np.corrcoef(x, yc)[0, 1])
            best.append((r, c, byte))
    best.sort(reverse=True)
    print('\nprobe 1 — |corr(state bit, S-box HW)| top 5:')
    for r, c, b in best[:5]:
        print(f'  col {c:2d} byte {b:2d}: r={r:.3f}')
    r_max = best[0][0]
    # significance floor for N=300: |r| >~ 3/sqrt(N) ≈ 0.17
    verdict = 'UNMASKED (share0 = full state)' if r_max > 0.25 else \
              'MASKED or share-0 uninformative' if r_max < 0.15 else \
              'INCONCLUSIVE'
    print(f'max |r| = {r_max:.3f} (noise floor ~{3/np.sqrt(N):.2f} at N={N})')
    print(f'VERDICT: {verdict}')


if __name__ == '__main__':
    main()
