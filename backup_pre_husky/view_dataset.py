#!/usr/bin/env python3
"""view_dataset.py — visualize a captured ASCON-128 trace dataset.

Generates a self-contained HTML report (<outdir>/report.html) containing:

  1. Dataset summary      (shape, dtype, range, attrs, key/nonce entropy)
  2. Trace overview       first 8 individual traces
  3. Mean +/- std         mean trace with envelope (the "average" crypto op)
  4. Overlay              first N traces overlaid (alignment + noise floor)
  5. Zoomed window        auto-locates the crypto operation and zooms in
  6. Spectrum             FFT of mean trace with 10 MHz clock harmonics
  7. Alignment            cross-correlation shift histogram vs mean
  8. Leakage scan (SNR)   per-sample SNR grouped by HW(key^nonce) per byte
  9. NICV                 normalized inter-class variance (model-free)
 10. Readback check       all ciphertexts re-verified against the oracle

Usage:
    python3 view_dataset.py Dataset/run1.h5 [--outdir Dataset/analysis]
"""
import argparse
import base64
import io
import os

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import signal

from ascon_ref import batch_fpga_expected, ascon_initialize, kadd_labels


def load(path):
    with h5py.File(path, 'r') as f:
        traces = f['traces'][:]
        keys = f['keys'][:]
        nonces = f['nonces'][:]
        cts = f['ciphertexts'][:]
        attrs = dict(f.attrs)
    return traces, keys, nonces, cts, attrs


def fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def hw_bits(x):
    return np.unpackbits(np.asarray(x, dtype=np.uint8)[:, None], axis=1,
                         bitorder='little').sum(axis=1)


def snr_grouped(traces, labels):
    """Per-sample SNR for 2+ groups of traces."""
    classes = np.unique(labels)
    means = np.array([traces[labels == c].mean(axis=0) for c in classes])
    vars_ = np.array([traces[labels == c].var(axis=0) for c in classes])
    gvar = means.var(axis=0)
    nvar = vars_.mean(axis=0)
    return gvar / np.maximum(nvar, 1e-12)


