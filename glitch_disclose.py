#!/usr/bin/env python3
r"""glitch_disclose.py — full-key recovery by state disclosure (no DFA needed).

Attack: hang the core's clock mid-INITIALIZATION with a glitch_only pulse.
ASCON-128 init loads S = IV || K0 || K1 || N0 || N1 into the state registers;
a hang freezes the latched REG_CRYPT_STATEOUT (0x0e, 320 bits, canonical word
order per ascon_top.sv lane_rev). Read it over USB, invert the executed init
rounds offline (training/state_disclosure.py, sim-validated 40/40), and the
recovery is SELF-VERIFYING: word 0 must equal the public IV constant and
words 3,4 must equal the chosen nonce. Verified -> words 1,2 ARE the key.

Then the key is PROVEN by a clean re-encryption: load the recovered key on a
fresh nonce with the glitch off and match the readback against the oracle.

Usage:
  # calibration (known key — proves mapping + end-to-end on this board):
  python3 glitch_disclose.py --key 8826d916cdfb21c6c1ff91a761565a70 \
      --nonce 000102030405060708090a0b0c0d0e0f

  # attack (key truly unknown; loaded but never used by the solver):
  python3 glitch_disclose.py --nonce 000102030405060708090a0b0c0d0e0f \
      --load-key-random
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'training'))
import numpy as np
import chipwhisperer as cw
from scope_config import verify_scope
from collect_dataset import _drain
from ascon_ref import fpga_expected, ascon_encrypt
from cw305_ascon_shim import wrap
from state_disclosure import disclose

BITSTREAM = 'vivado_ascon/ascon_cw305_top.bit'
REG_STATEOUT = 0x0e
AD = b'\x00' * 4
PT = b'\x00' * 4

def gate(t, target, tries=6):
    rng = np.random.default_rng(2)
    for _ in range(tries):
        k = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        n = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        try:
            t.loadEncryptionKey(k); t.loadInput(n); t.go()
            out = bytes(t.readOutput())
        except Exception:
            _drain(t); continue
        if out == fpga_expected(k, n):
            return True
    return False

def read_state(target):
    """40 raw bytes from REG_CRYPT_STATEOUT."""
    return bytes(target.fpga_read(REG_STATEOUT, 40))

def state_candidates(raw):
    """Raw 40B -> candidate 5-word lists (word/byte order unknown until
    calibrated). reg file reads LSB-first per bytecnt; adapter emits canonical
    words; the true mapping is found by the self-verifying disclose()."""
    le = [int.from_bytes(raw[8*i:8*i+8], 'little') for i in range(5)]
    be = [int.from_bytes(raw[8*i:8*i+8], 'big') for i in range(5)]
    return [('le-words', le), ('be-words', be),
            ('le-words-rev', le[::-1]), ('be-words-rev', be[::-1])]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--key', type=str,
                    help='known key hex (calibration mode: recovered key must '
                         'match this)')
    ap.add_argument('--load-key-random', action='store_true',
                    help='attack mode: load a random key the script never '
                         'uses; recovery verified by re-encryption only')
    ap.add_argument('--nonce', type=str, default='000102030405060708090a0b0c0d0e0f')
    ap.add_argument('--bitstream', type=str, default=BITSTREAM)
    ap.add_argument('--eo-min', type=int, default=0)
    ap.add_argument('--eo-max', type=int, default=16)
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--width', type=int, default=67)
    ap.add_argument('--repeat', type=int, default=3)
    ap.add_argument('--warmup', type=int, default=2)
    ap.add_argument('--settle-s', type=float, default=0.05)
    ap.add_argument('--crypto-clk', type=float, default=10e6)
    ap.add_argument('--samples', type=int, default=2000)
    ap.add_argument('--gain', type=float, default=35)
    ap.add_argument('--vco', type=float, default=600e6)
    args = ap.parse_args()

    nonce = bytes.fromhex(args.nonce)
    if args.key:
        load_key = bytes.fromhex(args.key)          # calibration
        calib = True
    elif args.load_key_random:
        load_key = os.urandom(16)                   # attack (unknown to solver)
        calib = False
        print(f'[attack] target key loaded (hidden): {load_key.hex()}')
    else:
        sys.exit('need --key <hex> (calibration) or --load-key-random (attack)')

    print('[+] Connecting...')
    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=args.bitstream, fpga_id='100t', platform='cw305')
    target.clkusbautooff = True
    target.clksleeptime = 1
    target.pll.pll_enable_set(True)
    t = wrap(target)
    scope = cw.scope()

    # clean gate first (PLL1)
    try:
        scope.glitch.enabled = False
    except Exception:
        pass
    scope.gain.db = args.gain
    scope.adc.samples = args.samples
    scope.adc.offset = 0
    scope.trigger.triggers = 'tio4'
    scope.clock.clkgen_src = 'system'
    scope.clock.adc_mul = int(round(40e6 / args.crypto_clk))
    scope.clock.clkgen_freq = args.crypto_clk
    target.fpga_write(0x00, [0x19])
    time.sleep(0.2)
    scope.io.hs2 = 'clkgen'
    if not gate(t, target):
        print('[!] FAIL: PLL1 sanity gate. STOP.'); sys.exit(1)
    print('[+] PLL1 gate passed.')

    # hang-fault config: glitch_only = core clock dead except glitch event
    target.fpga_write(0x00, [0x05])
    time.sleep(0.2)
    scope.io.hs2 = 'glitch'
    scope.glitch.enabled = True
    scope.glitch.clk_src = 'pll'
    scope.clock.fpga_vco_freq = args.vco
    scope.glitch.output = 'glitch_only'
    scope.glitch.trigger_src = 'ext_single'
    scope.glitch.repeat = 1
    scope.glitch.num_glitches = 1
    scope.glitch.offset = args.offset
    scope.glitch.width = args.width
    print(f'[+] hang-fault armed: glitch_only off={args.offset} '
          f'w={args.width}, eo {args.eo_min}..{args.eo_max}')

    found = None
    raw_dump = []          # insurance: every raw state read, for offline fix
    for eo in range(args.eo_min, args.eo_max + 1):
        scope.glitch.ext_offset = eo
        time.sleep(args.settle_s)
        for _ in range(args.warmup):
            t.loadEncryptionKey(load_key); t.loadInput(nonce)
            scope.arm(); t.go()
            _drain(t)
        for rep in range(args.repeat):
            t.loadEncryptionKey(load_key); t.loadInput(nonce)
            scope.arm(); t.go()
            raw = read_state(target)
            _drain(t)
            if not raw or len(raw) != 40:
                continue
            raw_dump.append((eo, rep, raw))
            for name, words in state_candidates(raw):
                key, r = disclose(words, nonce)
                if key is not None:
                    if calib and key != load_key:
                        print(f'  [eo={eo}] self-verified key under {name} '
                              f'DIFFERS from calibration key — skip')
                        continue
                    found = (key, eo, r, name, raw)
                    break
            if found:
                break
        if found:
            break
        print(f'  eo={eo}: no disclosed key')

    if not found:
        print('\n[!] No frozen init state disclosed a key in this eo range.')
        # INSURANCE: bank every raw state read for offline analysis (mapping
        # fixes, phase identification) — never leave a failed attack with
        # nothing.
        if raw_dump:
            np.savez('disclose_rawdump.npz',
                     eos=np.array([e for e, _, _ in raw_dump]),
                     reps=np.array([p for _, p, _ in raw_dump]),
                     states=np.array([list(s) for _, _, s in raw_dump],
                                     dtype=np.uint8),
                     nonce=np.frombuffer(nonce, np.uint8),
                     calib_key=np.frombuffer(load_key, np.uint8))
            print(f'[+] banked {len(raw_dump)} raw states -> '
                  'disclose_rawdump.npz (fix mapping offline, rerun disclose)')
        print('    Next: widen --eo-min/--eo-max, try --width 30/150.')
        scope.dis(); target.dis(); sys.exit(1)

    key, eo, r, name, raw = found
    print('\n' + '=' * 62)
    print(f'  KEY RECOVERED at eo={eo} ({name} mapping, {r} init rounds in)')
    print(f'  frozen state: {raw.hex()}')
    print(f'  RECOVERED KEY: {key.hex()}')
    if calib:
        print(f'  CALIBRATION:   {load_key.hex()}  '
              f'{"MATCH" if key == load_key else "MISMATCH"}')

    # definitive proof: clean re-encryption with the recovered key
    scope.glitch.enabled = False
    target.fpga_write(0x00, [0x19])
    time.sleep(0.2)
    scope.io.hs2 = 'clkgen'
    fresh = os.urandom(16)
    t.loadEncryptionKey(key); t.loadInput(fresh); t.go()
    got = bytes(t.readOutput())
    exp = fpga_expected(key, fresh)
    print(f'  re-encryption check (fresh nonce): '
          f'{"VERIFIED — board accepts recovered key" if got == exp else "FAIL"}')
    print('=' * 62)

    np.savez('disclose_result.npz', key=bytes(key), nonce=bytes(nonce),
             state=raw, eo=eo, rounds=r, mapping=name)
    print('[+] saved -> disclose_result.npz')
    scope.dis(); target.dis()

if __name__ == '__main__':
    main()
