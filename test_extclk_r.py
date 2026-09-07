#!/usr/bin/env python3
r"""test_extclk_r.py — one-shot: does the J16 external (Husky-driven) clock
improve byte-HW / per-bit correlation r vs the internal-PLL numbers?

Board must be set to external clock (J16 high). The crypto clock now comes
from the Husky's clkgen output over the 20-pin ribbon, so crypto and ADC
clocks are phase-coherent (no per-capture sampling drift).
"""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))
import chipwhisperer as cw
from scope_config import scope_model_name, is_husky
from collect_dataset import _drain
from ascon_ref import fpga_expected

BITSTREAM = 'vivado_ascon/ascon_cw305_top.bit'


def measure_r(traces, keys):
    n = len(traces); split = int(0.8 * n)
    Xz = (traces - traces.mean(0)) / (traces.std(0) + 1e-12)
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], float)
    B = np.zeros((n, 128))
    for b in range(16):
        for j in range(8): B[:, b*8+j] = (keys[:, b] >> j) & 1
    hw_rs = []
    for b in range(16):
        z = (hw[:split, b] - hw[:split, b].mean()) / (hw[:split, b].std() + 1e-12)
        r = z @ Xz[:split] / split
        pk = int(np.abs(r).argmax())
        hw_rs.append(abs(np.corrcoef(Xz[split:, pk], hw[split:, b])[0, 1]))
    bit_rs = []
    for c in range(128):
        z = (B[:split, c] - B[:split, c].mean()) / (B[:split, c].std() + 1e-12)
        r = z @ Xz[:split] / split
        pk = int(np.abs(r).argmax())
        bit_rs.append(abs(np.corrcoef(Xz[split:, pk], B[split:, c])[0, 1]))
    bit_rs = np.array(bit_rs)
    rng = np.random.default_rng(0)
    null_max = max(abs((rng.permutation(split) - split//2) / split * Xz[:split, 0]).max()
                   for _ in range(30))
    return (np.mean(hw_rs), np.max(hw_rs), np.mean(bit_rs), np.max(bit_rs),
            int((bit_rs > null_max).sum()), null_max)


def ct_sanity(t, tries=6):
    """One known-key query: readback must match the oracle -> core clocked OK."""
    rng = np.random.default_rng(1)
    for _ in range(tries):
        k = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        n = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        try:
            t.loadEncryptionKey(k)
            t.loadInput(n)
            t.go()
            out = bytes(t.readOutput())
        except Exception as e:
            _drain(t); continue
        if out == fpga_expected(k, n):
            return True, 'ok'
    return False, 'ct mismatch (core not running on ext clock?)'


def main():
    combos = [(5e6, 40), (5e6, 20), (10e6, 20), (10e6, 4)]  # (crypto Hz, adc_mul)
    t = None
    scope = None
    try:
        t = cw.target(None, cw.targets.CW305, force=True,
                      bsfile=BITSTREAM, fpga_id='100t', platform='cw305')
        t.clkusbautooff = True; t.clksleeptime = 1
        t.pll.pll_enable_set(True)
        # Force crypto clock source = 20-pin external (register select, J16-independent)
        t.fpga_write(0x00, [0x05])
        print('[+] target up, REG_CLKSETTINGS=0x05 (20-pin external clock)')
        scope = cw.scope()
        print('[+] scope:', scope_model_name(scope))
        try: scope.glitch.enabled = False
        except Exception: pass
        scope.gain.db = 35
        scope.adc.offset = 0
        scope.trigger.triggers = 'tio4'
        rng = np.random.default_rng(2)
        for crypto_hz, adc_mul in combos:
            sample_rate = crypto_hz * adc_mul
            tag = 'ext-clk crypto=%.1f MHz adc_mul=%d -> %.0f MS/s (%d samples/cyc)' % (
                crypto_hz/1e6, adc_mul, sample_rate/1e6, adc_mul)
            print('\n=== %s ===' % tag, flush=True)
            try:
                scope.clock.clkgen_src = 'system'
                scope.clock.adc_mul = adc_mul
                scope.clock.clkgen_freq = crypto_hz
                scope.clock.reset_adc()
            except Exception as e:
                print('[!] clock config fail: %s' % e, flush=True)
                continue
            samples = 8000
            scope.adc.samples = samples
            ok, why = ct_sanity(t)
            print('[+] ct sanity:', why, flush=True)
            if not ok:
                continue
            # quick trace sanity
            n = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
            t.loadEncryptionKey(bytes(16)); t.loadInput(n)
            scope.arm(); t.go(); scope.capture()
            tr = scope.get_last_trace()
            if tr is None or tr.size != samples or tr.std() < 1e-3:
                print('[!] flat/bad trace std=%.4f' % (tr.std() if tr is not None else -1), flush=True)
                continue
            print('[+] trace sanity: %d samples std=%.4f' % (tr.size, tr.std()), flush=True)
            N = 500
            traces, keys = [], []
            i, fails = 0, 0
            t0 = time.time()
            while len(traces) < N and i < N * 4:
                i += 1
                k = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
                nn = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
                t.loadEncryptionKey(k); t.loadInput(nn)
                scope.arm(); t.go(); scope.capture()
                tr = scope.get_last_trace()
                if tr is None or tr.size != samples or not np.isfinite(tr).all() or tr.std() < 1e-3:
                    _drain(t); fails += 1; continue
                traces.append(tr.astype(np.float64))
                keys.append(np.frombuffer(k, dtype=np.uint8).copy())
            print('[+] %d traces in %.0fs (%d fails)' % (len(traces), time.time()-t0, fails), flush=True)
            if len(traces) < 100:
                continue
            m = measure_r(np.array(traces), np.array(keys))
            print('[+] byte-HW r: mean %.3f  max %.3f' % (m[0], m[1]), flush=True)
            print('[+] per-bit r: mean %.3f  max %.3f  bits>null(%.3f): %d/128' % (m[2], m[3], m[5], m[4]), flush=True)
            import h5py
            fn = 'Dataset/extclk_c%.1f_m%d.h5' % (crypto_hz/1e6, adc_mul)
            with h5py.File(fn, 'w') as f:
                f.create_dataset('traces', data=np.array(traces))
                f.create_dataset('keys', data=np.array(keys))
                f.attrs['crypto_hz'] = crypto_hz
                f.attrs['adc_mul'] = adc_mul
                f.attrs['sample_rate'] = sample_rate
            print('[+] SAVED %s' % fn, flush=True)
            break  # one working config is enough for the decision
    finally:
        if scope is not None:
            try: scope.dis()
            except Exception: pass
        if t is not None:
            try: t.dis()
            except Exception: pass


if __name__ == '__main__':
    main()
