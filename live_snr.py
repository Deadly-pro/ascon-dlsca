#!/usr/bin/env python3
r"""live_snr.py — watch a growing .h5 capture and print per-column SNR live.
Run in a second terminal while collect_dataset.py is running.

Usage:
    .venv/bin/python live_snr.py Dataset/vprobe_100.h5
    .venv/bin/python live_snr.py Dataset/vprobe_100.h5 --interval 20
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))

import numpy as np
import h5py

def snr_db(traces, labels):
    """Per-sample SNR: var(class_means) / mean(within_class_var), then max over samples."""
    classes = np.unique(labels)
    if len(classes) < 2:
        return -999.0
    grand = traces.mean(0)
    between = np.zeros(traces.shape[1])
    within  = np.zeros(traces.shape[1])
    for c in classes:
        m = traces[labels == c]
        if len(m) < 2:
            continue
        between += len(m) * (m.mean(0) - grand)**2
        within  += m.var(0) * len(m)
    between /= len(traces)
    within  /= len(traces)
    within = np.where(within < 1e-12, 1e-12, within)
    ratio = between / within          # per-sample
    peak = ratio.max()
    return 10 * np.log10(peak) if peak > 0 else -999.0

def load_partial(path):
    try:
        with h5py.File(path, 'r') as f:
            traces = f['traces'][:]
            keys   = f['keys'][:]
            nonces = f['nonces'][:]
        return traces, keys, nonces
    except Exception:
        return None, None, None

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('h5', help='path to growing .h5 file')
    ap.add_argument('--interval', type=int, default=30,
                    help='seconds between updates (default 30)')
    ap.add_argument('--cols', type=int, nargs='+',
                    default=[0, 1, 16, 32, 48, 63],
                    help='S-box columns to check (default sample of 6)')
    args = ap.parse_args()

    import labels as lab

    print(f'Watching {args.h5}  (Ctrl-C to stop)')
    print(f'Checking cols: {args.cols}')
    last_n = 0

    while True:
        traces, keys, nonces = load_partial(args.h5)
        if traces is None or len(traces) < 50:
            print(f'\r[waiting — {0 if traces is None else len(traces)} traces so far]',
                  end='', flush=True)
            time.sleep(args.interval)
            continue

        n = len(traces)
        if n == last_n:
            print(f'\r[{n} traces — no change]', end='', flush=True)
            time.sleep(args.interval)
            continue
        last_n = n

        # z-score per trace (matches preprocess pipeline)
        mu = traces.mean(1, keepdims=True)
        sd = traces.std(1, keepdims=True)
        sd[sd < 1e-8] = 1.0
        X = (traces - mu) / sd

        # compute S-box HW labels for the requested columns
        try:
            sb = lab.round1_sbox_hw(keys, nonces)   # (N, 64)
        except Exception as e:
            print(f'\n[!] label error: {e}')
            time.sleep(args.interval)
            continue

        print(f'\n[{n} traces @ {time.strftime("%H:%M:%S")}]')
        any_leaks = False
        for c in args.cols:
            y = sb[:, c].astype(int)
            s = snr_db(X, y)
            chance = 1/6 * 100
            # quick logistic proxy: class count imbalance
            uniq, cnt = np.unique(y, return_counts=True)
            floor = cnt.max() / n * 100
            marker = ''
            if s > -10:
                marker = '  <-- LEAKING'
                any_leaks = True
            elif s > -15:
                marker = '  <-- marginal'
            print(f'  col {c:2d}: SNR {s:+6.1f} dB   floor {floor:.1f}%{marker}')

        if any_leaks:
            print('  *** above-floor leakage detected — PA arm viable ***')
        else:
            print(f'  all at noise floor (need > -15 dB to be hopeful)')

        time.sleep(args.interval)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n[stopped]')
