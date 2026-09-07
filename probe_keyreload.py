#!/usr/bin/env python3
r"""probe_keyreload.py — does the key-load write per trace matter?

A/B capture, same fixed key, M traces each, predict 128 bits from the
aligned average:
  A: key written ONCE (LiveQuery init), per-trace only loadInput+go
  B: loadEncryptionKey + loadInput + go per trace (collect_dataset style)

If B recovers bits and A doesn't, the wrapper needs the key write to
re-enter key absorption, and every attack capture must reload the key.
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


def load_templates():
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
    signs = np.zeros(128)
    deltas = np.zeros(128)
    sigmas = np.zeros(128)
    for c in range(128):
        z = (B[:split, c] - B[:split, c].mean()) / (B[:split, c].std() + 1e-12)
        r = z @ X[:split] / split
        pk = int(np.abs(r).argmax())
        peaks[c] = pk
        signs[c] = np.sign(r[pk]) if r[pk] != 0 else 1.0
        bit = B[:split, c]
        deltas[c] = X[:split][bit == 1, pk].mean() - X[:split][bit == 0, pk].mean()
        sigmas[c] = (X[:split, pk] - bit * deltas[c]).std() + 1e-12
    return d, peaks, signs, deltas, sigmas


def predict(avg_z, peaks, signs, deltas, sigmas, M_eff, M_prof=32):
    pred = np.zeros(128, dtype=np.uint8)
    conf = np.zeros(128)
    scale = np.sqrt(M_prof / max(M_eff, 1))
    for c in range(128):
        diff = (avg_z[peaks[c]] - deltas[c] / 2.0) * signs[c]
        pred[c] = 1 if diff > 0 else 0
        conf[c] = abs(diff) / (sigmas[c] * scale + 1e-12)
    return pred, conf


def capture_arm(lq, key, M, reload_key, samples, ref):
    from scipy import signal as sg
    from collect_dataset import _drain
    pool = []
    i = 0
    while len(pool) < M and i < M * 4:
        i += 1
        if reload_key:
            lq.t.loadEncryptionKey(key)
        lq.t.loadInput(os.urandom(16))
        lq.scope.arm()
        lq.t.go()
        lq.scope.capture()
        tr = lq.scope.get_last_trace()
        if tr is None or tr.size != samples or \
           not np.isfinite(tr).all() or tr.std() < 1e-3:
            _drain(lq.t)
            continue
        pool.append(tr.astype(np.float64))
    zs = []
    for tr in pool:
        c = sg.correlate(tr, ref, mode='same', method='fft')
        a = np.roll(tr, -int(np.argmax(c) - len(tr) // 2))
        zs.append((a - a.mean()) / max(a.std(), 1e-9))
    return np.mean(zs, axis=0), len(pool)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--M', type=int, default=256)
    ap.add_argument('--gain', type=int, default=25)
    ap.add_argument('--crypto-mhz', type=float, default=2.5)
    ap.add_argument('--samples', type=int, default=2000)
    ap.add_argument('--bitstream', default='vivado_ascon/ascon_cw305_top.bit')
    args = ap.parse_args()

    rng = np.random.default_rng()
    key = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
    print('[*] probe key: %s' % key.hex())
    true_bits = np.zeros(128, dtype=np.uint8)
    for b in range(16):
        for j in range(8):
            true_bits[b * 8 + j] = (key[b] >> j) & 1

    d, peaks, signs, deltas, sigmas = load_templates()
    ref = d['ref'].astype(np.float64)
    from live_query import LiveQuery

    for tag, reload_key in [('A key-once ', False), ('B key-each', True)]:
        lq = LiveQuery(args.bitstream, key, crypto_mhz=args.crypto_mhz,
                       gain=args.gain, samples=args.samples, offset=0)
        t0 = time.time()
        avg, n = capture_arm(lq, key, args.M, reload_key, args.samples, ref)
        pred, conf = predict(avg, peaks, signs, deltas, sigmas, n)
        wrong = int((pred != true_bits).sum())
        print('[%s] n=%d (%.0fs): wrong bits %d/128, '
              'median conf of correct %+.2f, of wrong %+.2f' %
              (tag, n, time.time() - t0, wrong,
               np.median(conf[pred == true_bits]) if (pred == true_bits).any() else 0,
               np.median(conf[pred != true_bits]) if (pred != true_bits).any() else 0))
        lq.close()
        time.sleep(1.0)


if __name__ == '__main__':
    main()
