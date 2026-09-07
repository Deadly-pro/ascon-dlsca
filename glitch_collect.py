#!/usr/bin/env python3
r"""glitch_collect.py — collect clock-glitch faults at a fixed config, localize
them with the known key, and run the bit-flip DFA to recover the key.

Pipeline (after glitch_cal.py finds a FAULTY config):
  1. Connect board, external-clock gate, glitch-clock gate (same as glitch_cal).
  2. At the fixed (ext_offset, offset, width): repeat N queries with the SAME
     key+nonce (nonce-misuse), capture every faulty tag (natural 16-byte order).
  3. Localize each fault to (col, bit) via dfa_bitflip.localize_fault (known
     key + simulated round-11 S-box-input bit flips).
  4. Save npz {correct_tag, tags, cols, bits} and run the DFA solver to recover
     the round-11 S-box input -> key. Verify with a fresh-query re-encryption.

Usage:
  python3 glitch_collect.py --key <hex> --ext-offset 30 --offset 10 --width 5 \\
      --count 200
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'training'))
import numpy as np
import chipwhisperer as cw
from scope_config import verify_scope, scope_model_name
from collect_dataset import _drain
from ascon_ref import fpga_expected, ascon_encrypt, _le32_words
from cw305_ascon_shim import wrap, REG_TAGOUT
import dfa_bitflip as df

BITSTREAM = 'vivado_ascon/ascon_cw305_top.bit'
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

def read_full_tag(target):
    return _le32_words(bytes(target.fpga_read(REG_TAGOUT, 16)))

def one_query(t, target, scope, key, nonce):
    t.loadEncryptionKey(bytes(key))
    t.loadInput(bytes(nonce))
    scope.arm()   # REQUIRED: with trigger_src='ext_single' the glitch only
                  # fires when the scope is armed AND tio4 triggers.
    t.go()
    return read_full_tag(target)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--key', required=True, type=str)
    ap.add_argument('--nonce', type=str,
                    help='fixed 16-byte nonce hex (data-dependent glitch faults '
                         'need the same key+nonce across runs)')
    ap.add_argument('--bitstream', type=str, default=BITSTREAM)
    ap.add_argument('--ext-offset', type=int, required=True)
    ap.add_argument('--offset', type=int, required=True)
    ap.add_argument('--width', type=int, required=True)
    ap.add_argument('--count', type=int, default=200)
    ap.add_argument('--num-glitches', type=int, default=1,
                    help='burst glitches per trigger (use 4 to match the '
                         'glitch_cal hunt that finds round-11 DFA faults; '
                         'single glitch at late eo hits the output latch)')
    ap.add_argument('--crypto-clk', type=float, default=10e6)
    ap.add_argument('--samples', type=int, default=2000)
    ap.add_argument('--gain', type=float, default=35)
    ap.add_argument('--vco', type=float, default=600e6)
    ap.add_argument('--output', type=str, default='clock_xor',
                    choices=['clock_xor', 'glitch_only', 'clock_or'])
    ap.add_argument('--out', type=str, default='glitch_faults.npz')
    args = ap.parse_args()

    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('key must be 16 bytes hex')
    nonce = bytes.fromhex(args.nonce) if args.nonce else os.urandom(16)
    ref16 = ascon_encrypt(key, nonce, AD, PT)[4:]
    print(f'key   = {key.hex()}')
    print(f'nonce = {nonce.hex()}   tag = {ref16.hex()}')

    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=args.bitstream, fpga_id='100t', platform='cw305')
    target.clkusbautooff = True
    target.clksleeptime = 1
    target.pll.pll_enable_set(True)
    t = wrap(target)
    scope = cw.scope()

    def cfg_scope(glitch_hs2):
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
        scope.io.hs2 = glitch_hs2
        try:
            scope.clock.reset_adc()
        except Exception:
            pass

    cfg_scope('clkgen')
    # Force PLL1 (0x19) + hs2=clkgen — register persists from prior runs.
    target.fpga_write(0x00, [0x19])
    time.sleep(0.2)
    scope.io.hs2 = 'clkgen'
    if not gate(t, target):
        print('[!] FAIL: PLL/external gate. STOP.'); sys.exit(1)
    print('[+] Gate passed (PLL1).')

    # glitch clock config
    target.fpga_write(0x00, [0x05])   # external 20-pin clock source
    time.sleep(0.2)
    scope.io.hs2 = 'glitch'
    scope.glitch.enabled = True
    scope.glitch.clk_src = 'pll'
    scope.clock.fpga_vco_freq = args.vco
    scope.glitch.output = args.output
    scope.glitch.trigger_src = 'ext_single'
    scope.glitch.repeat = 1
    n_glitch = max(1, int(args.num_glitches or 1))
    scope.glitch.num_glitches = n_glitch
    if n_glitch > 1:
        # burst: glitch 0 at ext_offset; glitch i at spacing=1 after i-1,
        # strafing consecutive crypto cycles (same as glitch_cal's hunt).
        scope.glitch.ext_offset = [int(args.ext_offset)] + [1] * (n_glitch - 1)
        print(f'[+] burst mode: {n_glitch} glitches per trigger '
              f'(first at eo={args.ext_offset})')
    else:
        scope.glitch.ext_offset = args.ext_offset
    scope.glitch.offset = args.offset
    scope.glitch.width = args.width
    if not gate(t, target):
        print('[!] FAIL: glitch clock gate. STOP.'); sys.exit(1)
    print('[+] Glitch clock gate passed.')

    # collect
    print(f'\n[+] Collecting {args.count} queries at '
          f'(eo={args.ext_offset}, off={args.offset}, w={args.width})...')
    outcomes = {}
    faulty_tags = []
    t.loadEncryptionKey(bytes(key))
    t0 = time.time()
    for i in range(args.count):
        full = one_query(t, target, scope, key, nonce)
        if full is None or len(full) != 16:
            outcomes['NO_OUT'] = outcomes.get('NO_OUT', 0) + 1
        elif full == ref16:
            outcomes['CORRECT'] = outcomes.get('CORRECT', 0) + 1
        else:
            outcomes['FAULTY'] = outcomes.get('FAULTY', 0) + 1
            faulty_tags.append(bytes(full))
        if (i + 1) % 50 == 0:
            print(f'  {i+1}/{args.count}  {outcomes}  '
                  f'{(i+1)/(time.time()-t0):.0f}/s')
    print(f'  done: {outcomes}')

    if not faulty_tags:
        print('[!] No faulty tags collected at this config.')
        scope.dis(); target.dis(); sys.exit(1)

    # Localize each fault to (col, bit) via the known key.
    print(f'\n[+] Localizing {len(faulty_tags)} faults (known key)...')
    obs = []
    unlocalized = 0
    for ft in faulty_tags:
        loc = df.localize_fault(key, nonce, AD, PT, ft)
        if loc is None:
            unlocalized += 1
        else:
            obs.append((loc[0], loc[1], ft))
    print(f'  localized {len(obs)}, unlocalized {unlocalized}')

    from collections import Counter
    col_counts = Counter(c for c, _, _ in obs)
    print(f'  fault columns hit: {len(col_counts)} distinct '
          f'(top: {col_counts.most_common(8)})')

    # Save ALL faulty tags (raw) FIRST — never lose data to a stats crash.
    all_tags = np.array([list(ft) for ft in faulty_tags], dtype=np.uint8)
    ref_arr = np.frombuffer(ref16, dtype=np.uint8)
    obs_tags = np.array([o[2] for o in obs], dtype=np.uint8) if obs else \
        np.zeros((0, 16), dtype=np.uint8)
    obs_cols = np.array([o[0] for o in obs], dtype=np.uint8) if obs else \
        np.zeros(0, dtype=np.uint8)
    obs_bits = np.array([o[1] for o in obs], dtype=np.uint8) if obs else \
        np.zeros(0, dtype=np.uint8)
    np.savez(args.out,
             correct_tag=ref_arr,
             tags=all_tags,            # ALL faulty tags (raw)
             cols=obs_cols, bits=obs_bits,   # localized subset (may be empty)
             key=bytes(key), nonce=bytes(nonce),
             ext_offset=args.ext_offset, offset=args.offset, width=args.width)
    print(f'[+] saved -> {args.out} ({len(all_tags)} raw faults, '
          f'{len(obs)} localized)')
    # diff diagnostics (after save; axis=1 on the 2-D array)
    if len(all_tags):
        nbyte_diff = (all_tags != ref_arr).sum(axis=1)
        nbit_diff = np.unpackbits(all_tags ^ ref_arr, axis=1).sum(axis=1)
        print(f'    tag byte-diffs: {nbyte_diff.min()}..{nbyte_diff.max()} bytes '
              f'(median {int(np.median(nbyte_diff))})')
        print(f'    tag bit-diffs:  {nbit_diff.min()}..{nbit_diff.max()} bits '
              f'(median {int(np.median(nbit_diff))})')

    # Solve: per-column DFA from the labeled observations.
    recovered = {}
    for col in sorted(set(c for c, _, _ in obs)):
        fl = []
        for c, b, ft in obs:
            if c != col:
                continue
            Y, P = df.tag_diff_to_pattern(ref16, ft)
            dy = sum((1 << j) for j in range(5) if (P[j] >> col) & 1)
            fl.append((dy, 1 << b))
        x = df.solve_column(fl)
        if x is not None:
            recovered[col] = x
    print(f'  DFA recovered {len(recovered)}/64 columns '
          f'(need all for key)')

    if len(recovered) == 64:
        rk = df.recover_key(recovered, ref16)
        if rk is not None:
            print(f'\n  RECOVERED KEY: {rk.hex()}')
            print(f'  TRUE KEY:      {key.hex()}')
            print(f'  MATCH: {rk == key}')
        else:
            print('  key recovery failed (columns inconsistent).')
    else:
        print(f'  Need faults on all 64 columns for the key; this config only '
              f'hit {len(recovered)}. Collect at other (ext_offset,width) '
              f'configs and merge (see dfa_bitflip --faults).')

    scope.dis(); target.dis()

if __name__ == '__main__':
    main()
