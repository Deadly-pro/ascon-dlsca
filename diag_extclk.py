#!/usr/bin/env python3
r"""diag_extclk.py — one-shot: is the Husky actually clocking the CW305 crypto core?

Tests in order (ALL use the AsconMux shim like sanity_check.py, not raw target):
  1. Normal mode (PLL1): MUST pass (sanity equivalent).
  2. External-clock mode WITHOUT register write (relies on J16=1 + hs2='clkgen').
  3. Register 0x05 (20-pin select).
  4. Register 0x19 (repo default) + glitch enabled, hs2='glitch'.
Prints PASS/FAIL per step. Run with J16=1.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chipwhisperer as cw
import numpy as np
from ascon_ref import fpga_expected
from cw305_ascon_shim import wrap
from collect_dataset import _drain

BITSTREAM = 'vivado_ascon/ascon_cw305_top.bit'
RNG = np.random.default_rng(7)

def ct_sanity(t, tries=6):
    """One known-key query via the AsconMux shim (same as sanity_check.py)."""
    for _ in range(tries):
        k = bytes(RNG.integers(0, 256, 16, dtype=np.uint8))
        n = bytes(RNG.integers(0, 256, 16, dtype=np.uint8))
        try:
            t.loadEncryptionKey(k)
            t.loadInput(n)
            t.go()
            out = bytes(t.readOutput())
        except Exception:
            _drain(t)
            continue
        if out == fpga_expected(k, n):
            return True
    return False

def set_pll(target):
    target.pll.pll_enable_set(True)
    target.pll.pll_outenable_set(False, 0)
    target.pll.pll_outenable_set(True, 1)
    target.pll.pll_outenable_set(False, 2)
    target.pll.pll_outfreq_set(10e6, 1)

def main():
    print('[+] Opening CW305...')
    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=BITSTREAM, fpga_id='100t', platform='cw305')
    target.clkusbautooff = True
    target.clksleeptime = 1
    set_pll(target)
    t = wrap(target)          # <<< AsconMux shim (the whole point)

    scope = cw.scope()
    try:
        scope.glitch.enabled = False
    except Exception:
        pass
    scope.gain.db = 35
    scope.adc.samples = 2000
    scope.adc.offset = 0
    scope.trigger.triggers = 'tio4'

    # ---- Step 1: PLL1 (no external clock) ----
    scope.io.hs2 = 'clkgen'
    scope.clock.clkgen_src = 'system'
    scope.clock.adc_mul = 1
    scope.clock.clkgen_freq = 10e6
    try:
        scope.clock.reset_adc()
    except Exception:
        pass
    print('\n[1] Normal PLL1 mode:')
    ok1 = ct_sanity(t)
    print('   ct_sanity:', 'PASS' if ok1 else 'FAIL')
    cs = target.fpga_read(0x00, 1)
    print('   REG_CLKSETTINGS =', hex(cs[0]) if cs else '?')

    # ---- Step 2: J16=1 external, no register write ----
    print('\n[2] J16=1 external (no reg write, hs2=clkgen):')
    ok2 = ct_sanity(t)
    print('   ct_sanity:', 'PASS' if ok2 else 'FAIL')
    cs = target.fpga_read(0x00, 1)
    print('   REG_CLKSETTINGS =', hex(cs[0]) if cs else '?')

    # ---- Step 3: register 0x05 ----
    print('\n[3] Register 0x05 (20-pin select):')
    target.fpga_write(0x00, [0x05])
    time.sleep(0.2)
    ok3 = ct_sanity(t)
    print('   ct_sanity:', 'PASS' if ok3 else 'FAIL')
    cs = target.fpga_read(0x00, 1)
    print('   REG_CLKSETTINGS =', hex(cs[0]) if cs else '?')

    # ---- Step 4: 0x19 + glitch hs2 ----
    print('\n[4] Reg 0x19 + glitch enabled, hs2=glitch:')
    target.fpga_write(0x00, [0x19])
    time.sleep(0.2)
    scope.io.hs2 = 'glitch'
    try:
        scope.glitch.enabled = True
        scope.glitch.clk_src = 'pll'
        scope.clock.fpga_vco_freq = 600e6
        scope.glitch.output = 'clock_xor'
        scope.glitch.trigger_src = 'ext_single'
        scope.glitch.repeat = 1
        scope.glitch.ext_offset = 0
    except Exception as e:
        print('   glitch cfg error:', e)
    ok4 = ct_sanity(t)
    print('   ct_sanity:', 'PASS' if ok4 else 'FAIL')
    cs = target.fpga_read(0x00, 1)
    print('   REG_CLKSETTINGS =', hex(cs[0]) if cs else '?')
    try:
        print('   mmcm_locked =', scope.glitch.mmcm_locked)
    except Exception:
        pass

    # ---- Step 5: TRUE glitch clock into core (0x05 = 20-pin ext + hs2=glitch) ----
    # 0x19 = PLL1 per clocks.v (clock_reg[2:0]==001) so step 4 never used the
    # glitch clock. 0x05 (101) selects the 20-pin; with hs2='glitch' the glitch
    # module clock must drive the core. offset=width=0 -> clean pass-through.
    print('\n[5] Reg 0x05 + hs2=glitch, glitch on (offset/width 0 = clean clock):')
    target.fpga_write(0x00, [0x05])
    time.sleep(0.2)
    scope.io.hs2 = 'glitch'
    try:
        scope.glitch.enabled = True
        scope.glitch.clk_src = 'pll'
        scope.clock.fpga_vco_freq = 600e6
        scope.glitch.output = 'clock_xor'
        scope.glitch.trigger_src = 'ext_single'
        scope.glitch.repeat = 1
        scope.glitch.ext_offset = 0
        scope.glitch.offset = 0
        scope.glitch.width = 0
        scope.glitch.num_glitches = 1
    except Exception as e:
        print('   glitch cfg error:', e)
    try:
        print('   phase_shift_steps =', scope.glitch.phase_shift_steps)
    except Exception:
        pass
    ok5 = ct_sanity(t)
    print('   ct_sanity:', 'PASS' if ok5 else 'FAIL')

    scope.dis()
    target.dis()
    print('\nVerdict:')
    print(f'  PLL1 mode:             {"PASS" if ok1 else "FAIL"} (must be PASS)')
    print(f'  J16 ext (no reg):      {"PASS" if ok2 else "FAIL"}')
    print(f'  reg 0x05 ext:          {"PASS" if ok3 else "FAIL"}')
    print(f'  0x19 + glitch (PLL1):  {"PASS" if ok4 else "FAIL"}')
    print(f'  0x05 + glitch clock:   {"PASS" if ok5 else "FAIL"}')

if __name__ == '__main__':
    main()
