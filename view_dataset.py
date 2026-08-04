#!/usr/bin/env python3
"""view_dataset.py — exploratory analysis of a captured ASCON trace dataset.

Prints a summary and writes plots to <outdir>:
    trace0.png     first trace + mean trace with +/- std envelope
    overlay.png    first N traces overlaid (gross alignment + noise floor)
    spectrum.png   log power spectrum of the mean trace with clock harmonics
    snr.png        per-sample SNR grouped by HW(key_byte ^ nonce_byte) — a
                   first-pass leakage scan (where in time the data leaks)
    alignment.png  cross-correlation shift histogram (first K traces vs mean)

Usage:
    python3 view_dataset.py Dataset/ascon_dataset.h5 [--outdir Dataset/analysis]
"""
import argparse
import os

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal


def load(path):
    with h5py.File(path, 'r') as f:
        traces = f['traces'][:]
        keys = f['keys'][:]
        nonces = f['nonces'][:]
        cts = f['ciphertexts'][:]
        attrs = dict(f.attrs)
    return traces, keys, nonces, cts, attrs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', default='Dataset/ascon_dataset.h5', nargs='?')
    ap.add_argument('--outdir', default='Dataset/analysis')
    ap.add_argument('--overlay', type=int, default=20)
    ap.add_argument('--align-k', type=int, default=50)
    ap.add_argument('--snr-byte', type=int, default=0,
                    help='key/nonce byte index for the SNR scan')
    args = ap.parse_args()

    traces, keys, nonces, cts, attrs = load(args.h5)
    n, samples = traces.shape
    fs = attrs.get('fs_hz', 40e6)

    print(f"traces       : {n} x {samples}  {traces.dtype}")
    print(f"attrs        : {attrs}")
    print(f"trace range  : [{traces.min():.4f}, {traces.max():.4f}]")
    print(f"mean/std     : {traces.mean():.5f} / {traces.std():.5f}")
    kk, nn = keys[:, 0].astype(np.uint32), nonces[:, 0].astype(np.uint32)
    print(f"key byte0 uniq: {len(np.unique(kk))}/{n}   nonce byte0 uniq: {len(np.unique(nn))}/{n}")

    os.makedirs(args.outdir, exist_ok=True)

    t = np.arange(samples) / fs * 1e6  # microseconds

    # 1. first trace + mean +/- std
    mean_t = traces.mean(axis=0)
    std_t = traces.std(axis=0)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(t, traces[0], lw=0.5, alpha=0.7, label='trace 0')
    ax.fill_between(t, mean_t - std_t, mean_t + std_t, alpha=0.25, color='C1', label='mean +/- std')
    ax.plot(t, mean_t, lw=1, color='C1', label='mean')
    ax.set(xlabel='time (us)', ylabel='volts', title=f'Trace 0 vs mean ({n} traces)')
    ax.legend(loc='upper right')
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, 'trace0.png')); plt.close(fig)

    # 2. overlay
    fig, ax = plt.subplots(figsize=(12, 4))
    for i in range(min(args.overlay, n)):
        ax.plot(t, traces[i], lw=0.3, alpha=0.5)
    ax.set(xlabel='time (us)', ylabel='volts', title=f'First {min(args.overlay, n)} traces')
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, 'overlay.png')); plt.close(fig)

    # 3. spectrum with clock harmonics
    win = np.hanning(samples)
    X = np.abs(np.fft.rfft((mean_t - mean_t.mean()) * win))
    freqs = np.fft.rfftfreq(samples, 1 / fs)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.semilogy(freqs[1:] / 1e6, X[1:], lw=0.5)
    for h in (10, 20, 30, 40):
        ax.axvline(h, color='r', ls='--', lw=0.8, alpha=0.6, label=f'{h} MHz' if h == 10 else None)
    ax.set(xlabel='MHz', ylabel='|X|', xlim=(0, 40), title='Spectrum of mean trace (crypto clk 10 MHz, ADC 40 MHz)')
    ax.legend()
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, 'spectrum.png')); plt.close(fig)

    # 4. SNR grouped by HW(key_byte ^ nonce_byte)
    b = args.snr_byte
    hw = (np.bitwise_xor(keys[:, b].astype(np.uint32), nonces[:, b].astype(np.uint32))
          .astype(np.uint8))
    hw = np.unpackbits(hw[:, None], axis=1, bitorder='little').sum(axis=1)
    classes = np.unique(hw)
    if len(classes) > 1:
        means = np.array([traces[hw == c].mean(axis=0) for c in classes])
        gvar = means.var(axis=0)
        nvar = np.array([traces[hw == c].var(axis=0) for c in classes]).mean(axis=0)
        snr = gvar / np.maximum(nvar, 1e-12)
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(t, 10 * np.log10(snr), lw=0.6)
        ax.set(xlabel='time (us)', ylabel='SNR (dB)',
               title=f'SNR grouped by HW(key[{b}] ^ nonce[{b}])  (classes: {classes.tolist()})')
        fig.tight_layout(); fig.savefig(os.path.join(args.outdir, 'snr.png')); plt.close(fig)
    else:
        print('skipping snr.png: single HW class')

    # 5. alignment: cross-correlation shift of first K traces vs mean
    k = min(args.align_k, n)
    ref = traces.mean(axis=0)
    shifts = []
    for i in range(k):
        c = signal.correlate(traces[i], ref, mode='same', method='fft')
        shifts.append(np.argmax(c) - samples // 2)
    shifts = np.array(shifts)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(shifts, bins=min(40, max(5, shifts.max() - shifts.min() + 1)))
    ax.set(xlabel='sample shift vs mean', ylabel='count',
           title=f'Cross-correlation shift ({k} traces): {shifts.min()}..{shifts.max()}')
    fig.tight_layout(); fig.savefig(os.path.join(args.outdir, 'alignment.png')); plt.close(fig)

    print(f"[+] plots written to {os.path.abspath(args.outdir)}/")


if __name__ == '__main__':
    main()
