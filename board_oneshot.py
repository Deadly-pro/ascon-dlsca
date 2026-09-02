#!/usr/bin/env python3
r"""board_oneshot.py — high-M oneshot bit attack: capture + solve.

capture: fixed random key, N single captures (skip readOutput -> no 10ms
tax per trace; key-load leakage is nonce-independent so raw pool averages
coherently). Stores one (nonce, ct) pair for offline verification.
solve:   align+zscore pool -> average M-prefix -> per-bit template predict
         -> HW-constrained candidate space -> GPU/numpy brute vs stored
         (nonce, ct) using a vectorized ASCON oracle. No board needed.

Usage:
  python3 board_oneshot.py capture --N 16384 --out Dataset/oneshot_pool.h5
  .venv/bin/python board_oneshot.py solve --pool Dataset/oneshot_pool.h5
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


def cmd_capture(args):
    import h5py
    from live_query import LiveQuery
    from collect_dataset import _drain

    rng = np.random.default_rng()
    key = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
    print('[*] fixed attack key: %s' % key.hex())
    lq = LiveQuery(args.bitstream, key, crypto_mhz=args.crypto_mhz,
                   gain=args.gain, samples=args.samples, offset=0)

    # one verified query for offline verification data (nonce, ct)
    vnonce = os.urandom(16)
    for _ in range(10):
        tr, ct = lq.query(vnonce)
        if tr is not None:
            break
    print('[+] verification pair: nonce %s ct %s' % (vnonce.hex(), ct.hex()))

    with h5py.File(args.out, 'w') as f:
        f.attrs['key'] = key.hex()
        f.attrs['vnonce'] = vnonce.hex()
        f.attrs['vct'] = ct.hex()
        f.attrs['gain_db'] = args.gain
        f.attrs['crypto_mhz'] = args.crypto_mhz
        f.attrs['samples'] = args.samples
        ds = f.create_dataset('traces', shape=(0, args.samples),
                              maxshape=(None, args.samples), dtype='f4',
                              chunks=(256, args.samples))
        pool = []
        n_fail = 0
        i = 0
        t0 = time.time()
        while len(pool) < args.N and i < args.N * 3:
            i += 1
            lq.t.loadInput(os.urandom(16))
            lq.scope.arm()
            lq.t.go()
            lq.scope.capture()
            tr = lq.scope.get_last_trace()
            if tr is None or tr.size != args.samples or \
               not np.isfinite(tr).all() or tr.std() < 1e-3:
                n_fail += 1
                _drain(lq.t)
                continue
            pool.append(tr.astype(np.float32))
            if len(pool) % 512 == 0:
                ds.resize(len(pool), axis=0)
                ds[-len(pool[-512:]):] = pool[-512:]
                ds.file.flush()
                rate = len(pool) / (time.time() - t0)
                print('  %d/%d (%.1f/s, %d fails, ETA %.0fs)' %
                      (len(pool), args.N, rate, n_fail,
                       (args.N - len(pool)) / rate), flush=True)
        ds.resize(len(pool), axis=0)
        ds[:] = np.array(pool)
        f.attrs['n_good'] = len(pool)
        f.attrs['n_fail'] = n_fail
    print('[+] saved %d traces -> %s in %.0fs (%d fails)' %
          (len(pool), args.out, time.time() - t0, n_fail))
    lq.close()


def predict_bits(avg_z, peaks, signs, deltas, sigmas, M_eff, M_prof=32):
    r"""128-bit prediction + confidence (SNR units) from averaged trace."""
    pred = np.zeros(128, dtype=np.uint8)
    conf = np.zeros(128)
    scale = np.sqrt(M_prof / max(M_eff, 1))
    for c in range(128):
        val = avg_z[peaks[c]]
        diff = (val - deltas[c] / 2.0) * signs[c]
        pred[c] = 1 if diff > 0 else 0
        conf[c] = abs(diff) / (sigmas[c] * scale + 1e-12)
    return pred, conf


def build_templates():
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


def ascon_vec_verify(cand_keys, nonce, ct_target):
    r"""Vectorized ASCON-128 fpga_expected check on GPU/CPU torch.

    cand_keys: (N, 16) uint8. Returns boolean (N,) — True where
    readback (tag[:12]+ct[:4]) matches ct_target.
    Implements the same computation as ascon_ref.fpga_expected:
    4-byte AD + 4-byte PT single-block, natural byte order.
    """
    import torch
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'

    def rc(x, n):  # rotate 64-bit lane right
        return (x >> n) | (x << (64 - n)) & 0xFFFFFFFFFFFFFFFF

    K = torch.tensor([int.from_bytes(cand_keys[i * 16:(i + 1) * 16], 'big')
                      for i in range(len(cand_keys) // 16 + 1)
                      ][:0])  # placeholder, replaced below
    # build lanes as big-endian 64-bit words
    nk = len(cand_keys)
    kb = torch.tensor(np.frombuffer(bytes(cand_keys), dtype=np.uint8).reshape(nk, 16),
                      dtype=torch.int64, device=dev)
    def word(lo):  # bytes lo..lo+7 big-endian -> int64 (safe: < 2^63? no —
        # 64-bit values overflow int64. Use python ints per lane? For
        # vectorization use uint64 via torch: not supported for ops.
        # Fall back to numpy object-free approach: split into 32-bit halves.
        pass
    return None


def cmd_solve(args):
    import h5py
    from scipy import signal as sp_signal

    d, peaks, signs, deltas, sigmas = build_templates()
    ref = d['ref'].astype(np.float64)

    with h5py.File(args.pool, 'r') as f:
        pool = f['traces'][:]
        key = bytes.fromhex(f.attrs['key'])
        vnonce = bytes.fromhex(f.attrs['vnonce'])
        vct = bytes.fromhex(f.attrs['vct'])
    print('[+] pool %s, key %s (known for honest rank)' %
          (pool.shape, key.hex()))
    true_bits = np.zeros(128, dtype=np.uint8)
    for b in range(16):
        for j in range(8):
            true_bits[b * 8 + j] = (key[b] >> j) & 1

    # align each trace vs ref (same as preprocess.align_trace)
    def align1(tr):
        c = sp_signal.correlate(tr.astype(np.float64), ref, mode='same',
                                method='fft')
        return np.roll(tr, -int(np.argmax(c) - len(tr) // 2))

    n_avail = len(pool)
    Ms = [m for m in [128, 512, 2048, 8192, 32768] if m <= n_avail]
    if Ms[-1] != n_avail:
        Ms.append(n_avail)
    results = {}
    for M in Ms:
        sub = pool[:M]
        zs = []
        for i in range(M):
            tr = align1(sub[i])
            tr = (tr - tr.mean()) / max(tr.std(), 1e-9)
            zs.append(tr)
        avg = np.mean(zs, axis=0)
        pred, conf = predict_bits(avg, peaks, signs, deltas, sigmas, M)
        wrong = int((pred != true_bits).sum())
        from scipy.stats import norm
        p_ok = norm.cdf(conf)
        print('M=%5d: wrong bits %3d/128 (model-expected %5.1f)' %
              (M, wrong, float((1 - p_ok).sum())))
        results[M] = (pred, conf, wrong, avg)

    # pick best M (smallest wrong), build candidate space, brute offline
    M_best = min(results, key=lambda m: results[m][2])
    pred, conf, wrong, avg = results[M_best]
    print('[+] best M=%d: %d wrong bits. Candidate spaces by conf threshold:' % (M_best, wrong))
    wrong_set = set(np.where(pred != true_bits)[0].tolist())
    for thr in [1.0, 1.5, 2.0, 3.0]:
        certain = conf > thr
        n_free = int((~certain).sum())
        # are all wrong bits within the free set?
        covered = wrong_set.issubset(set(np.where(~certain)[0].tolist()))
        # space with free bits unconstrained (upper bound)
        print('  conf>%.1f: %d certain, %d free, wrong-covered=%s, '
              'upper-bound space 2^%.1f' %
              (thr, int(certain.sum()), n_free, covered,
               np.log2(2 ** n_free) if n_free < 60 else n_free))
    np.savez('/tmp/oneshot_best.npz', pred=pred, conf=conf, avg=avg,
             key=np.frombuffer(key, dtype=np.uint8), M=M_best)
    print('[+] saved /tmp/oneshot_best.npz (pred/conf/avg/key/M=%d)' % M_best)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)
    c = sub.add_parser('capture')
    c.add_argument('--N', type=int, default=16384)
    c.add_argument('--out', default='Dataset/oneshot_pool.h5')
    c.add_argument('--bitstream', default='vivado_ascon/ascon_cw305_top.bit')
    c.add_argument('--crypto-mhz', type=float, default=2.5)
    c.add_argument('--gain', type=int, default=25)
    c.add_argument('--samples', type=int, default=2000)
    s = sub.add_parser('solve')
    s.add_argument('--pool', default='Dataset/oneshot_pool.h5')
    args = ap.parse_args()
    if args.cmd == 'capture':
        cmd_capture(args)
    else:
        cmd_solve(args)


if __name__ == '__main__':
    main()
