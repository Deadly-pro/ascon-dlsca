#!/usr/bin/env python3
r"""underclock_sweep.py — sweep crypto clock at 200 MS/s, measure per-bit r at each.

Root hypothesis: at 10 MHz / 40 MS/s = 4 samples/cycle, individual bit
transitions are unresolvable. At 1 MHz / 200 MS/s = 200 samples/cycle,
each round spreads across 200 samples, making transitions resolvable.

SAKURA-G at 500 MS/s with 125 s/cycle got per-bit r=0.3-0.7.
We aim for 200 s/cycle at 1 MHz / 200 MS/s.

Usage: python3 underclock_sweep.py
"""
import numpy as np, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))
import chipwhisperer as cw
from scope_config import configure_scope, connect_target, scope_model_name
from collect_dataset import _drain

BITSTREAM = 'vivado_ascon/ascon_cw305_top.bit'

def capture(t, scope, n, samples, key_mode='random', key=None):
    rng = np.random.default_rng()
    traces, keys = [], []
    i, fails = 0, 0
    t0 = time.time()
    while len(traces) < n and i < n * 4:
        i += 1
        k = key if key else bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        t.loadEncryptionKey(k)
        t.loadInput(os.urandom(16))
        scope.arm(); t.go(); scope.capture()
        tr = scope.get_last_trace()
        if tr is None or tr.size != samples or not np.isfinite(tr).all() or tr.std() < 1e-3:
            _drain(t); fails += 1; continue
        traces.append(tr.astype(np.float64))
        keys.append(np.frombuffer(k, dtype=np.uint8).copy())
    return np.array(traces), np.array(keys), fails, time.time() - t0

def measure_r(traces, keys):
    n = len(traces); split = int(0.8 * n)
    Xz = (traces - traces.mean(0)) / (traces.std(0) + 1e-12)
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], float)
    B = np.zeros((n, 128))
    for b in range(16):
        for j in range(8): B[:, b*8+j] = (keys[:, b] >> j) & 1
    # per-byte HW held-out r
    hw_rs = []
    for b in range(16):
        z = (hw[:split,b]-hw[:split,b].mean())/(hw[:split,b].std()+1e-12)
        r = z @ Xz[:split] / split
        pk = int(np.abs(r).argmax())
        r_va = abs(np.corrcoef(Xz[split:,pk], hw[split:,b])[0,1])
        hw_rs.append(r_va)
    # per-bit held-out r
    bit_rs = []
    for c in range(128):
        z = (B[:split,c]-B[:split,c].mean())/(B[:split,c].std()+1e-12)
        r = z @ Xz[:split] / split
        pk = int(np.abs(r).argmax())
        r_va = abs(np.corrcoef(Xz[split:,pk], B[split:,c])[0,1])
        bit_rs.append(r_va)
    bit_rs = np.array(bit_rs)
    # null floor
    rng = np.random.default_rng(0)
    null_max = max(abs((rng.permutation(split) - split//2) / split * Xz[:split,0]).max() for _ in range(30))
    return np.mean(hw_rs), np.max(hw_rs), np.mean(bit_rs), np.max(bit_rs), (bit_rs > null_max).sum(), null_max

def main():
    t = connect_target(BITSTREAM, crypto_hz=2.5e6, program=True)
    clocks = [(10.0, 2000), (5.0, 4000), (2.5, 4000), (1.0, 10000), (0.5, 20000)]
    print('='*70)
    for clk, samples in clocks:
        tag = '%.1f MHz / 200 MS/s (%d samples, %d s/cycle)' % (clk, samples, int(200/clk))
        print('\n=== %s ===' % tag, flush=True)
        try:
            scope = configure_scope(gain=25, samples=samples, offset=0,
                                    sample_rate=200e6, crypto_hz=clk*1e6)
        except Exception as e:
            print('[!] scope config fail: %s' % e, flush=True); continue
        # sanity
        t.loadEncryptionKey(bytes(16)); t.loadInput(bytes(16))
        scope.arm(); t.go(); scope.capture()
        tr = scope.get_last_trace()
        if tr is None or tr.size != samples:
            print('[!] sanity fail (size %d != %d)' % (tr.size if tr is not None else 0, samples), flush=True)
            scope.dis(); continue
        print('[+] sanity: %d samples, std %.4f' % (tr.size, tr.std()), flush=True)
        n_cap = 400
        traces, keys, fails, dt = capture(t, scope, n_cap, samples)
        print('[+] %d traces in %.0fs (%d fails)' % (len(traces), dt, fails), flush=True)
        if len(traces) < 100:
            print('[!] too few traces', flush=True); scope.dis(); continue
        hw_mean, hw_max, bit_mean, bit_max, bits_above, null = measure_r(traces, keys)
        print('[+] byte-HW r: mean %.3f, max %.3f' % (hw_mean, hw_max), flush=True)
        print('[+] per-bit r: mean %.3f, max %.3f, bits>null %.3f: %d/128' % (
            bit_mean, bit_max, null, bits_above), flush=True)
        print('[+] samples/cycle: %d, samples/round: %d' % (int(200/clk), int(200/clk)), flush=True)
        # save if promising
        if bit_max > 0.2 or bits_above > 30:
            import h5py
            fn = 'Dataset/underclock_%.1fMHz.h5' % clk
            with h5py.File(fn, 'w') as f:
                f.create_dataset('traces', data=traces)
                f.create_dataset('keys', data=keys)
                f.attrs['crypto_mhz'] = clk
                f.attrs['sample_rate'] = 200e6
                f.attrs['samples'] = samples
                f.attrs['samples_per_cycle'] = int(200/clk)
            print('[+] SAVED %s (bit r > 0.2 — promising!)' % fn, flush=True)
        scope.dis()
    print('\n[DONE]')

if __name__ == '__main__':
    main()
