#!/usr/bin/env python3
"""verify_oracle.py — confirm the Python oracle matches standard ASCON-128.

Computes fpga_expected for 3 known vectors and round-trip verifies
ascon_encrypt/ascon_decrypt. Also writes the case1 expected value to
tb_verify_exp.txt for optional Verilator/iverilog simulation.
"""
import ascon_ref
import os

HERE = os.path.dirname(os.path.abspath(__file__))

VECTORS = [
    # (key_hex, nonce_hex, expected_readback_hex)
    # case1: K=N=000102030405060708090a0b0c0d0e0f
    ('000102030405060708090a0b0c0d0e0f', '000102030405060708090a0b0c0d0e0f',
     '19c8f96a6b6a4fe5caa719a719378c6a'),
    # case2: K=deadbeef..., N=10203040...
    ('deadbeefcafebabe0001020304050607', '102030405060708090a0b0c0d0e0f000',
     '94f0b9bc9fa873085c828fe6d1dc9341'),
    # case3: K=N=all zeros
    ('00000000000000000000000000000000', '00000000000000000000000000000000',
     '3e2a56698ec81e2e053815e89761cfb5'),
]


def main():
    ok = True

    # 1. oracle verification
    print("=== Oracle verification ===")
    for k, n, exp in VECTORS:
        got = ascon_ref.fpga_expected(bytes.fromhex(k), bytes.fromhex(n))
        status = "OK" if got.hex() == exp else "FAIL"
        if got.hex() != exp:
            ok = False
        print(f"  {status}  K={k[:8]}...  N={n[:8]}...")
        if got.hex() != exp:
            print(f"        got={got.hex()}")
            print(f"        exp={exp}")

    # 2. round-trip test
    print("\n=== Round-trip test ===")
    for k, n, _ in VECTORS:
        key = bytes.fromhex(k)
        nonce = bytes.fromhex(n)
        ct_tag = ascon_ref.ascon_encrypt(key, nonce, b'\x00\x00\x00\x00', b'\x00\x00\x00\x00')
        pt = ascon_ref.ascon_decrypt(key, nonce, b'\x00\x00\x00\x00', ct_tag)
        status = "OK" if pt == b'\x00\x00\x00\x00' else "FAIL"
        if pt != b'\x00\x00\x00\x00':
            ok = False
        print(f"  {status}  decrypt -> '{pt.hex()}'")

    # 3. write expected value for sim TB
    k, n, _ = VECTORS[0]
    exp = ascon_ref.fpga_expected(bytes.fromhex(k), bytes.fromhex(n))
    with open(os.path.join(HERE, 'vivado_ascon', 'tb_verify_exp.txt'), 'w') as f:
        f.write(exp.hex() + '\n')
    print(f"\n  wrote tb_verify_exp.txt = {exp.hex()}")

    # 4. batch performance
    print("\n=== Batch performance ===")
    import time, os as _os
    pairs = [(bytes.fromhex(k), bytes.fromhex(n)) for k, n, _ in VECTORS] * 333  # 999 pairs
    t0 = time.time()
    result = ascon_ref.batch_fpga_expected(pairs)
    dt = time.time() - t0
    print(f"  {len(result)} pairs in {dt:.2f}s ({dt/len(result)*1e3:.1f} ms/pair)")

    if ok:
        print("\n[+] ALL CHECKS PASSED")
    else:
        print("\n[!] SOME CHECKS FAILED")
        raise SystemExit(1)


if __name__ == '__main__':
    main()
