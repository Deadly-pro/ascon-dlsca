#!/usr/bin/env python3
r"""eda.py — dataset overview and leakage analysis for the ASCON-128 CW305 captures.

Loads one captured h5 dataset and produces:

  1. Health report    shape, range, clipping/flat rate, oracle re-verification
  2. Trace stats      mean/std envelope, alignment (jitter) histogram
  3. Active region    where the crypto operation actually sits in the window
  4. Leakage scan     per-sample SNR on the real post-init KADD intermediate,
                      per-byte HW(key^nonce) SNR, and model-free NICV
  5. Spectrum         10 MHz crypto-clock harmonics

Text summary is printed to stdout; plots are saved to --out.

Usage:
    python3 training/eda.py Dataset/run1.h5
    python3 training/eda.py Dataset/run1.h5 --out training/plots/run1
    python3 training/eda.py Dataset/main.h5 --subsample 4000
"""
import argparse
import os
import sys

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ascon_ref import batch_fpga_expected, kadd_labels


def load(path, subsample=None):
    with h5py.File(path, 'r') as f:
        attrs = dict(f.attrs)
        traces = f['traces'][:]
        keys = f['keys'][:]
        nonces = f['nonces'][:]
        cts = f['ciphertexts'][:]
    if subsample and traces.shape[0] > subsample:
        idx = np.unique(np.linspace(0, traces.shape[0] - 1, subsample).astype(int))
        traces, keys, nonces, cts = traces[idx], keys[idx], nonces[idx], cts[idx]
    return traces, keys, nonces, cts, attrs


def snr_grouped(traces, labels):
    classes = np.unique(labels)
    means = np.array([traces[labels == c].mean(axis=0) for c in classes])
    vars_ = np.array([traces[labels == c].var(axis=0) for c in classes])
    gvar = means.var(axis=0)
    nvar = vars_.mean(axis=0)
    return gvar / np.maximum(nvar, 1e-12)


def nicv(traces, labels):
    classes = np.unique(labels)
    means = np.array([traces[labels == c].mean(axis=0) for c in classes])
    gvar = means.var(axis=0)
    tvar = traces.var(axis=0)
    return gvar / np.maximum(tvar, 1e-12)


