#!/usr/bin/env python3
"""Localize the key-dependent leak: UART/FIFO byte-serial shift-in vs
register-file write bus vs key register flip-flops.

Signatures:
 - UART byte-serial: each key byte b leaks at a DIFFERENT, time-staggered
   sample (byte 0 early, byte 15 later), spacing ~ bits/baud.
 - Register-file parallel write: all key bytes leak at ~the SAME sample
   (the write-strobe cycle), possibly a few word-grouped samples.
 - Trigger coverage: if the leak is BEFORE sample 0 of the trigger window
   it won't appear at all; if it dominates, the trigger window includes the
   load phase (bad for isolating crypto).
"""
import sys, numpy as np
sys.path.insert(0, 'training'); sys.path.insert(0, '.')

d = np.load('training/data/prof16sc_m32.npz', allow_pickle=True)
tr = d['traces'].astype(np.float64)
keys = d['keys']
N, T = tr.shape
print(f'{N} traces x {T} samples')

Xm = tr - tr.mean(0); Xs = tr.std(0); Xs[Xs < 1e-9] = 1
Xn = Xm / Xs

def corr_prof(y):
    y = y - y.mean(); sd = y.std()
    if sd == 0:
        return np.zeros(T)
    return (Xn.T @ (y / sd)) / (N - 1)

# per-KEY-BYTE Hamming weight leak: where does each of the 16 bytes peak?
print('\nper-key-byte HW leak (byte -> peak sample, |r|):')
peaks = []
for b in range(16):
    hw = np.array([bin(int(k[b])).count('1') for k in keys], dtype=float)
    r = corr_prof(hw)
    i = np.abs(r).argmax()
    peaks.append(i)
    print(f'  byte {b:2d}: sample {i:4d}  r={r[i]:+.3f}')

peaks = np.array(peaks)
print(f'\nbyte-peak spread: min={peaks.min()} max={peaks.max()} '
      f'range={peaks.max()-peaks.min()} std={peaks.std():.1f}')
if peaks.max() - peaks.min() > 100:
    print('  => TIME-STAGGERED across bytes -> UART/serial shift-in')
else:
    print('  => bytes cluster at one sample -> PARALLEL register write bus')

# per-NONCE-byte too (for comparison — nonce loads after key)
print('\nper-nonce-byte HW leak peak samples:')
nonces = d['nonces']
npk = []
for b in range(16):
    hw = np.array([bin(int(n[b])).count('1') for n in nonces], dtype=float)
    r = corr_prof(hw)
    npk.append(np.abs(r).argmax())
npk = np.array(npk)
print(f'  nonce-byte peaks: min={npk.min()} max={npk.max()}')

# energy structure: regular periodic spikes = clocked serial bus
eng = tr.std(0)
from scipy.signal import find_peaks
pk, _ = find_peaks(eng, height=0.25 * eng.max(), distance=8)
if len(pk) > 1:
    diffs = np.diff(pk)
    print(f'\nenergy spikes at {len(pk)} points, spacing median={np.median(diffs):.0f} '
          f'(regular spacing = clocked byte/word bus)')
    print(f'  first 12 spike samples: {pk[:12].tolist()}')

# is the key-leak region BEFORE or overlapping crypto?
print(f'\nkey-byte leak region {peaks.min()}-{peaks.max()}; '
      f'energy peak (likely crypto) at {eng.argmax()}')
