#!/usr/bin/env python3
"""Corrected: same preprocessing for profiling fit and live predict."""
import numpy as np, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))
from live_query import LiveQuery
from collect_dataset import _drain
from scipy import signal
from sklearn.linear_model import LinearRegression

# ---- fit on profiling (per-sample z, high-pass, per-sample z) ----
d = np.load('training/data/prof16sc_m32.npz', allow_pickle=True)
X = d['traces'].astype(np.float64); keys = d['keys']
n = len(X); split = int(0.8*n)
hw = np.array([[bin(int(b)).count('1') for b in row] for row in keys], float)

mean0, std0 = X[:split].mean(0), X[:split].std(0) + 1e-12
Xz = (X - mean0) / std0
b, a = signal.butter(4, 0.05, 'high')
Xf = signal.filtfilt(b, a, Xz, axis=1)
meanf, stdf = Xf[:split].mean(0), Xf[:split].std(0) + 1e-12
Xfn = (Xf - meanf) / stdf

models = []
for byte in range(16):
    z = (hw[:split,byte]-hw[:split,byte].mean())/(hw[:split,byte].std()+1e-12)
    r = z @ Xfn[:split] / split
    pk = int(np.abs(r).argmax())
    lo = max(0, pk-10)
    m = LinearRegression().fit(Xfn[:split, lo:lo+21], hw[:split, byte])
    models.append((lo, m))
    print('byte %2d: peak %d r=%.3f' % (byte, pk, np.abs(r).max()), flush=True)

# ---- live: fixed key+nonce, M captures, SAME preprocessing ----
rng = np.random.default_rng(42)
key = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
nonce = os.urandom(16)
print('key: %s' % key.hex(), flush=True)
print('nonce: %s' % nonce.hex(), flush=True)
hw_true = np.array([bin(k).count('1') for k in key])

lq = LiveQuery('vivado_ascon/ascon_cw305_top.bit', key, crypto_mhz=2.5, gain=25, samples=2000, offset=0)
lq.t.loadInput(nonce)
ref = d['ref'].astype(np.float64)

def align1(tr):
    c = signal.correlate(tr, ref, mode='same', method='fft')
    return np.roll(tr, -int(np.argmax(c) - len(tr)//2))

M = 256
pool = []; i = 0; fails = 0
print('capturing %d x same (key,nonce)...' % M, flush=True)
t0 = time.time()
while len(pool) < M and i < M*4:
    i += 1
    lq.scope.arm(); lq.t.go(); lq.scope.capture()
    tr = lq.scope.get_last_trace()
    if tr is None or tr.size != 2000 or tr.std() < 1e-3:
        _drain(lq.t); fails += 1; continue
    pool.append(tr.astype(np.float64))
print('%d traces in %.0fs (%d fails)' % (len(pool), time.time()-t0, fails), flush=True)
lq.close()

for M in [32, 128, 256]:
    # per-trace z-score FIRST (matches profiling preprocessing)
    zs = np.array([(align1(t)-t.mean())/max(t.std(),1e-9) for t in pool[:M]])
    avg = zs.mean(0)
    # THEN per-sample z using profiling stats (on already-per-trace-z'd data)
    avg_z = (avg - mean0) / std0
    avg_f = signal.filtfilt(b, a, avg_z, axis=0)
    avg_fn = (avg_f - meanf) / stdf
    est = np.zeros(16)
    for byte in range(16):
        lo, m = models[byte]
        est[byte] = m.predict(avg_fn[lo:lo+21][None])[0]
    err = np.abs(est - hw_true)
    print('M=%3d: +-1: %d/16, +-0.5: %d/16' % (M, int((err<=1).sum()), int((err<=0.5).sum())), flush=True)
print('True:', ' '.join(str(h) for h in hw_true), flush=True)
print('DONE', flush=True)
