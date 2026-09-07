#!/usr/bin/env python3
r"""glitch_cal.py — find the clock-glitch (ext_offset, offset, width) window that
produces reproducible faulty ciphertext+tag on the CW305, and optionally
collect faults for the bit-flip DFA.

Usage (all gate first, then sweep / collect / repeat):
  python3 glitch_cal.py --key <hex> --sweep 5000 --max-ext-offset 120
  python3 glitch_cal.py --key <hex> --ext-offset 30 --offset 10 --width 5 --repeat 30
  python3 glitch_cal.py --key <hex> --collect ...   (collect DFA faults at a config)

Husky semantics (NOT CW-Lite percent):
  * offset/width are integer PHASE-SHIFT STEPS in [0, phase_shift_steps/2).
    Read scope.glitch.phase_shift_steps at runtime; sweep in fractions of it.
  * ext_offset = number of SOURCE-CLOCK CYCLES between the tio4 trigger and the
    glitch — this chooses WHICH crypto cycle is faulted (the DFA needs faults
    near the end of the finalization p^12).
  * trigger_src = 'ext_single' so one armed query fires exactly one glitch.
"""
import sys, os, time, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import chipwhisperer as cw
from scope_config import verify_scope, scope_model_name
from collect_dataset import _drain
from ascon_ref import fpga_expected, ascon_encrypt, _le32_words
from cw305_ascon_shim import wrap, REG_TAGOUT

BITSTREAM = 'vivado_ascon/ascon_cw305_top.bit'

def connect(bitstream):
    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=bitstream, fpga_id='100t', platform='cw305')
    target.clkusbautooff = True
    target.clksleeptime = 1
    target.pll.pll_enable_set(True)
    target.pll.pll_outenable_set(False, 0)
    target.pll.pll_outenable_set(True, 1)
    target.pll.pll_outenable_set(False, 2)
    target.pll.pll_outfreq_set(10e6, 1)
    return target, wrap(target)

def configure_scope(scope, crypto_hz=10e6, samples=2000, gain=35):
    try:
        scope.glitch.enabled = False
    except Exception:
        pass
    scope.gain.db = gain
    scope.adc.samples = samples
    scope.adc.offset = 0
    scope.trigger.triggers = 'tio4'
    scope.clock.clkgen_src = 'system'
    scope.clock.adc_mul = int(round(40e6 / crypto_hz))
    scope.clock.clkgen_freq = crypto_hz
    try:
        scope.clock.reset_adc()
    except Exception:
        pass

def gate(t, target, tries=6):
    """PLL1-mode sanity (same as sanity_check) BEFORE touching glitch clock."""
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

def read_full_tag(target, t):
    """Natural-order full 16-byte tag from REG_TAGOUT (le32 self-inverse)."""
    raw = bytes(target.fpga_read(REG_TAGOUT, 16))
    return _le32_words(raw)

def one_query(t, target, key, nonce):
    """Run one encryption; return (natural_full_tag16, readOutput16)."""
    t.loadEncryptionKey(bytes(key))
    t.loadInput(bytes(nonce))
    t.go()
    return read_full_tag(target, t), bytes(t.readOutput())

def classify_glitch(t, target, scope, key, nonce, ref16, ref_readout):
    """Run one glitched query. Returns (class, tag16).

    class in {CORRECT, FTL (fault, ct intact = finalization, DFA-usable),
              FCT (fault, ct also wrong = early/mid crypto), NO_OUT}.
    ct is emitted before the finalization p^12, so ct intact + tag wrong means
    the glitch landed in the finalization — the DFA target. scope.arm() is
    REQUIRED (ext_single only glitches when armed AND tio4 fires)."""
    try:
        scope.arm()
        full, ro = one_query(t, target, key, nonce)
    except Exception:
        _drain(t)
        return 'NO_OUT', None
    if full is None or len(full) != 16 or ro is None:
        return 'NO_OUT', None
    if full == ref16:
        return 'CORRECT', full
    # tag wrong. Is the ct tail still right?  ro = le32(tag[:12])+le32(ct).
    if ro[12:16] == ref_readout[12:16]:
        return 'FTL', full   # ct intact -> fault in finalization
    return 'FCT', full       # ct corrupted -> fault earlier than finalization

