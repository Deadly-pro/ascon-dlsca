#!/usr/bin/env python3
r"""vcc_sweep.py — VCCINT voltage sweep: is the lack of key-bit leakage a rail
effect? Sets the CW305 core voltage via code (0.75-1.05 V, safe range), gates
on the 5-vector KAT at every step, captures 400 traces at the proven-best
resolution (2.5 MHz crypto, 16 samples/cycle, extclk), and runs the leakage
battery per voltage: popcount correlation peak, honest S-box recovery, KADD.

Aborts and restores 1.0 V the moment a KAT vector fails (config corruption).
"""
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import h5py
import chipwhisperer as cw

from ascon_ref import fpga_expected, batch_fpga_expected
from sanity_check import VECTORS
from collect_dataset import _drain
from scope_config import connect_target, configure_scope
import labels as lab
from preprocess import align_trace
from lda_attack import fit_template, score_traces

BITSTREAM = os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit')
VOLTS = [1.05, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75]
GAIN = 25
SAMPLES = 1600
N = 400          # 300 fit + 100 held-out
CRYPTO_MHZ = 2.5


def kat5(t):
    for (k_hex, n_hex, *_rest) in VECTORS:
        key = bytes.fromhex(k_hex)
        nonce = bytes.fromhex(n_hex)
        t.loadEncryptionKey(key)
        t.loadInput(nonce)
        t.go()
        got = bytes(t.readOutput())
        if got != fpga_expected(key, nonce):
            return False
    return True


def battery(tr, kk, nn):
    """Returns (popcount_max|r|, peak_sample, recovery[3], kadd_max|r|)."""
    kk = np.frombuffer(b''.join(kk), np.uint8).reshape(-1, 16)
    nn = np.frombuffer(b''.join(nn), np.uint8).reshape(-1, 16)
    al = np.stack([align_trace(t, tr[:300].mean(0)) for t in tr[:300]])
    khw = kk[:300].astype(np.int32).sum(1)
    c = np.array([np.corrcoef(al[:, t], khw)[0, 1]
                  for t in range(tr.shape[1])])
    peak = int(np.abs(c).argmax())
    nf = 300
    bits = np.unpackbits(np.frombuffer(kk[nf].tobytes(), np.uint8),
                         bitorder='little')
    truth = (bits[:64].astype(int) << 1) | bits[64:].astype(int)
    rec = []
    for (w0, w) in [(0, 60), (peak, 120), (0, tr.shape[1])]:
        if w0 + w > tr.shape[1]:
            rec.append(-1)
            continue
        win = slice(w0, w0 + w)
        m = fit_template(tr, kk, nn, nf, win)
        ll = score_traces(tr[nf:nf + 100], nn[nf:nf + 100], m, win)
        rec.append(int((ll.sum(0).argmax(1) == truth).sum()))
    al3 = np.stack([align_trace(t, tr[:300].mean(0)) for t in tr[:300]])
    labl = np.asarray(lab.kadd_words_hw(kk[:300], nn[:300]), dtype=np.float64)
    rs = np.array([[np.corrcoef(al3[:, t], labl[:, j])[0, 1]
                    for j in range(labl.shape[1])]
                   for t in range(tr.shape[1])])
    return float(np.abs(c).max()), peak, rec, float(np.abs(rs).max())


def capture(t, scope, n, samples):
    """Mirror collect_dataset: arm/go, judge by content, retry with drain.

    Returns stored traces/keys/nonces + flat/clip counters.
    """
    traces, keys, nonces = [], [], []
    flats = clips = 0
    plan = [(os.urandom(16), os.urandom(16)) for _ in range(n)]
    exp = batch_fpga_expected(plan)
    for i, (key, nonce) in enumerate(plan):
        t.loadEncryptionKey(key)
        t.loadInput(nonce)
        attempt = 0
        while True:
            attempt += 1
            scope.arm()
            t.go()
            scope.capture()
            trace = scope.get_last_trace()
            if trace is None or trace.size < 64:
                if attempt >= 6:
                    flats += 1
                    break
                _drain(t)
                continue
            if trace.std() < 0.001:
                if attempt >= 6:
                    flats += 1
                    break
                _drain(t)
                continue
            if bytes(t.readOutput()) != exp[i]:
                break                      # verify fail: skip pair
            if float(np.abs(trace).max()) > 0.49:
                clips += 1
                if attempt >= 6:
                    break
                _drain(t)
                continue
            traces.append(trace)
            keys.append(key)
            nonces.append(nonce)
            break
        if i % 100 == 0:
            print(f'      {i}/{n} (stored {len(traces)}, flat {flats}, clip {clips})')
    return np.array(traces, dtype=np.float32), keys, nonces, flats, clips


def main():
    print('[+] programming bitstream at 1.0 V ...')
    t = connect_target(BITSTREAM, crypto_hz=10e6, program=True)
    target = t._t
    print('[+] KAT @1.0 V:', 'PASS' if kat5(t) else 'FAIL')
    scope = configure_scope(gain=GAIN, samples=SAMPLES, offset=700,
                            sample_rate=40e6, extclk=True,
                            crypto_hz=CRYPTO_MHZ * 1e6)
    print(f'[+] gain {GAIN} dB, {SAMPLES} samples, {CRYPTO_MHZ} MHz extclk')

    try:
        for v in VOLTS:
            target.vccint_set(v)
            got = target.vccint_get()
            ok = kat5(t)
            print(f'--- VCCINT {v:.2f} V (readback {got:.2f}) KAT '
                  f'{"PASS" if ok else "FAIL"} ---')
            if not ok:
                print(f'[!] KAT failed at {v:.2f} V — config corrupted, '
                      f'stopping sweep, restoring 1.0 V')
                break
            t0 = time.time()
            h5name = os.path.join(ROOT, 'Dataset',
                                  f'vcc{v:.2f}.h5'.replace('.', 'p'))
            if os.path.exists(h5name):
                with h5py.File(h5name, 'r') as f:
                    tr = f['traces'][:].astype(np.float64)
                    kk = f['keys'][:]
                    nn = f['nonces'][:]
                pmax, peak, rec, kmax = battery(tr, kk, nn)
                print(f'  [cached] {len(tr)} traces  popcount |r|={pmax:.2f}'
                      f'@{peak}  recovery {rec} (chance 16)  KADD {kmax:.2f}')
                continue
            tr, kk, nn, flats, clips = capture(t, scope, N, SAMPLES)
            with h5py.File(h5name, 'w') as f:
                f.create_dataset('traces', data=tr, compression='gzip')
                f.create_dataset('keys',
                                 data=np.frombuffer(b''.join(kk),
                                                    np.uint8).reshape(-1, 16))
                f.create_dataset('nonces',
                                 data=np.frombuffer(b''.join(nn),
                                                    np.uint8).reshape(-1, 16))
            if len(tr) < N:
                print(f'  [!] only {len(tr)} usable — skipping battery')
                continue
            pmax, peak, rec, kmax = battery(tr, kk, nn)
            print(f'  {time.time()-t0:.0f}s  {len(tr)} traces  '
                  f'popcount |r|={pmax:.2f}@{peak}  '
                  f'recovery {rec} (chance 16)  KADD {kmax:.2f}  '
                  f'flat {flats} clip {clips}  std {tr.std(1).mean()*1000:.1f} mV')
            print(f'  saved {h5name}')
    finally:
        target.vccint_set(1.0)
        print(f'[+] restored VCCINT = {target.vccint_get():.2f} V')


if __name__ == '__main__':
    main()