def hw_bits(x):
    return np.unpackbits(np.asarray(x, dtype=np.uint8)[:, None], axis=1,
                         bitorder='little').sum(axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', help='captured dataset (Dataset/*.h5)')
    ap.add_argument('--out', default=None, help='output dir for plots')
    ap.add_argument('--align-k', type=int, default=200)
    ap.add_argument('--subsample', type=int, default=None,
                    help='max traces to analyze (keeps SNR fast on big files)')
    args = ap.parse_args()

    traces, keys, nonces, cts, attrs = load(args.h5, args.subsample)
    n, samples = traces.shape
    fs = attrs.get('fs_hz', 40e6)
    t_us = np.arange(samples) / fs * 1e6
    name = os.path.splitext(os.path.basename(args.h5))[0]
    outdir = args.out or os.path.join('training', 'plots', name)
    os.makedirs(outdir, exist_ok=True)

    def save(fig, title):
        path = os.path.join(outdir, title.replace(' ', '_') + '.png')
        fig.savefig(path, dpi=110, bbox_inches='tight')
        plt.close(fig)
        print(f'    plot: {path}')

    print(f'=== {name}.h5 ===')
    print(f'  traces {n} x {samples} ({traces.dtype}), {samples/fs*1e6:.0f} us window @ {fs/1e6:.1f} MHz')
    print(f'  attrs: gain={attrs.get("gain_db")} dB, adc_src={attrs.get("adc_src","clkgen_x4")}, '
          f'crypto_clk={attrs.get("crypto_clk_hz",10e6)/1e6:.0f} MHz, verified={attrs.get("verified")}')

    # ---- 1. health report ----
    peak = np.abs(traces).max()
    clip_frac = (np.abs(traces).max(axis=1) > 0.49).mean()
    flat_frac = (traces.std(axis=1) < 0.01).mean()
    exp = batch_fpga_expected(list(zip(map(bytes, keys), map(bytes, nonces))))
    n_ok = sum(1 for e, c in zip(exp, map(bytes, cts)) if e == c)
    print(f'  range [{traces.min():.4f}, {traces.max():.4f}]  peak {peak:.4f} V')
    print(f'  clip-rate {clip_frac*100:.1f}%   flat-rate {flat_frac*100:.1f}%   '
          f'oracle-verify {n_ok}/{n}')
    print(f'  unique keys {len(np.unique(keys,axis=0))}/{n}  '
          f'nonces {len(np.unique(nonces,axis=0))}/{n}  '
          f'cts {len(np.unique(cts,axis=0))}/{n}')

    # ---- 2. mean/std envelope + alignment ----
    mean_t = traces.mean(axis=0)
    std_t = traces.std(axis=0)
    ref = mean_t
    shifts = []
    for i in range(min(args.align_k, n)):
        c = signal.correlate(traces[i], ref, mode='same', method='fft')
        shifts.append(int(np.argmax(c) - samples // 2))
    shifts = np.array(shifts)
    print(f'  alignment jitter: {shifts.min()}..{shifts.max()} samples '
          f'({(shifts.max()-shifts.min())/fs*1e6:.2f} us spread)')

    fig, ax = plt.subplots(figsize=(13, 3.5))
    ax.plot(t_us, traces[0], lw=0.4, alpha=0.5, label='trace 0')
    ax.fill_between(t_us, mean_t - std_t, mean_t + std_t, alpha=0.25, color='C1')
    ax.plot(t_us, mean_t, lw=1, color='C1', label='mean')
    ax.set(xlabel='time (us)', ylabel='volts', title=f'{name}: mean +/- std envelope')
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); save(fig, '1_mean_envelope')

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.hist(shifts, bins=min(60, max(10, shifts.max() - shifts.min() + 1)))
    ax.set(xlabel='sample shift vs mean', ylabel='count', title='alignment histogram')
    ax.grid(alpha=0.3)
    fig.tight_layout(); save(fig, '2_alignment')

    # ---- 3. active region (variance envelope) ----
    v = std_t ** 2
    vmax = v.max()
    active = v > 0.25 * vmax
    runs, start = [], None
    for i, a in enumerate(active):
        if a and start is None:
            start = i
        elif not a and start is not None:
            runs.append((start, i)); start = None
    if start is not None:
        runs.append((start, samples))
    if runs:
        lo = runs[0][0]
        # restrict to earliest contiguous activity (the actual crypto op)
        lo = runs[0][0]; hi = lo
        for s, e in runs:
            if s <= hi + samples * 0.001:
                hi = max(hi, e)
            else:
                break
        print(f'  active region: samples {lo}..{hi}  (t = {t_us[lo]:.1f}..{t_us[min(hi,samples-1)]:.1f} us, '
              f'{(hi-lo)/fs*1e6:.1f} us wide)')
    else:
        lo, hi = 0, samples
        print('  no clear active region found')

    fig, ax = plt.subplots(figsize=(13, 3.5))
    ax.plot(t_us, v, lw=0.6)
    ax.axvspan(t_us[lo], t_us[min(hi, samples - 1)], color='r', alpha=0.15, label='active region')
    ax.set(xlabel='time (us)', ylabel='var', yscale='log',
           title=f'{name}: variance envelope (active region highlighted)')
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); save(fig, '3_active_region')

    # zoom into the active region
    pad = int((hi - lo) * 0.3) + 1
    lo_z = max(0, lo - pad); hi_z = min(samples, hi + pad)
    fig, ax = plt.subplots(figsize=(13, 3.5))
    ax.plot(t_us[lo_z:hi_z], mean_t[lo_z:hi_z], lw=0.9, label='mean')
    ax.fill_between(t_us[lo_z:hi_z], mean_t[lo_z:hi_z] - std_t[lo_z:hi_z],
                    mean_t[lo_z:hi_z] + std_t[lo_z:hi_z], alpha=0.25)
    ax.set(xlabel='time (us)', ylabel='volts', title=f'{name}: zoomed active region')
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); save(fig, '4_active_zoom')

    # ---- 4. leakage scan (real KADD intermediate) ----
    lbl = kadd_labels([bytes(k) for k in keys], [bytes(n) for n in nonces])
    classes = np.unique(lbl)
    if len(classes) > 1:
        snr = snr_grouped(traces, lbl)
        fig, ax = plt.subplots(figsize=(13, 3.5))
        ax.plot(t_us, 10 * np.log10(snr), lw=0.6)
        ax.set(xlabel='time (us)', ylabel='SNR (dB)', xlim=(0, t_us[-1]),
               title=f'{name}: SNR by HW(post-init KADD S[3])')
        ax.grid(alpha=0.3)
        fig.tight_layout(); save(fig, '5_snr_kadd')
        k = np.argmax(snr)
        print(f'  KADD-SNR peak {10*np.log10(snr[k]):.1f} dB at sample {k} '
              f'(t={t_us[k]:.1f} us, in-active={"y" if lo<=k<=hi else "n"})')

    # per-byte HW(key^nonce) SNR (generic scan)
    nb = min(16, keys.shape[1])
    max_snr_per_byte = []
    fig, axes = plt.subplots(4, 4, figsize=(18, 12), sharex=True)
    for b in range(nb):
        ax = axes.flat[b]
        lblb = hw_bits(np.bitwise_xor(keys[:, b], nonces[:, b]))
        if len(np.unique(lblb)) > 1:
            s = snr_grouped(traces, lblb)
            ax.plot(t_us, 10 * np.log10(s), lw=0.5)
            max_snr_per_byte.append(10 * np.log10(s.max()))
        ax.set_title(f'byte {b}'); ax.grid(alpha=0.3)
    fig.suptitle(f'{name}: per-byte SNR by HW(key[b] ^ nonce[b])')
    fig.tight_layout(); save(fig, '6_snr_perbyte')
    if max_snr_per_byte:
        print(f'  per-byte HW(key^nonce) SNR max: {max(max_snr_per_byte):.1f} dB')

    # ---- 4b. NICV (model-free) ----
    b = 0
    lbln = hw_bits(np.bitwise_xor(keys[:, b], nonces[:, b]))
    if len(np.unique(lbln)) > 1:
        nv = nicv(traces, lbln)
        fig, ax = plt.subplots(figsize=(13, 3.5))
        ax.plot(t_us, nv, lw=0.7)
        ax.set(xlabel='time (us)', ylabel='NICV',
               title=f'{name}: NICV by HW(key[0]^nonce[0])  max {nv.max():.4f}')
        ax.grid(alpha=0.3)
        fig.tight_layout(); save(fig, '7_nicv')
        print(f'  NICV peak {nv.max():.4f} at sample {np.argmax(nv)}')

    # ---- 5. spectrum ----
    win = np.hanning(samples)
    X = np.abs(np.fft.rfft((mean_t - mean_t.mean()) * win))
    freqs = np.fft.rfftfreq(samples, 1 / fs)
    fig, ax = plt.subplots(figsize=(13, 3.5))
    ax.semilogy(freqs[1:] / 1e6, X[1:], lw=0.6)
    for h in (10, 20, 30, 40):
        ax.axvline(h, color='r', ls='--', lw=0.8, alpha=0.6)
    ax.set(xlabel='MHz', ylabel='|X|', xlim=(0, 40), title=f'{name}: spectrum of mean trace')
    ax.grid(alpha=0.3)
    fig.tight_layout(); save(fig, '8_spectrum')

    print(f'  plots -> {outdir}/')


if __name__ == '__main__':
    main()
