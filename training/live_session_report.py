#!/usr/bin/env python3
r"""live_session_report.py — HTML report for live_loop_transformer session.

Usage: python3 training/live_session_report.py Dataset/live_xfm_session_YYYYMMDD_HHMMSS.h5
Output: results/report.html

Processes the ep_XXX group format (no keys stored), producing trace-health
stats, mean/std envelope, alignment jitter, active-region, and spectrum.
"""
import argparse, base64, io, os, sys
import h5py, numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


def _ep_data(h):
    """Yield (ep_num, traces, nonces, cts) for each episode."""
    eps = sorted(h.keys())
    for k in eps:
        g = h[k]
        yield int(k[3:]), g['traces'][:], g['nonces'][:], g['cts'][:]


def _fig2b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=110, bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def build_report(h5_path):
    with h5py.File(h5_path, 'r') as h:
        attrs = dict(h.attrs)
        all_traces = []
        all_nonces = []
        all_cts = []
        ep_data = []
        for ep, tr, nn, ct in _ep_data(h):
            ep_data.append((ep, tr, nn, ct))
            all_traces.append(tr)
            all_nonces.append(nn)
            all_cts.append(ct)
    traces = np.concatenate(all_traces, axis=0)
    nonces = np.concatenate(all_nonces, axis=0)
    cts = np.concatenate(all_cts, axis=0)
    n, samples = traces.shape
    fs = 40e6
    t_us = np.arange(samples) / fs * 1e6
    name = os.path.splitext(os.path.basename(h5_path))[0]

    # ---- health ----
    peak = float(np.abs(traces).max())
    clip_frac = float((np.abs(traces).max(axis=1) > 0.49).mean())
    flat_frac = float((traces.std(axis=1) < 0.001).mean())
    stds = traces.std(axis=1)
    per_ep = []
    for ep, tr, nn, ct in ep_data:
        s = tr.std(axis=1)
        per_ep.append((ep, tr.shape[0], float(s.mean()), float(s.min()),
                       float(np.abs(tr).max()), float((s < 0.001).mean()),
                       float((np.abs(tr).max(axis=1) > 0.49).mean())))

    # ---- mean/std envelope ----
    mean_t = traces.mean(axis=0)
    std_t = traces.std(axis=0)
    # alignment jitter (first 200 traces)
    ref = mean_t.copy()
    k_align = min(200, n)
    shifts = []
    for i in range(k_align):
        c = signal.correlate(traces[i], ref, mode='same', method='fft')
        shifts.append(int(np.argmax(c) - samples // 2))
    shifts = np.array(shifts)
    sh_min, sh_max = int(shifts.min()), int(shifts.max())
    # active region (|mean| > 5×median absolute)
    med_abs = float(np.median(np.abs(mean_t)))
    th = 5 * med_abs
    active = np.where(np.abs(mean_t) > th)[0]
    if active.size:
        act_start, act_end = int(active[0]), int(active[-1]) + 1
    else:
        act_start, act_end = 0, 0

    # ---- spectrum ----
    mean_dc = mean_t - mean_t.mean()
    window = np.hanning(samples)
    X = np.abs(np.fft.rfft(mean_dc * window))
    freqs = np.fft.rfftfreq(samples, 1 / fs)

    # ---- build plots ----
    if not HAS_MPL:
        print('[!] matplotlib not available — skipping plots')
        plots = {}
    else:
        plt.rcParams.update({'font.size': 9, 'figure.dpi': 110})
        plots = {}

        # 1. mean/std envelope
        fig, ax = plt.subplots(figsize=(14, 3.5))
        ax.plot(t_us, mean_t, lw=0.6, label='mean')
        ax.fill_between(t_us, mean_t - std_t, mean_t + std_t, alpha=0.2, label='±1σ')
        ax.axvspan(act_start / fs * 1e6, act_end / fs * 1e6, color='g', alpha=0.1, label='active')
        ax.set(xlabel='time (µs)', ylabel='V', title=f'{name}: mean ±1σ envelope')
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        plots['envelope'] = _fig2b64(fig)

        # 2. alignment jitter
        fig, ax = plt.subplots(figsize=(10, 2.5))
        ax.hist(shifts, bins=min(50, sh_max - sh_min + 1), alpha=0.7)
        ax.set(xlabel='shift (samples)', ylabel='count', title=f'{name}: alignment jitter  (n={k_align})')
        ax.grid(alpha=0.3)
        plots['jitter'] = _fig2b64(fig)

        # 3. per-episode std
        fig, ax = plt.subplots(figsize=(10, 2.5))
        eps_arr = np.array([p[0] for p in per_ep])
        std_mean = np.array([p[2] for p in per_ep])
        std_min = np.array([p[3] for p in per_ep])
        ax.plot(eps_arr, std_mean, 'o-', lw=0.8, ms=3, label='mean std')
        ax.plot(eps_arr, std_min, 'x-', lw=0.5, ms=2, alpha=0.6, label='min std')
        ax.set(xlabel='episode', ylabel='std (V)', title=f'{name}: per-episode trace std')
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
        plots['per_ep_std'] = _fig2b64(fig)

        # 4. spectrum
        fig, ax = plt.subplots(figsize=(13, 3.5))
        ax.semilogy(freqs[1:] / 1e6, X[1:], lw=0.6)
        for h in (10, 20, 30, 40):
            ax.axvline(h, color='r', ls='--', lw=0.8, alpha=0.6)
        ax.set(xlabel='MHz', ylabel='|X|', xlim=(0, 40), title=f'{name}: spectrum of mean trace')
        ax.grid(alpha=0.3)
        plots['spectrum'] = _fig2b64(fig)

        # 5. per-sample std (noise floor characterization)
        fig, ax = plt.subplots(figsize=(14, 2.5))
        ax.plot(t_us, std_t, lw=0.6)
        ax.axvspan(act_start / fs * 1e6, act_end / fs * 1e6, color='g', alpha=0.1, label='active')
        ax.set(xlabel='time (µs)', ylabel='σ (V)', title=f'{name}: per-sample std')
        ax.grid(alpha=0.3)
        plots['per_sample_std'] = _fig2b64(fig)

    # ---- build HTML ----
    def td(v): return f'<td>{v}</td>'
    def tr(*cells): return '<tr>' + ''.join(td(c) for c in cells) + '</tr>'

    html = f'''<!DOCTYPE html><html><head><meta charset="utf-8">
<title>{name} — Live Session Report</title>
<style>
body{{font-family:sans-serif;margin:2em;background:#fafafa;color:#222}}
img{{max-width:100%;height:auto;border:1px solid #ccc;margin:0.5em 0;border-radius:4px}}
table{{border-collapse:collapse;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,0.1)}}
td,th{{padding:5px 12px;border:1px solid #ddd;text-align:left}}
th{{background:#f0f0f0;font-weight:600}}
h1{{color:#111;border-bottom:2px solid #4488ff;padding-bottom:8px}}
h2{{margin-top:2em;color:#333}}
.section{{background:#fff;padding:1em 1.5em;border-radius:6px;box-shadow:0 1px 3px rgba(0,0,0,0.1);margin:1em 0}}
.verdict{{padding:0.8em 1.2em;border-radius:6px;font-weight:600}}
.good{{background:#d4edda;color:#155724;border:1px solid #c3e6cb}}
.warn{{background:#fff3cd;color:#856404;border:1px solid #ffeeba}}
.bad{{background:#f8d7da;color:#721c24;border:1px solid #f5c6cb}}
</style></head><body>
<h1>{name} — Live Session Report</h1>
<p>Gain {attrs.get("gain")} dB · M={attrs.get("M")} · integrator={attrs.get("integrator")} · window {attrs.get("window")} · {attrs.get("created","")}</p>

<div class="section">
<h2>1. Trace Health</h2>
<table>
<tr><th>metric</th><th>value</th></tr>
{tr("traces", n)}
{tr("samples", samples)}
{tr("dtype", str(traces.dtype))}
{tr("window", f"{samples/fs*1e6:.0f} µs")}
{tr("sample rate", f"{fs/1e6:.1f} MHz")}
{tr("range", f"[{traces.min():.4f}, {traces.max():.4f}]")}
{tr("peak |x|", f"{peak:.4f} V")}
{tr("clip rate (>0.49V)", f"{clip_frac*100:.1f}%")}
{tr("flat rate (std<0.001V)", f"{flat_frac*100:.1f}%")}
{tr("mean std", f"{stds.mean():.5f} V")}
{tr("median std", f"{float(np.median(stds)):.5f} V")}
{tr("std p5", f"{float(np.percentile(stds,5)):.5f} V")}
{tr("std p95", f"{float(np.percentile(stds,95)):.5f} V")}
{tr("unique nonces", len(np.unique(nonces, axis=0)))}
{tr("unique cts", len(np.unique(cts, axis=0)))}
</table>
'''

    # per-episode table
    html += '''<h3>Per-Episode</h3>
<table><tr><th>ep</th><th>traces</th><th>std mean</th><th>std min</th><th>peak |x|</th><th>flat frac</th><th>clip frac</th></tr>'''
    for ep, tn, sm, smn, pk, ff, cf in per_ep:
        html += tr(f'ep_{ep:03d}', tn, f'{sm:.5f}', f'{smn:.5f}', f'{pk:.4f}',
                   f'{ff*100:.1f}%', f'{cf*100:.1f}%')
    html += '</table></div>\n'

    # verdict badge
    verdict_class = 'good'
    verdict_msg = 'Healthy — no clipping, no flat traces.'
    if clip_frac > 0.05:
        verdict_class = 'bad'
        verdict_msg = f'CLIP: {clip_frac*100:.1f}% traces clipped — reduce gain!'
    elif flat_frac > 0.05:
        verdict_class = 'warn'
        verdict_msg = f'FLAT: {flat_frac*100:.1f}% traces flat — check trigger.'
    html += f'<div class="verdict {verdict_class}">{verdict_msg}</div>\n'

    # signal region
    if active.size:
        pct = (act_end - act_start) / samples * 100
        pk_idx = int(np.argmax(np.abs(mean_t)))
        html += f'''<div class="section">
<h2>2. Signal Region</h2>
<table>
{tr("active region", f"samples {act_start}..{act_end} ({pct:.0f}% of window)")}
{tr("mean-trace peak", f"sample {pk_idx} ({pk_idx/fs*1e6:.2f} µs), |x|={abs(mean_t[pk_idx]):.4f} V")}
{tr("alignment jitter", f"{sh_min}..{sh_max} samples ({sh_min/fs*1e6:.2f}..{sh_max/fs*1e6:.2f} µs)")}
</table>
<p>Active region: samples where |mean trace| > 5× median absolute ({th:.5f} V).</p>
</div>'''
    else:
        html += '<div class="section warn"><h2>2. Signal Region</h2><p>No active region detected — signal may be absent or buried in noise.</p></div>'

    # spectral info
    base_freq = float(freqs[1:][X[1:].argmax()]) if X[1:].size > 0 else 0
    html += f'''<div class="section">
<h2>3. Spectrum</h2>
<table>
{tr("dominant frequency", f"{base_freq/1e6:.2f} MHz")}
{tr("crypto clock (expected)", "10 MHz")}
{tr("ADC rate", "40 MHz")}
</table>
</div>'''

    # plots
    if plots:
        html += '<div class="section"><h2>4. Plots</h2>\n'
        for pname, pb64 in plots.items():
            html += f'<img src="data:image/png;base64,{pb64}" alt="{pname}"><br>\n'
        html += '</div>\n'

    html += '</body></html>'

    # ---- text summary ----
    print(f'=== {name} Live Session Report ===')
    print(f'  {n} traces × {samples} samples, {fs/1e6:.0f} MHz')
    print(f'  gain={attrs.get("gain")} dB  M={attrs.get("M")}  window={attrs.get("window")}')
    print(f'  peak={peak:.4f}V  clip={clip_frac*100:.1f}%  flat={flat_frac*100:.1f}%')
    if active.size:
        print(f'  active region: {act_start}..{act_end} ({pct:.0f}%)  peak at sample {pk_idx}')
    print(f'  alignment jitter: {sh_min}..{sh_max} samples')
    print(f'  dominant freq: {base_freq/1e6:.2f} MHz')
    print(f'  plots: {list(plots.keys())}')
    print(f'  HTML report: {os.path.join(ROOT, "results", "report.html")}')

    return html


def main():
    ap = argparse.ArgumentParser(description='Live session report → results/report.html')
    ap.add_argument('h5', help='live session h5')
    args = ap.parse_args()

    out_path = os.path.join(ROOT, 'results', 'report.html')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    html = build_report(args.h5)
    with open(out_path, 'w') as f:
        f.write(html)
    print(f'[+] {out_path}  ({len(html)} bytes)')


if __name__ == '__main__':
    main()