def nicv(traces, labels):
    """Normalized inter-class variance (model-free leakage)."""
    classes = np.unique(labels)
    means = np.array([traces[labels == c].mean(axis=0) for c in classes])
    gvar = means.var(axis=0)
    tvar = traces.var(axis=0)
    return gvar / np.maximum(tvar, 1e-12)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', default='Dataset/run1.h5', nargs='?')
    ap.add_argument('--outdir', default='Dataset/analysis')
    ap.add_argument('--overlay', type=int, default=30)
    ap.add_argument('--align-k', type=int, default=200)
    args = ap.parse_args()

    traces, keys, nonces, cts, attrs = load(args.h5)
    n, samples = traces.shape
    fs = attrs.get('fs_hz', 40e6)
    t_us = np.arange(samples) / fs * 1e6
    os.makedirs(args.outdir, exist_ok=True)

    print(f"[+] loaded {n} x {samples} traces  {traces.dtype}")
    print(f"[+] range [{traces.min():.4f}, {traces.max():.4f}]  mean {traces.mean():.5f}  std {traces.std():.5f}")
    print(f"[+] attrs: {attrs}")

    report = []
    imgs = []

    def add_panel(title, fig):
        imgs.append(f'<h2>{title}</h2><img src="data:image/png;base64,{fig_to_b64(fig)}"/>')

    # ---- 1. summary table ----
    rows = [
        ('traces', n), ('samples', samples), ('dtype', str(traces.dtype)),
        ('sample rate', f'{fs/1e6:.1f} MHz'), ('window', f'{samples/fs*1e6:.0f} us'),
        ('crypto clk', f'{attrs.get("crypto_clk_hz",10e6)/1e6:.0f} MHz'),
        ('gain', f'{attrs.get("gain_db","?")} dB'), ('verified', attrs.get('verified', '?')),
        ('key_mode', attrs.get('key_mode', '?')),
        ('trace min/max', f'{traces.min():.4f} / {traces.max():.4f}'),
        ('trace mean/std', f'{traces.mean():.5f} / {traces.std():.5f}'),
        ('unique keys', len(np.unique(keys, axis=0))),
        ('unique nonces', len(np.unique(nonces, axis=0))),
        ('unique cts', len(np.unique(cts, axis=0))),
    ]
    table = '<table border="1" cellpadding="4" style="border-collapse:collapse">' + \
            ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in rows) + '</table>'
    report.append(f'<h1>ASCON-128 CW305 Dataset Report</h1>{table}')

    # ---- 2. first 8 individual traces ----
    fig, axes = plt.subplots(4, 2, figsize=(14, 10), sharex=True)
    for i, ax in enumerate(axes.flat):
        if i >= min(8, n):
            ax.axis('off')
            continue
        ax.plot(t_us, traces[i], lw=0.5)
        ax.set_title(f'trace {i}  key={bytes(keys[i][:4]).hex()}..  nonce={bytes(nonces[i][:4]).hex()}..')
        ax.grid(alpha=0.3)
    fig.suptitle('First 8 traces (full window)')
    fig.tight_layout()
    add_panel('Individual traces', fig)

    # ---- 3. mean +/- std ----
    mean_t = traces.mean(axis=0)
    std_t = traces.std(axis=0)
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(t_us, traces[0], lw=0.4, alpha=0.5, label='trace 0')
    ax.fill_between(t_us, mean_t - std_t, mean_t + std_t, alpha=0.25, color='C1', label='mean +/- std')
    ax.plot(t_us, mean_t, lw=1, color='C1', label='mean')
    ax.set(xlabel='time (us)', ylabel='volts', title=f'Mean trace with envelope ({n} traces)')
    ax.legend(loc='upper right'); ax.grid(alpha=0.3)
    fig.tight_layout()
    add_panel('Mean +/- std', fig)

    # ---- 4. overlay ----
    fig, ax = plt.subplots(figsize=(14, 4))
    for i in range(min(args.overlay, n)):
        ax.plot(t_us, traces[i], lw=0.3, alpha=0.45)
    ax.set(xlabel='time (us)', ylabel='volts', title=f'Overlay of first {min(args.overlay, n)} traces')
    ax.grid(alpha=0.3)
    fig.tight_layout()
    add_panel('Overlay', fig)

    # ---- 5. zoomed window (first half, where crypto op lives) ----
    v = std_t ** 2
    half = samples // 2
    peak = int(np.argmax(v[:half]))
    lo = max(0, peak - 2000)
    hi = min(samples - 1, peak + 4000)
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.plot(t_us[lo:hi], mean_t[lo:hi], lw=0.8, label='mean')
    ax.fill_between(t_us[lo:hi], mean_t[lo:hi] - std_t[lo:hi], mean_t[lo:hi] + std_t[lo:hi],
                    alpha=0.25, label='std')
    ax.set(xlabel='time (us)', ylabel='volts',
           title=f'Zoomed around peak activity (samples {lo}..{hi}, t={t_us[lo]:.0f}..{t_us[hi]:.0f} us)')
    ax.legend(loc='upper right'); ax.grid(alpha=0.3)
    fig.tight_layout()
    add_panel('Zoomed crypto window', fig)
    print(f"[+] peak activity at sample {peak} (~{t_us[peak]:.1f} us)")

    # ---- 6. spectrum ----
    win = np.hanning(samples)
    X = np.abs(np.fft.rfft((mean_t - mean_t.mean()) * win))
    freqs = np.fft.rfftfreq(samples, 1 / fs)
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.semilogy(freqs[1:] / 1e6, X[1:], lw=0.6)
    for h in (10, 20, 30, 40):
        ax.axvline(h, color='r', ls='--', lw=0.8, alpha=0.6,
                   label=f'{h} MHz' if h == 10 else None)
    ax.set(xlabel='MHz', ylabel='|X|', xlim=(0, 40), title='Spectrum of mean trace')
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout()
    add_panel('Spectrum', fig)

    # ---- 7. alignment ----
    k = min(args.align_k, n)
    ref = mean_t
    shifts = []
    for i in range(k):
        c = signal.correlate(traces[i], ref, mode='same', method='fft')
        shifts.append(int(np.argmax(c) - samples // 2))
    shifts = np.array(shifts)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(shifts, bins=min(60, max(10, shifts.max() - shifts.min() + 1)))
    ax.set(xlabel='sample shift vs mean', ylabel='count',
           title=f'Alignment shift histogram ({k} traces): {shifts.min()}..{shifts.max()}')
    ax.grid(alpha=0.3)
    fig.tight_layout()
    add_panel('Alignment', fig)

    # ---- 8. SNR: post-init KADD state (real intermediate) ----
    try:
        lbl = kadd_labels([bytes(k) for k in keys], [bytes(n) for n in nonces])
        classes = np.unique(lbl)
        if len(classes) > 1:
            snr = snr_grouped(traces, lbl)
            fig, ax = plt.subplots(figsize=(14, 4))
            ax.plot(t_us, 10 * np.log10(snr), lw=0.6)
            ax.set(xlabel='time (us)', ylabel='SNR (dB)',
                   title=f'SNR: HW(ASCON post-init KADD state word 3)  — {len(classes)} classes')
            ax.grid(alpha=0.3)
            fig.tight_layout()
            add_panel('SNR (real intermediate)', fig)
        else:
            print('skipping SNR: single HW class (fixed key?)')
    except Exception as e:
        print(f'skipping SNR (KADD label): {e}')

    # ---- 8b. per-byte HW(key^nonce) - generic placeholder ----
    nb = min(16, keys.shape[1])
    fig, axes = plt.subplots(4, 4, figsize=(18, 12), sharex=True)
    for b in range(nb):
        ax = axes.flat[b]
        lbl = hw_bits(np.bitwise_xor(keys[:, b], nonces[:, b]))
        if len(np.unique(lbl)) > 1:
            snr = snr_grouped(traces, lbl)
            ax.plot(t_us, 10 * np.log10(snr), lw=0.5)
        ax.set_title(f'byte {b}')
        ax.grid(alpha=0.3)
    fig.suptitle('Per-byte SNR: HW(key[b] ^ nonce[b]) — generic placeholder, not an ASCON intermediate')
    fig.tight_layout()
    add_panel('Per-byte SNR (generic)', fig)

    # ---- 9. NICV (model-free) ----
    b = 0
    lbl = hw_bits(np.bitwise_xor(keys[:, b], nonces[:, b]))
    if len(np.unique(lbl)) > 1:
        nv = nicv(traces, lbl)
        fig, ax = plt.subplots(figsize=(14, 4))
        ax.plot(t_us, nv, lw=0.7)
        ax.set(xlabel='time (us)', ylabel='NICV', title=f'NICV by HW(key[0]^nonce[0]) — max {nv.max():.4f}')
        ax.grid(alpha=0.3)
        fig.tight_layout()
        add_panel('NICV', fig)

    # ---- 10. readback re-verification ----
    exp_list = batch_fpga_expected(list(zip(map(bytes, keys), map(bytes, nonces))))
    mismatch = sum(1 for e, c in zip(exp_list, map(bytes, cts)) if e != c)
    report.append(f'<h2>Readback re-verification</h2><p>{n - mismatch}/{n} ciphertexts match the oracle '
                  f'({"PASS" if mismatch == 0 else "FAIL: " + str(mismatch) + " mismatch"})</p>')
    print(f"[+] readback re-verify: {n-mismatch}/{n} match oracle")

    # ---- write HTML ----
    html = ('<!DOCTYPE html><html><head><meta charset="utf-8"><title>ASCON Dataset Report</title>'
            '<style>body{font-family:sans-serif;margin:2em}img{max-width:100%;height:auto;'
            'border:1px solid #ccc;margin:0.5em 0}td,th{padding:4px 10px}'
            'h1{color:#222}h2{border-bottom:1px solid #ccc;padding-bottom:4px;margin-top:2em}</style>'
            '</head><body>'
            + ''.join(report) + ''.join(imgs)
            + '</body></html>')
    out_html = os.path.join(args.outdir, 'report.html')
    with open(out_html, 'w') as f:
        f.write(html)
    print(f"[+] report: {os.path.abspath(out_html)}")


if __name__ == '__main__':
    main()
