#!/usr/bin/env python3
r"""underclock_m_test.py — does M-averaging converge at 200 MS/s + 1 MHz?

The 40 MS/s M-test failed: HW estimate saturated (M=32==M=2048).
Hypothesis: at 200 MS/s the noise is higher bandwidth (less correlated),
so M-averaging should converge (noise shrinks as 1/sqrt(M), signal stays).

Test: capture M=256 fixed-key same-nonce traces at 1 MHz / 200 MS/s,
measure HW estimate vs M. If the estimate CONVERGES to the true HW
(rather than saturating), the attack is alive.

Usage: python3 underclock_m_test.py
"""
import numpy as np, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))
from scope_config import configure_scope, connect_target
from collect_dataset import _drain
from scipy import signal as sg
from sklearn.linear_model import LinearRegression

BITSTREAM = 'vivado_ascon/ascon_cw305_top.bit'

def main():
    # Load the 1 MHz / 200 MS/s dataset for profiling templates
    import h5py
    fn = 'Dataset/underclock_1.0MHz.h5'
    if not os.path.exists(fn):
        print('[!] %s not found. Run underclock_sweep.py first.' % fn)
        return
    with h5py.File(fn, 'r') as f:
        X = f['traces'][:].astype(np.float64)
        keys = f['keys'][:]
    n = len(X); split = int(0.8 * n)
    print('[+] profiling: %d traces, %d samples' % (n, X.shape[1]))
    Xz = (X - X.mean(0)) / (X.std(0) + 1e-12)
    hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], float)

    # Fit OLS templates per byte (high-pass for noise reduction)
    b, a = sg.butter(4, 0.05, 'high')
    Xf = sg.filtfilt(b, a, Xz, axis=1)
    Xf = (Xf - Xf.mean(0)) / (Xf.std(0) + 1e-12)
    models = []
    for byte in range(16):
        z = (hw[:split, byte] - hw[:split, byte].mean()) / (hw[:split, byte].std() + 1e-12)
        r = z @ Xf[:split] / split
        pk = int(np.abs(r).argmax())
        lo = max(0, pk - 10)
        m = LinearRegression().fit(Xf[:split, lo:lo+21], hw[:split, byte])
        models.append((lo, m))
    # Also per-bit templates
    B = np.zeros((n, 128))
    for b in range(16):
        for j in range(8):
            B[:, b*8+j] = (keys[:, b] >> j) & 1
    bit_peaks = np.zeros(128, dtype=int)
    bit_signs = np.zeros(128)
    bit_deltas = np.zeros(128)
    bit_sigmas = np.zeros(128)
    for c in range(128):
        z = (B[:split, c] - B[:split, c].mean()) / (B[:split, c].std() + 1e-12)
        r = z @ Xf[:split] / split
        pk = int(np.abs(r).argmax())
        bit_peaks[c] = pk
        bit_signs[c] = np.sign(r[pk]) if r[pk] != 0 else 1
        bit = B[:split, c]
        bit_deltas[c] = Xf[:split][bit == 1, pk].mean() - Xf[:split][bit == 0, pk].mean()
        bit_sigmas[c] = (Xf[:split, pk] - bit * bit_deltas[c]).std() + 1e-12
    print('[+] templates ready: byte-HW OLS + per-bit, 200 MS/s, 1 MHz')

    # Connect board
    rng = np.random.default_rng(42)
    key = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
    nonce = os.urandom(16)
    hw_true = np.array([bin(k).count('1') for k in key])
    print('[*] key: %s  HW: %s' % (key.hex(), ' '.join(str(h) for h in hw_true)))
    t = connect_target(BITSTREAM, crypto_hz=1.0e6, program=True)
    t.loadEncryptionKey(key)
    scope = configure_scope(gain=25, samples=10000, offset=0,
                            sample_rate=200e6, crypto_hz=1.0e6)
    print('[+] scope: 200 MS/s, 1 MHz crypto, 10000 samples')

    # M-averaging test: same key+nonce, M captures
    t.loadInput(nonce)
    M = 512
    pool = []; i = 0; fails = 0
    t0 = time.time()
    while len(pool) < M and i < M * 4:
        i += 1
        scope.arm(); t.go(); scope.capture()
        tr = scope.get_last_trace()
        if tr is None or tr.size != 10000 or tr.std() < 1e-3:
            _drain(t); fails += 1; continue
        pool.append(tr.astype(np.float64))
    print('[+] %d captures in %.0fs (%d fails)' % (len(pool), time.time() - t0, fails))
    scope.dis()

    # Align to profiling mean (first 2000 samples of the 10000 -> crop to match)
    # The profiling data was 2000 samples at 200 MS/s / 10 MHz.
    # Here we have 10000 samples at 200 MS/s / 1 MHz.
    # The 1 MHz trace covers 50 cycles = 50 * 200 = 10000 samples.
    # The profiling was 2000 samples at 200 MS/s / 10 MHz = 10 cycles.
    # We need to use the SAME 10000-sample window for both.
    # Align: crop to first 2000 for compatibility with profiling templates.
    # But that wastes 80% of the data. Instead: re-fit templates on the
    # 1 MHz profiling set (which has 10000 samples).
    # For now: use full 10000-sample traces and re-fit on the fly.
    Xf_pool = sg.filtfilt(b, a, (pool - np.mean(pool)) / (np.std(pool) + 1e-12), axis=1)
    Xf_pool = (Xf_pool - Xf_pool.mean(0)) / (Xf_pool.std(0) + 1e-12)

    # Re-fit OLS on the 1 MHz profiling data (10000 samples)
    lo_all = 0; w = 21
    models_1m = []
    for byte in range(16):
        z = (hw[:split, byte] - hw[:split, byte].mean()) / (hw[:split, byte].std() + 1e-12)
        r = z @ Xf[:split] / split
        pk = int(np.abs(r).argmax())
        lo = max(0, pk - 10)
        m = LinearRegression().fit(Xf[:split, lo:lo+w], hw[:split, byte])
        models_1m.append((lo, m))

    # Per-bit templates on 1 MHz data
    bit_peaks_1m = np.zeros(128, dtype=int)
    bit_signs_1m = np.zeros(128)
    bit_deltas_1m = np.zeros(128)
    bit_sigmas_1m = np.zeros(128)
    for c in range(128):
        z = (B[:split, c] - B[:split, c].mean()) / (B[:split, c].std() + 1e-12)
        r = z @ Xf[:split] / split
        pk = int(np.abs(r).argmax())
        bit_peaks_1m[c] = pk
        bit_signs_1m[c] = np.sign(r[pk]) if r[pk] != 0 else 1
        bit = B[:split, c]
        bit_deltas_1m[c] = Xf[:split][bit == 1, pk].mean() - Xf[:split][bit == 0, pk].mean()
        bit_sigmas_1m[c] = (Xf[:split, pk] - bit * bit_deltas_1m[c]).std() + 1e-12

    # M-sweep: average M traces, predict HW and bits
    true_bits = np.zeros(128, dtype=np.uint8)
    for b in range(16):
        for j in range(8):
            true_bits[b*8+j] = (key[b] >> j) & 1

    print('\n=== M-SWEEP: HW estimate + per-bit accuracy vs M ===')
    for M in [32, 128, 256, 512]:
        if M > len(pool):
            break
        avg = Xf_pool[:M].mean(0)
        # HW
        est = np.zeros(16)
        for byte in range(16):
            lo, m = models_1m[byte]
            est[byte] = m.predict(avg[lo:lo+w][None])[0]
        hw_err = np.abs(est - hw_true)
        # Per-bit
        pred = np.zeros(128, dtype=np.uint8)
        for c in range(128):
            pk = bit_peaks_1m[c]
            diff = (avg[pk] - bit_deltas_1m[c] / 2) * bit_signs_1m[c]
            pred[c] = 1 if diff > 0 else 0
        bit_wrong = int((pred != true_bits).sum())
        # SNR: avg bit-delta / sigma at M
        snr = np.abs(bit_deltas_1m).mean() / (bit_sigmas_1m.mean() / np.sqrt(M) + 1e-12)
        print('M=%3d: HW +-1 %d/16 | bit wrong %d/128 (SNR %.1f) | est %s' % (
            M, int((hw_err <= 1).sum()), bit_wrong, snr,
            ' '.join('%.0f' % e for e in est)))
    print('\nTrue HW:', ' '.join(str(h) for h in hw_true))
    print('True bits: %s' % ''.join(str(b) for b in true_bits))

if __name__ == '__main__':
    main()
