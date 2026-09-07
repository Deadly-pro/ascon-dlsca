#!/usr/bin/env python3
r"""gain_clock_sweep.py — quick on-board SNR probe.

For each (gain, crypto_clk) combo: fixed random key, one fixed nonce,
M averaged captures -> align each vs profiling ref -> average ->
correlation of the averaged trace against the two key-bit group means at
each of the 128 bit peaks (Pearson r per bit at its peak sample).
Reports per-combo: mean/median r over the 128 bits, r at the strong peaks.

Compare combos and pick the best for the oneshot attack.
Usage: python3 gain_clock_sweep.py --gains 15 20 25 30 --clks 2.5 5 --M 32
"""
import argparse
import os
import sys
import time
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

NPZ = os.path.join(ROOT, 'training/data/prof16sc_m32.npz')


def build_bit_templates():
    d = np.load(NPZ, allow_pickle=True)
    traces = d['traces'].astype(np.float64)
    keys = d['keys']
    split = int(0.8 * len(traces))
    mu, sd = traces.mean(0), traces.std(0) + 1e-12
    X = (traces - mu) / sd
    B = np.zeros((len(traces), 128))
    for b in range(16):
        for j in range(8):
            B[:, b * 8 + j] = (keys[:, b] >> j) & 1
    peaks = np.zeros(128, dtype=np.int64)
    for c in range(128):
        z = (B[:split, c] - B[:split, c].mean()) / (B[:split, c].std() + 1e-12)
        r = z @ X[:split] / split
        peaks[c] = int(np.abs(r).argmax())
    return d, X, B, peaks, split


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--gains', type=int, nargs='+', default=[15, 20, 25, 30, 35])
    ap.add_argument('--clks', type=float, nargs='+', default=[2.5])
    ap.add_argument('--M', type=int, default=32,
                    help='traces averaged per combo (fixed key+nonce)')
    ap.add_argument('--bitstream', default='vivado_ascon/ascon_cw305_top.bit')
    ap.add_argument('--key', default=None,
                    help='fixed probe key hex (default: random)')
    ap.add_argument('--samples', type=int, default=2000)
    args = ap.parse_args()

    rng = np.random.default_rng()
    probe_key = (bytes.fromhex(args.key) if args.key
                 else bytes(rng.integers(0, 256, 16, dtype=np.uint8)))
    print('[*] probe key: %s' % probe_key.hex())

    d, X, B, peaks, split = build_bit_templates()
    ref = d['ref'].astype(np.float64)
    from scipy import signal as sg
    from live_query import LiveQuery
    from collect_dataset import _drain

    # template mean-difference at each peak: bit=1 vs bit=0 group means
    # from PROFILING data (domain: profiling gain/clock)
    print('[*] %d bit peaks ready' % len(peaks))

    # sweep over (gain, clk)
    results = {}
    for clk in args.clks:
        for gain in args.gains:
            tag = 'g%d_c%.1f' % (gain, clk)
            print('\n=== %s: M=%d fixed key+nonce ===' % (tag, args.M))
            try:
                lq = LiveQuery(args.bitstream, probe_key, crypto_mhz=clk,
                               gain=gain, samples=args.samples, offset=0)
            except Exception as e:
                print('  init fail: %s' % e)
                continue
            nonce = os.urandom(16)
            pool = []
            i = 0
            t0 = time.time()
            while len(pool) < args.M and i < args.M * 4:
                i += 1
                lq.t.loadInput(nonce)
                lq.scope.arm()
                lq.t.go()
                lq.scope.capture()
                tr = lq.scope.get_last_trace()
                if tr is None or tr.size != args.samples or \
                   not np.isfinite(tr).all() or tr.std() < 1e-3:
                    _drain(lq.t)
                    continue
                pool.append(tr.astype(np.float64))
            if len(pool) < args.M // 2:
                print('  capture fail (%d/%d)' % (len(pool), args.M))
                lq.close()
                continue
            rate = len(pool) / (time.time() - t0)
            # align vs ref + average
            zs = []
            for tr in pool:
                c = sg.correlate(tr, ref, mode='same', method='fft')
                tr_a = np.roll(tr, -int(np.argmax(c) - len(tr) // 2))
                zs.append((tr_a - tr_a.mean()) / max(tr_a.std(), 1e-9))
            avg = np.mean(zs, axis=0)
            # per-bit Pearson r at peak: averaged trace vs bit template
            # r_c = (avg[pk_c] - <avg[pk]>) / ... using bit groups from the
            # probe key: template value = +1 if bit=1 else -1 -> r = corr
            # between avg[peaks] and (2*bit-1)
            bits = np.zeros(128)
            for b in range(16):
                for j in range(8):
                    bits[b * 8 + j] = (probe_key[b] >> j) & 1
            tmpl = 2 * bits - 1
            vals = avg[peaks]
            # pearson over the 128 peaks
            r = np.corrcoef(vals, tmpl)[0, 1]
            # also: correlation-profile energy vs profiling templates
            # (does the averaged trace reproduce the profiling r pattern?)
            results[tag] = (r, gain, clk, rate)
            print('  %d caps @%.1f/s -> avg |trace| std %.3f' %
                  (len(pool), rate, avg.std()))
            print('  PEARSON r(avg[peaks], key bits) = %+.4f' % r)
            lq.close()
            time.sleep(1.0)

    print('\n===== SUMMARY (higher |r| = better) =====')
    for tag, (r, g, c, rate) in sorted(results.items(), key=lambda kv: -abs(kv[1][0])):
        print('%-12s r=%+.4f gain=%d clk=%.1f (%.1f caps/s)' % (tag, r, g, c, rate))


if __name__ == '__main__':
    main()