def set_burst_eo(scope, eo, n, spacing=1):
    """Set glitch trigger position for single or burst mode.

    num_glitches=1: plain ext_offset. >1: glitch 0 at `eo` cycles after the
    trigger; glitch i fires 2+ext_offset[i] cycles after glitch i-1, so a
    per-glitch value of `spacing` walks consecutive crypto cycles — a burst
    strafing rounds eo..eo+n-1 in one query."""
    if n <= 1:
        scope.glitch.ext_offset = int(eo)
    else:
        offs = [int(eo)] + [spacing] * (n - 1)
        scope.glitch.ext_offset = offs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--key', type=str, default='8826d916cdfb21c6c1ff91a761565a70')
    ap.add_argument('--nonce', type=str,
                    help='fixed 16-byte nonce hex (data-dependent glitch faults '
                         'need the same key+nonce across runs)')
    ap.add_argument('--nonce-hunt', type=int,
                    help='hunt N random nonces: coarse settled eo scan each, '
                         'flag configs whose FTL fault bit-diff falls in the '
                         'DFA band [10,40] bits (round-11/12 S-box input)')
    ap.add_argument('--seed', type=int, default=0,
                    help='RNG seed for --nonce-hunt (0 = nondeterministic)')
    ap.add_argument('--num-glitches', type=int, default=1,
                    help='glitches per trigger (Husky up to 32). >1 = burst: '
                         'with num_glitches=k and ext_offset list, glitch i '
                         'fires 2+ext_offset[i] cycles after glitch i-1. '
                         'Bursts strafe several rounds in one query.')
    ap.add_argument('--vccint', type=float,
                    help='core voltage in V (CW305 programmable VCCINT, the '
                         'board\'s intended FI knob; e.g. 0.90/0.88/0.85). '
                         'Undervolting makes setup marginal -> faults at many '
                         'more cycles. Restored to 1.0V at exit.')
    ap.add_argument('--bitstream', type=str, default=BITSTREAM)
    ap.add_argument('--crypto-clk', type=float, default=10e6)
    ap.add_argument('--samples', type=int, default=2000)
    ap.add_argument('--gain', type=float, default=35)
    ap.add_argument('--sweep', type=int, help='number of (ext_offset x offset) combos')
    ap.add_argument('--eo-sweep', type=int,
                    help='sweep ext_offset 0..max at fixed (offset, width), '
                         'N repeats each — find FTL (finalization) window')
    ap.add_argument('--ftl-hunt', action='store_true',
                    help='dense hunt: full offset sweep at every eo in '
                         '[--eo-min, --eo-max], 3 probes each, flag FTL live')
    ap.add_argument('--steady-scan', action='store_true',
                    help='SETTLED scan: for each (eo, offset) set the config, '
                         'sleep for DCM relock, discard warmup, then probe — '
                         'sweeps that change offset/width every iteration read '
                         'DCM-relock transients as fake faults; this avoids that')
    ap.add_argument('--diff-by-eo', action='store_true',
                    help='sweep eo at fixed (offset,width); report the tag '
                         'bit-diff of faults per eo — the LAST-round fault '
                         'window is where bit-diff collapses to a few bits')
    ap.add_argument('--warmup', type=int, default=5,
                    help='queries discarded after each config change '
                         '(DCM relock settle)')
    ap.add_argument('--settle-s', type=float, default=0.1,
                    help='sleep seconds after config change before probing')
    ap.add_argument('--eo-min', type=int, default=0)
    ap.add_argument('--eo-max', type=int, default=85)
    ap.add_argument('--off-steps', type=int, default=24,
                    help='offset resolution for --ftl-hunt (fraction of period)')
    ap.add_argument('--width-sweep', type=int,
                    help='sweep width 0..period at fixed (ext_offset, offset)')
    ap.add_argument('--max-ext-offset', type=int, default=120)
    ap.add_argument('--ext-offset', type=int)
    ap.add_argument('--offset', type=int)
    ap.add_argument('--width', type=int)
    ap.add_argument('--repeat', type=int, default=1)
    ap.add_argument('--out', type=str, default='glitch_results.npz')
    ap.add_argument('--vco', type=float, default=600e6)
    ap.add_argument('--sweep-width-pct', type=float, default=0.25,
                    help='sweep pulse width as a fraction of the period (Husky)')
    ap.add_argument('--output', type=str, default='clock_xor',
                    choices=['clock_xor', 'glitch_only', 'clock_or', 'enable_only'])
    args = ap.parse_args()

    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('key must be 16 bytes hex')
    print(f'key = {key.hex()}')
    print('[+] Connecting...')
    target, t = connect(args.bitstream)
    print('[+] target up (PLL1)')
    scope = cw.scope()
    configure_scope(scope, args.crypto_clk, args.samples, args.gain)
    verify_scope(scope)

    # 1) Clean gate (PLL1, no external clock) — MUST pass.
    # IMPORTANT: the FPGA is NOT reprogrammed when the bitstream is already
    # loaded, so REG_CLKSETTINGS retains whatever the last run left (diag ends
    # on 0x05 = external). Force PLL1 mode (0x19 per clocks.v) + hs2=clkgen so
    # this gate really tests PLL1 regardless of prior register state.
    print('\n[+] Gate 1: PLL1 sanity (glitch disabled)...')
    target.fpga_write(0x00, [0x19])
    time.sleep(0.2)
    scope.io.hs2 = 'clkgen'
    if not gate(t, target):
        print('[!] FAIL: core not running in PLL1 mode. STOP.')
        sys.exit(1)
    print('[+] Gate 1 passed.')

    # Optional VCCINT undervolting (CW305 programmable core supply — the
    # board's intended FI knob). Lower Vcc -> global setup marginality ->
    # faults at many more cycles. Gate again at the new voltage; too low
    # and the core stops passing KAT (report and stop).
    if args.vccint is not None:
        print(f'\n[+] Setting VCCINT = {args.vccint} V ...')
        try:
            target.vccint_set(args.vccint)
            time.sleep(0.5)
        except Exception as e:
            print(f'[!] vccint_set failed: {e}'); sys.exit(1)
        got = target.vccint_get()
        print(f'    readback: {got} V')
        if not gate(t, target):
            print('[!] core fails KAT at this voltage — raise --vccint. STOP.')
            try: target.vccint_set(1.0)
            except Exception: pass
            sys.exit(1)
        print('[+] core passes KAT at reduced voltage (marginal but functional).')

    # 2) External-clock gate (reg 0x05 + hs2=clkgen) — proves clock path.
    target.fpga_write(0x00, [0x05])
    time.sleep(0.2)
    scope.io.hs2 = 'clkgen'
    if not gate(t, target):
        print('[!] FAIL: core not running on external clock. Check J16 + ribbon.')
        sys.exit(1)
    print('[+] Gate 2 passed: core runs on external clock.')

    # 3) Glitch-clock gate (0x05 + hs2=glitch, offset/width 0 = clean clock).
    scope.io.hs2 = 'glitch'
    scope.glitch.enabled = True
    scope.glitch.clk_src = 'pll'
    scope.clock.fpga_vco_freq = args.vco
    scope.glitch.output = args.output
    scope.glitch.trigger_src = 'ext_single'
    scope.glitch.repeat = 1
    n_glitch = max(1, int(getattr(args, 'num_glitches', 1) or 1))
    scope.glitch.num_glitches = n_glitch
    if n_glitch > 1:
        # burst: glitch 0 at ext_offset; glitch i at ext_offset + i*spacing
        # (Husky: glitch i fires 2+ext_offset[i] cycles after glitch i-1,
        # so a constant per-glitch spacing of 1 cycle straes consecutive
        # crypto cycles). Values are set per-mode below; here just arm count.
        print(f'[+] burst mode: {n_glitch} glitches per trigger')
    scope.glitch.offset = 0
    scope.glitch.width = 0
    scope.glitch.ext_offset = 0
    if not gate(t, target):
        print('[!] FAIL: core not running on glitch module clock (offset/width 0).')
        sys.exit(1)
    try:
        pss = int(scope.glitch.phase_shift_steps)
    except Exception:
        pss = 0
    print(f'[+] Gate 3 passed: glitch clock drives core. phase_shift_steps={pss}')

    # ---- NONCE-HUNT mode: resample the data-dependent fault landscape ----
    # The runt only corrupts registers whose data TRANSITIONS at the glitched
    # edge; with a fixed key+nonce the fault points are fixed (we proved: one
    # nonce -> faults at eo=31/45 only, DFA band empty). Each NEW nonce
    # redeals which cycles are faultable. Hunt N nonces over the finalization
    # eo band; flag any config whose FTL fault bit-diff is in [5,45] bits
    # (the round-11/12 S-box-input DFA band: verified 6..42 across 20 random
    # nonces in simulation; excludes 1-bit output-latch and ~62-bit early).
    if args.nonce_hunt:
        BAND = (5, 45)
        w = args.width if args.width is not None else max(1, int(pss * 0.02))
        offs = [0, pss // 2, pss - 1] if pss > 0 else [0, 25, 49]
        eos = np.arange(args.eo_min, args.eo_max + 1)
        probes = max(3, min(args.repeat, 8))
        print(f'\n[+] Nonce hunt: {args.nonce_hunt} nonces x {len(eos)} eo x '
              f'{len(offs)} offsets (w={w}, {probes} probes) — flagging '
              f'bit-diff in {BAND}...')
        t.loadEncryptionKey(bytes(key))
        rng = np.random.default_rng(args.seed if args.seed else None)
        band_hits, any_fault = [], []
        t0 = time.time()
        for ni in range(args.nonce_hunt):
            nonce = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
            ref16 = ascon_encrypt(key, nonce, b'\x00' * 4, b'\x00' * 4)[4:]
            ref_ro = fpga_expected(key, nonce)
            t.loadInput(nonce)
            for eo in eos:
                set_burst_eo(scope, eo, n_glitch)
                for off in offs:
                    scope.glitch.offset = int(off)
                    scope.glitch.width = int(w)
                    time.sleep(args.settle_s)
                    for _ in range(2):   # warmup after phase change
                        classify_glitch(t, target, scope, key, nonce,
                                        ref16, ref_ro)
                    for _ in range(probes):
                        cls, full = classify_glitch(t, target, scope, key,
                                                    nonce, ref16, ref_ro)
                        if cls == 'FTL' and full is not None:
                            bd = int(np.unpackbits(
                                np.frombuffer(bytes(full), np.uint8) ^
                                np.frombuffer(ref16, np.uint8)).sum())
                            any_fault.append((ni, int(eo), int(off), w, bd))
                            if BAND[0] <= bd <= BAND[1]:
                                band_hits.append((nonce.hex(), int(eo),
                                                  int(off), w, bd, full.hex()))
                                print(f'  *** DFA-BAND HIT nonce#{ni} '
                                      f'eo={eo} off={off} w={w} '
                                      f'bitdiff={bd}')
            if (ni + 1) % 5 == 0:
                dt = time.time() - t0
                print(f'  {ni+1}/{args.nonce_hunt} nonces, '
                      f'{len(any_fault)} faults, {len(band_hits)} in band  '
                      f'({(ni+1)/dt:.1f} nonce/s)')
        print(f'\n  Nonce hunt done: {len(any_fault)} FTL faults across '
              f'{args.nonce_hunt} nonces; {len(band_hits)} in the DFA band')
        from collections import Counter
        print(f'  bit-diff histogram: {dict(Counter(bd for *_ , bd in any_fault))}')
        if band_hits:
            print(f'  band hits (nonce,eo,off,w,diff,tag): {band_hits[:20]}')
            np.savez(args.out, band_hits=np.array(band_hits, dtype=object),
                     key=bytes(key))
            print(f'[+] saved -> {args.out}  (collect these configs with '
                  f'glitch_collect.py at the same nonce)')
        else:
            print('  No band hits. Escalate: --vccint 0.92/0.90/0.88, or '
                  '--width 150/300, or more nonces.')
        if args.vccint is not None:
            try:
                target.vccint_set(1.0)
                print('[+] VCCINT restored to 1.0 V')
            except Exception:
                pass
        scope.dis(); target.dis()
        return

    # Reference tag for the fixed nonce we will query.
    nonce = bytes.fromhex(args.nonce) if args.nonce else os.urandom(16)
    # natural 16-byte tag oracle (ct 4 bytes prefix dropped)
    ref16 = ascon_encrypt(key, nonce, b'\x00' * 4, b'\x00' * 4)[4:]
    ref_readout = fpga_expected(key, nonce)   # expected readOutput() bytes
    print(f'nonce = {nonce.hex()}')
    print(f'tag   = {ref16.hex()}')

    # ---- SWEEP mode: (ext_offset, offset) grid at a configurable width ----
    results = []
    if args.sweep:
        steps = int(np.sqrt(args.sweep))
        ext_offsets = np.unique(np.linspace(0, args.max_ext_offset, steps).astype(int))
        if pss > 0:
            # sweep the FULL period (0..pss-1), not just half — the sensitive
            # region is data-dependent and can sit anywhere in the cycle.
            offsets = np.linspace(0, max(pss - 1, 1), steps).round().astype(int)
            offsets = np.unique(offsets)
        else:  # CW-Lite fallback: percent
            offsets = np.linspace(0, 49, steps)
        # default width: a substantial pulse (25% of period), not 2% — a
        # narrow pulse is too weak to violate setup/hold except at the
        # marginal rising-edge point. Overridable with --width-when-sweeping.
        def_w = max(1, int(pss * args.sweep_width_pct)) if pss > 0 else args.sweep_width_pct
        widths = [def_w]
        print(f'\n[+] Sweeping {len(ext_offsets)}x{len(offsets)} '
              f'(ext_offset x offset, width={widths[0]}, pss={pss}, '
              f'width_pct={args.sweep_width_pct})...')
        t.loadEncryptionKey(bytes(key))
        found = 0
        t0 = time.time()
        for eo in ext_offsets:
            for off in offsets:
                try:
                    scope.glitch.ext_offset = int(eo)
                    scope.glitch.offset = int(off)
                    scope.glitch.width = int(widths[0])
                except Exception as ex:
                    print(f'  cfg error at eo={eo} off={off}: {type(ex).__name__}: {ex}')
                    continue
                cls, full = classify_glitch(t, target, scope, key, nonce, ref16,
                                            ref_readout)
                results.append((int(eo), float(off), float(widths[0]), cls))
                if cls in ('FTL', 'FCT'):
                    found += 1
                if len(results) % 200 == 0:
                    dt = time.time() - t0
                    print(f'  {len(results)}/{len(ext_offsets)*len(offsets)} '
                          f'faulty={found}  {len(results)/dt:.0f}/s  ETA '
                          f'{(len(ext_offsets)*len(offsets)-len(results))/(len(results)/dt):.0f}s')
        print(f'\n  Sweep done: {found} faulty of {len(results)}')
        from collections import Counter
        tally = Counter(r[3] for r in results)
        print(f'  classification: {dict(tally)}')
        faulty = [r for r in results if r[3] in ('FTL', 'FCT')]
        ftl = [r for r in results if r[3] == 'FTL']
        if ftl:
            print(f'  ** {len(ftl)} FINALIZATION faults (ct intact, tag wrong) — '
                  f'DFA-usable!')
            print(f'     (eo,off,width): {ftl[:15]}')
        elif faulty:
            print(f'  Faulty (ct corrupt = early): {faulty[:15]}')
        else:
            print('  NO FAULTY CONFIGS.')
            if tally.get('NO_OUT', 0) > 0:
                print('  >> Most captures returned NO_OUT: glitch is over-driving the')
                print('     clock (core is too aggressive a target). Try --output')
                print('     glitch_only, or --vco 800e6 to shrink the pulse.')
            print('  Try: --output glitch_only, higher --vco 800e6, wider window,')
            print('  slower crypto (--crypto-clk 5e6).')

    # ---- EO-SWEEP mode: find where faults land in the crypto timeline ----
    # At a fixed (offset, width), sweep ext_offset across the whole crypto and
    # classify FTL (ct intact = finalization fault, DFA-usable) vs FCT (early).
    # This maps the glitch to crypto cycles: the FTL window is the target.
    if args.eo_sweep is not None:
        if args.offset is None or args.width is None:
            sys.exit('--eo-sweep needs --offset and --width')
        eos = np.arange(0, args.max_ext_offset + 1)
        print(f'\n[+] eo-sweep: {len(eos)} ext_offsets at off={args.offset} '
              f'w={args.width}, {args.repeat} probes each...')
        t.loadEncryptionKey(bytes(key))
        scope.glitch.offset = int(args.offset)
        scope.glitch.width = int(args.width)
        eo_outcomes = []
        for eo in eos:
            scope.glitch.ext_offset = int(eo)
            counts = {}
            tags_seen = set()
            for _ in range(args.repeat):
                cls, full = classify_glitch(t, target, scope, key, nonce, ref16,
                                            ref_readout)
                counts[cls] = counts.get(cls, 0) + 1
                if full is not None:
                    tags_seen.add(bytes(full))
            eo_outcomes.append((int(eo), counts, len(tags_seen)))
        print('\n  ext_offset -> (CORRECT, FTL, FCT, NO_OUT)  [distinct tags]')
        for eo, counts, ntags in eo_outcomes:
            mark = '  <-- FTL' if counts.get('FTL', 0) > 0 else ''
            print(f'  eo={eo:3d}  C={counts.get("CORRECT",0):2d} '
                  f'FTL={counts.get("FTL",0):2d} FCT={counts.get("FCT",0):2d} '
                  f'NO={counts.get("NO_OUT",0):2d}  [{ntags} tags]{mark}')
        ftl_eos = [eo for eo, counts, _ in eo_outcomes if counts.get('FTL', 0) > 0]
        if ftl_eos:
            print(f'\n  ** FINALIZATION-fault (FTL) ext_offsets: {ftl_eos}')
        else:
            print('\n  No FTL at this (offset,width). Try width near the narrow '
                  'edge (small widths) and offsets across the full period.')
        results = [(eo, args.offset, args.width,
                    'FTL' if counts.get('FTL') else
                    ('FCT' if counts.get('FCT') else 'CORRECT'))
                   for eo, counts, _ in eo_outcomes]

    # ---- DIFF-BY-EO: find where the fault lands in the LAST rounds ----
    # A fault in the last two rounds of the finalization p^12 leaves a SMALL
    # tag bit-diff (a handful of bits); a fault in earlier finalization rounds
    # diffuses through many remaining rounds -> ~half the tag bits differ
    # (62/128 observed). Sweep eo toward the end and report the bit-diff per
    # eo: the DFA window is where the diff collapses to a few bits.
    if args.diff_by_eo:
        if pss <= 0:
            sys.exit('--diff-by-eo needs phase_shift_steps (Husky)')
        if args.offset is None or args.width is None:
            sys.exit('--diff-by-eo needs --offset and --width')
        w = int(args.width)
        eos = np.arange(args.eo_min, args.eo_max + 1)
        nprobe = args.repeat if args.repeat > 1 else 20
        print(f'\n[+] diff-by-eo: eo {args.eo_min}..{args.eo_max} at '
              f'off={args.offset} w={w}, {nprobe} settled probes each...')
        t.loadEncryptionKey(bytes(key))
        scope.glitch.width = w
        print('    eo : FTL/FC-rate   bit-diff (min/med/max)   sample tag')
        best = None
        for eo in eos:
            scope.glitch.ext_offset = int(eo)
            scope.glitch.offset = int(args.offset)
            time.sleep(args.settle_s)
            for _ in range(args.warmup):
                classify_glitch(t, target, scope, key, nonce, ref16, ref_readout)
            diffs = []
            nftl = nfct = 0
            for _ in range(nprobe):
                cls, full = classify_glitch(t, target, scope, key, nonce,
                                            ref16, ref_readout)
                if cls == 'FTL' and full is not None:
                    nftl += 1
                    bd = int(np.unpackbits(
                        np.frombuffer(bytes(full), np.uint8) ^
                        np.frombuffer(ref16, np.uint8)).sum())
                    diffs.append(bd)
                elif cls == 'FCT':
                    nfct += 1
            if diffs:
                dmin, dmed, dmax = min(diffs), int(np.median(diffs)), max(diffs)
                print(f'    {eo:3d}: FTL {nftl:2d}/{nprobe} FCT {nfct:2d}  '
                      f'bitdiff {dmin}/{dmed}/{dmax}')
                if best is None or dmed < best[1]:
                    best = (eo, dmed, dmin)
            elif nftl or nfct:
                print(f'    {eo:3d}: FTL {nftl:2d}/{nprobe} FCT {nfct:2d}')
        if best:
            print(f'\n  ** smallest median diff at eo={best[0]} '
                  f'(med {best[1]}, min {best[2]}) — DFA target window')
            print('     faults here are nearest the last rounds of finalization')
        else:
            print('\n  No FTL faults in this eo range at this (offset,width).')
        results = [(best[0], args.offset, w, 'FTL')] if best else \
                  [(args.eo_min, args.offset, w, 'CORRECT')]

    # ---- STEADY-SCAN: settled per-config measurement (no relock artifacts) ----
    # Sweeps that change offset/width every iteration read DCM-relock
    # transients as fake faults (we proved this: the FTL "hits" at eo=47 did
    # not reproduce in a fixed-config run). This mode sets each config ONCE,
    # sleeps for the DCMs to re-lock, discards warmup queries, then measures.
    if args.steady_scan:
        if pss <= 0:
            sys.exit('--steady-scan needs phase_shift_steps (Husky)')
        w = args.width if args.width is not None else max(1, int(pss * 0.02))
        offsets = np.linspace(0, pss - 1, args.off_steps).round().astype(int)
        offsets = np.unique(offsets)
        eos = np.arange(args.eo_min, args.eo_max + 1)
        nprobe = args.repeat if args.repeat > 1 else 10
        print(f'\n[+] Steady scan: {len(eos)} eo x {len(offsets)} offsets '
              f'(w={w}, warmup={args.warmup}, probe={nprobe}) — settled reads...')
        t.loadEncryptionKey(bytes(key))
        scope.glitch.width = int(w)
        hits = []
        for eo in eos:
            scope.glitch.ext_offset = int(eo)
            for off in offsets:
                scope.glitch.offset = int(off)
                time.sleep(args.settle_s)   # let DCMs re-lock
                for _ in range(args.warmup):
                    classify_glitch(t, target, scope, key, nonce, ref16,
                                    ref_readout)  # discard
                counts = {}
                bd_list = []
                for _ in range(nprobe):
                    cls, full = classify_glitch(t, target, scope, key, nonce,
                                                ref16, ref_readout)
                    counts[cls] = counts.get(cls, 0) + 1
                    if cls == 'FTL' and full is not None:
                        hits.append((int(eo), int(off), int(w), bytes(full)))
                        bd_list.append(int(np.unpackbits(
                            np.frombuffer(bytes(full), np.uint8) ^
                            np.frombuffer(ref16, np.uint8)).sum()))
                if counts.get('FTL', 0) or counts.get('FCT', 0):
                    bdstr = ''
                    if bd_list:
                        bdstr = f'  bitdiff {min(bd_list)}/{int(np.median(bd_list))}/{max(bd_list)}'
                    print(f'  eo={eo:3d} off={off:4d}: {counts}{bdstr}')
        print(f'\n  Steady scan done: {len(hits)} real FTL hits (settled reads)')
        if hits:
            print(f'  hits: {[(a,b,c) for a,b,c,_ in hits][:40]}')
        else:
            print('  No real faults found at any settled (eo, offset).')
            print('  This means the earlier sweep faults were DCM-relock noise.')
            print('  Next: try larger width (--width 100/200/400), or the ')
            print('  fault may need a much wider pulse than 2% of the period.')
        results = [(eo, off, w, 'FTL') for eo, off, w, _ in hits] or \
                  [(args.eo_min, 0, w, 'CORRECT')]

    # ---- FTL-HUNT mode: dense (eo x full-period offset) finalization hunt ----
    # eo-sweep at a single offset is blind: a runt only flips a register whose
    # data transitions at the glitched edge, so the finalization rounds fault
    # at SOME offset, not necessarily off=0. Sweep both dimensions.
    if args.ftl_hunt:
        if pss <= 0:
            sys.exit('--ftl-hunt needs phase_shift_steps (Husky)')
        w = args.width if args.width is not None else max(1, int(pss * 0.02))
        offsets = np.linspace(0, pss - 1, args.off_steps).round().astype(int)
        offsets = np.unique(offsets)
        eos = np.arange(args.eo_min, args.eo_max + 1)
        print(f'\n[+] FTL hunt: {len(eos)} eo x {len(offsets)} offsets '
              f'(w={w}, {args.repeat} probes) — flagging ct-intact faults...')
        t.loadEncryptionKey(bytes(key))
        scope.glitch.width = int(w)
        hits = []
        total = len(eos) * len(offsets)
        done = 0
        t0 = time.time()
        for eo in eos:
            scope.glitch.ext_offset = int(eo)
            for off in offsets:
                scope.glitch.offset = int(off)
                for _ in range(args.repeat):
                    cls, full = classify_glitch(t, target, scope, key, nonce,
                                                ref16, ref_readout)
                    if cls == 'FTL':
                        hits.append((int(eo), int(off), int(w)))
                        print(f'  *** FTL at eo={eo} off={off} w={w} '
                              f'tag={full.hex()}')
                        # don't stop; collect the whole map
                done += 1
                if done % 400 == 0:
                    dt = time.time() - t0
                    print(f'  {done}/{total}  {len(hits)} FTL hits  '
                          f'{done/dt:.0f}/s ETA {(total-done)/(done/dt):.0f}s')
        print(f'\n  FTL hunt done: {len(hits)} finalization-fault configs of '
              f'{done} tested')
        if hits:
            # cluster: report contiguous eo bands so collection can target them
            print(f'  hits: {hits[:40]}')
        else:
            print('  No FTL found. Try: different width (--width 30/100/150),')
            print('  denser offset (--off-steps 48), wider eo (--eo-max 120).')
        results = [(eo, off, w, 'FTL') for eo, off, w in hits] or \
                  [(args.eo_min, 0, w, 'CORRECT')]

    # ---- WIDTH-SWEEP mode: find the correct->faulty width boundary ----
    # At a fixed (ext_offset, offset), width is the real fault-strength knob.
    # Sweep it across the whole period and report the fault fraction per width
    # so you can pick the "mostly correct, occasionally faulty" operating point
    # (rare + clean faults = DFA-usable), not the all-faulty over-drive point.
    if args.width_sweep is not None:
        if args.ext_offset is None or args.offset is None:
            sys.exit('--width-sweep needs --ext-offset and --offset')
        widths = np.linspace(0, max(pss - 1, 1), args.width_sweep).round().astype(int)
        widths = np.unique(widths)
        print(f'\n[+] Width sweep at eo={args.ext_offset} off={args.offset}: '
              f'{len(widths)} widths over [0, {max(pss - 1, 1)}]...')
        t.loadEncryptionKey(bytes(key))
        scope.glitch.ext_offset = int(args.ext_offset)
        scope.glitch.offset = int(args.offset)
        width_outcomes = []
        for w in widths:
            scope.glitch.width = int(w)
            time.sleep(args.settle_s)   # let DCMs re-lock after width change
            for _ in range(args.warmup):
                classify_glitch(t, target, scope, key, nonce, ref16,
                                ref_readout)  # discard relock transients
            # probes per width for a fault-fraction estimate
            nf = 0
            cls_last = None
            bd_list = []
            for _ in range(3):
                cls, full = classify_glitch(t, target, scope, key, nonce,
                                            ref16, ref_readout)
                cls_last = cls
                nf += (cls in ('FTL', 'FCT'))
                if cls == 'FTL' and full is not None:
                    bd_list.append(int(np.unpackbits(
                        np.frombuffer(bytes(full), np.uint8) ^
                        np.frombuffer(ref16, np.uint8)).sum()))
            width_outcomes.append((int(w), nf, nf / 3, cls_last, bd_list))
            bdstr = f' bitdiff {min(bd_list)}/{int(np.median(bd_list))}/{max(bd_list)}' \
                if bd_list else ''
            print(f'  width={w:5d}  faulty {nf}/3  (last={cls_last}){bdstr}')
        print('\n  Boundary (first widths going faulty):')
        for w, nf, frac, cls_last, bd_list in width_outcomes:
            if frac > 0:
                print(f'    width={w}  fault_fraction={frac:.2f}  class={cls_last}')
                break
        results = [(args.ext_offset, args.offset, w,
                    'FTL' if cls_last == 'FTL' else ('FCT' if nf else 'CORRECT'))
                   for w, nf, frac, cls_last, bd_list in width_outcomes]

    # ---- FIXED-CONFIG repeat ----
    if args.ext_offset is not None and args.offset is not None and args.width is not None:
        print(f'\n[+] Fixed config: ext_offset={args.ext_offset} offset={args.offset} '
              f'width={args.width}  N={args.repeat}')
        scope.glitch.ext_offset = int(args.ext_offset)
        scope.glitch.offset = int(args.offset)
        scope.glitch.width = int(args.width)
        outcomes = {}
        faulty_tags = []
        for i in range(args.repeat):
            cls, full = classify_glitch(t, target, scope, key, nonce, ref16,
                                        ref_readout)
            outcomes[cls] = outcomes.get(cls, 0) + 1
            if cls in ('FTL', 'FCT'):
                faulty_tags.append(full)
        print(f'  Outcomes: {outcomes}')
        ftl = outcomes.get('FTL', 0)
        fct = outcomes.get('FCT', 0)
        if ftl or fct:
            # count distinct faulty tags / measure Hamming distance spread
            uniq = set(faulty_tags)
            hd = [sum(a != b for a, b in zip(ref16, ft)) for ft in faulty_tags]
            print(f'  {len(uniq)} distinct faulty tags; tag byte-diff range '
                  f'[{min(hd)}, {max(hd)}]')
            if ftl:
                print(f'  ** {ftl}/{args.repeat} are FINALIZATION faults '
                      f'(ct intact) — DFA-usable')
        results = [(args.ext_offset, args.offset, args.width, c)
                   for c in outcomes for _ in range(outcomes[c])]

    if results:
        arr = np.array([list(r[:3]) + [1 if r[3] in ('FTL', 'FCT') else 0]
                        for r in results], dtype=float)
        np.savez(args.out, configs=arr, key=bytes(key), nonce=nonce,
                 tag=bytes(ref16))
        print(f'[+] saved -> {args.out}')

    scope.dis()
    target.dis()

if __name__ == '__main__':
    main()
