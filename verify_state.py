#!/usr/bin/env python3
r"""verify_state.py — decisive unmasked-state gate for the new core.

Reads REG_CRYPT_STATEOUT (0x0e) after a full encryption and compares
byte-exact against the oracle-computed final ASCON state (post p12
finalization + KADD_4: x3 = tag1, x4 = tag2). If it matches, state_reg_out
carries the real internal register — fully observable unmasked core.

Usage: python3 verify_state.py [-b vivado_ascon/ascon_cw305_top.bit]
"""
import argparse
import numpy as np
from scope_config import connect_target
from ascon_ref import ascon_initialize, ascon_process_associated_data, \
    ascon_process_plaintext, ascon_finalize, int_to_bytes

REG_STATEOUT = 0x0e


def oracle_final_state(key16, nonce16):
    from ascon_ref import int_to_bytes
    k = len(key16) * 8
    S = [0, 0, 0, 0, 0]
    ascon_initialize(S, k, 8, 12, 6, 1, key16, nonce16)
    ascon_process_associated_data(S, 6, 8, b'\x00' * 4)
    ascon_process_plaintext(S, 6, 8, b'\x00' * 4)
    ascon_finalize(S, 8, 12, key16)
    return b''.join(int_to_bytes(w, 8) for w in S)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-b', '--bitstream',
                    default='vivado_ascon/ascon_cw305_top.bit')
    ap.add_argument('-n', '--n-tests', type=int, default=5)
    args = ap.parse_args()

    t = connect_target(args.bitstream)
    target = t._t

    rng = np.random.default_rng(7)
    ok = 0
    for i in range(args.n_tests):
        key, nonce = rng.bytes(16), rng.bytes(16)
        t.loadEncryptionKey(key)
        t.loadInput(nonce)
        t.go()
        raw = bytes(target.fpga_read(REG_STATEOUT, 40))
        exp_raw = oracle_final_state(key, nonce)
        match = raw == exp_raw
        ok += match
        print(f'test {i}: {"MATCH" if match else "MISMATCH"}')
        if not match:
            print(f'  got: {raw.hex()}')
            print(f'  exp: {exp_raw.hex()}')

    print(f'\n{ok}/{args.n_tests} state readbacks match oracle exactly')
    print('VERDICT:', 'UNMASKED STATE FULLY OBSERVABLE' if ok == args.n_tests
          else 'state mismatch - investigate')


if __name__ == '__main__':
    main()
