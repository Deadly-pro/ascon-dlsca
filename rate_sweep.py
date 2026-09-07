#!/usr/bin/env python3
r"""rate_sweep.py — capture random-key traces at multiple sample rates, measure per-bit and per-byte HW leakage, compare 40/100/200 MS/s."""
import numpy as np, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))
import chipwhisperer as cw
from scope_config import configure_scope, connect_target, scope_model_name
from collect_dataset import _drain
from scipy import signal as sg

BITSTREAM = 'vivado_ascon/ascon_cw305_top.bit'
GAIN = 25
CRYPTO = 2.5e6

def capture_with_keys(t, scope, n, samples, key=None):
    r"""Capture n traces; if key given, use it fixed (reload each trace);
    otherwise random key per trace. Returns (traces, keys) arrays."""
    rng = np.random.default_rng()
    traces, keys = [], []
    i, fails = 0, 0
    t0 = time.time()
    while len(traces) < n and i < n * 4:
        i += 1
        k = key if key else bytes(rng.integers(0, 256, 16, dtype=np.uint8))
        t.loadEncryptionKey(k)
        t.loadInput(os.urandom(16))
        scope.arm()
        t.go()
        scope.capture()
        tr = scope.get_last_trace()
        if tr is None or tr.size != samples or not np.isfinite(tr).all() or tr.std() < 1e-3:
            _drain(t); fails += 1; continue
        traces.append(tr.astype(np.float64))
        keys.append(np.frombuffer(k, dtype=np.uint8).copy())
    return np.array(traces), np.array(keys), fails, time.time() - t0

def measure_leakage(traces, keys, label):
    n = len(traces); split = int(0.8 * n)
    if split < 32:
        print('  %s: too few (%d)' % (label, n)); return
    mu, sd = traces[:split].mean(0), traces[:split].std(0) + 1e-12
    X = (traces - mu) / sd
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], float)
    # byte-HW Pearson r (train-fit, held-out evaluate)
    tr_r, va_r = [], []
    for b in range(16):
        z = (hw[:split, b] - hw[:split, b].mean()) / (hw[:split, b].std() + 1e-12)
        r_tr = z @ X[:split] / split
        zva = (hw[split:, b] - hw[split:, b].mean()) / (hw[split:, b].std() + 1e-12)
        r_va = zva @ X[split:] / (n - split)
        tr_r.append(np.abs(r_tr).max())
        va_r.append(np.abs(r_va[np.abs(r_tr).argmax()]))
    tr_r = np.array(tr_r); va_r = np.array(va_r)
    print('  %s: byte-HW r: train mean %.3f max %.3f | held-out %.3f (floor ~%.3f)' % (
        label, tr_r.mean(), tr_r.max(), va_r.mean(), 2/np.sqrt(n-split)))
    # per-bit
    B = np.zeros((n, 128))
    for b in range(16):
        for j in range(8):
            B[:, b*8+j] = (keys[:, b] >> j) & 1
    bit_r = np.zeros(128)
    for c in range(128):
        z = (B[:split, c] - B[:split, c].mean()) / (B[:split, c].std() + 1e-12)
        r = z @ X[:split] / split
        bit_r[c] = np.abs(r).max()
    # permutation null
    rng = np.random.default_rng(0)
    fls = []
    for _ in range(15):
        p = rng.permutation(split)
        zb = (B[:split, 0][p] - B[:split, 0].mean()) / (B[:split, 0].std() + 1e-12)
        fls.append(np.abs(zb @ X[:split] / split).max())
    null = max(fls)
    print('  %s: per-bit r: mean %.3f max %.3f | null max %.3f | bits>null: %d/128' % (
        label, bit_r.mean(), bit_r.max(), null, int((bit_r > null).sum())))
    return tr_r, va_r, bit_r

def main():
    rng = np.random.default_rng(42)
    key = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
    print('[*] HW probe key: %s' % key.hex())

    t = connect_target(BITSTREAM, crypto_hz=CRYPTO, program=True)
    t.loadEncryptionKey(key)

    for rate_mhz in [40, 100, 200]:
        print('\n' + '='*60)
        print('=== %d MS/s ===' % rate_mhz)
        try:
            scope = configure_scope(gain=GAIN, samples=2000, offset=0,
                                    sample_rate=rate_mhz*1e6, crypto_hz=CRYPTO)
        except Exception as e:
            print('[!] config fail: %s' % e); continue
        # sanity
        scope.arm(); t.go(); scope.capture()
        tr = scope.get_last_trace()
        if tr is None or tr.size != 2000:
            print('[!] sanity fail'); scope.dis(); continue
        print('[+] sanity: std %.4f range [%.3f, %.3f]' % (tr.std(), tr.min(), tr.max()))

        # random-key traces for bit templates (need HW variance)
        n_rand = 400
        print('[+] capturing %d random-key traces...' % n_rand)
        tr_rand, k_rand, fails, dt = capture_with_keys(t, scope, n_rand, 2000, key=None)
        print('[+] %d traces in %.0fs (%d fails)' % (len(tr_rand), dt, fails))
        measure_leakage(tr_rand, k_rand, 'random-key')

        # fixed-key traces for M-averaging test (byte-HW per-M check)
        n_fixed = 256
        print('[+] capturing %d fixed-key traces (key reload each)...' % n_fixed)
        tr_fix, _, fails2, dt2 = capture_with_keys(t, scope, n_fixed, 2000, key=key)
        print('[+] %d traces in %.0fs (%d fails)' % (len(tr_fix), dt2, fails2))
        # HW estimate vs M: does the ridge estimate converge?
        hw_true = np.array([bin(k).count('1') for k in key])
        from sklearn.linear_model import Ridge
        # fit HW ridge on random-key data
        split_r = int(0.8 * len(tr_rand))
        hw_rand = np.array([[bin(int(b)).count('1') for b in row] for row in k_rand], float)
        models = []
        for b in range(16):
            # find peak
            Xz = (tr_rand[:split_r] - tr_rand[:split_r].mean(0)) / (tr_rand[:split_r].std(0)+1e-12)
            z = (hw_rand[:split_r, b] - hw_rand[:split_r, b].mean()) / (hw_rand[:split_r, b].std()+1e-12)
            r = z @ Xz / split_r
            pk = int(np.abs(r).argmax())
            lo = max(0, pk - 10)
            Xw = tr_rand[:split_r, lo:lo+21].astype(np.float64)
            mu, sd = Xw.mean(0), Xw.std(0) + 1e-12
            m = Ridge(alpha=3.0).fit((Xw - mu) / sd, hw_rand[:split_r, b])
            models.append((lo, mu, sd, m))
        # apply to fixed-key M-prefix averages
        for M in [32, 128, 256]:
            if M > len(tr_fix): continue
            avg = tr_fix[:M].mean(0)
            est = np.zeros(16)
            for b in range(16):
                lo, mu, sd, m = models[b]
                w = (avg[lo:lo+21] - mu) / sd
                est[b] = m.predict(w[None])[0]
            err = np.abs(est - hw_true)
            print('  M=%3d fixed-key HW: est %s | +-1: %d/16, +-0.5: %d/16' % (
                M, ' '.join('%.1f' % e for e in est), int((err<=1).sum()), int((err<=0.5).sum())))
        scope.dis()

    print('\n[DONE]')

if __name__ == '__main__':
    main()
