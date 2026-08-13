#!/usr/bin/env python3
r"""sim_board.py — virtual CW305 board for closed-loop ACPPA without hardware.

Fits a noise + leakage model from a real unmasked capture, then answers
query(nonce) -> (trace, ct) with the SAME interface as live_query.LiveQuery,
so training/adaptive.py --sim runs the identical loop code against it.

Generation model (per sample t):
    trace(t) = mu(t) + amp * alpha(t) * (HW(key,nonce) - E[HW])
               + sigma(t) * noise(t) + drift_i + jitter_shift

where:
    mu(t)      aligned mean trace from the real capture (the "average op")
    alpha(t)   per-sample leakage template = regression slope of the real
               traces on HW of the target column (measured, not guessed)
    E[HW]      mean HW of the target column over the real (random-key) traces
    sigma(t)   residual noise std per sample after removing the leakage term
    noise(t)   unit-variance white noise + the lag-5 colored component
               measured in the real residual ACF
    drift_i    per-trace DC offset sampled from the measured distribution
    jitter     alignment shift sampled from the measured shift histogram

amp is the leakage gain knob: amp=1 reproduces the real per-column SNR,
amp>1 amplifies the leakage (the "what if the board leaked harder" sweep).
"""

import argparse
import os
import sys

import h5py
import numpy as np
from scipy import signal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))
import labels as lab
from ascon_ref import fpga_expected


def _fit_from_h5(path, column, k=300, target='sbox'):
    """Measure mu, alpha, sigma, drift distribution, jitter, lag-5 color.

    target='sbox' fits the round-1 S-box column leak (single alpha profile);
    target='kadd' fits the 8-byte KADD leak (one alpha profile per byte).
    """
    with h5py.File(path, 'r') as f:
        traces = f['traces'][:].astype(np.float64)
        keys = f['keys'][:]
        nonces = f['nonces'][:]
    n, T = traces.shape

    # align every trace to the mean (same as preprocess.align) so mu/sigma
    # and the jitter histogram are measured on aligned traces
    ref = traces.mean(axis=0)
    aligned = np.empty_like(traces)
    shifts = np.empty(n, dtype=np.int64)
    for i in range(n):
        c = signal.correlate(traces[i], ref, mode='same', method='fft')
        shifts[i] = int(np.argmax(c) - T // 2)
        aligned[i] = np.roll(traces[i], -int(shifts[i]))

    mu = aligned.mean(axis=0)

    if target == 'kadd':
        hw = lab.kadd_words_hw(keys, nonces).astype(np.float64)   # (N,8)
        alphas = np.empty((8, T))
        resid = aligned.copy()
        for b in range(8):
            hwc = hw[:, b] - hw[:, b].mean()
            alphas[b] = (aligned.T @ hwc) / (hwc @ hwc) if (hwc @ hwc) > 0 \
                else np.zeros(T)
            resid -= alphas[b][None, :] * hwc[:, None]
        sigma = resid.std(axis=0)
        mean_hw = hw.mean(axis=0)
        alpha = alphas
    else:
        hw = lab.round1_sbox_hw(keys, nonces)[:, column].astype(np.float64)
        hw_c = hw - hw.mean()
        var_hw = float(hw_c @ hw_c)
        alpha = (aligned.T @ hw_c) / var_hw if var_hw > 0 else np.zeros(T)
        resid = aligned - mu[None, :] - alpha[None, :] * hw_c[:, None]
        sigma = resid.std(axis=0)
        mean_hw = float(hw.mean())

    # per-trace DC drift (mean of the aligned trace after removing mu)
    drift = (aligned - mu[None, :]).mean(axis=1)

    # lag-5 colored component of the standardized residual
    r = (resid - resid.mean(axis=1, keepdims=True))
    r /= np.maximum(resid.std(axis=1, keepdims=True), 1e-9)
    rho5 = float(np.mean(r[:, 5:] * r[:, :-5]))
    if not np.isfinite(rho5):
        rho5 = 0.0

    return dict(mu=mu, alpha=alpha, sigma=sigma, drift=drift, shifts=shifts,
                rho5=rho5, mean_hw=mean_hw, n=n, samples=T, target=target)


class SimBoard:
    """Drop-in replacement for live_query.LiveQuery (same query/verify/close)."""

    def __init__(self, dataset_h5, key, column=0, amp=1.0, samples=2000,
                 seed=0, flat_p=0.0, fit_k=300, rail=0.49, target='sbox',
                 program=True):
        assert len(key) == 16
        self.key = bytes(key)
        self.column = int(column)
        self.target = target
        self.amp = float(amp)
        self.flat_p = float(flat_p)
        self.rng = np.random.default_rng(seed)
        fit = _fit_from_h5(dataset_h5, self.column, fit_k, target)
        self.mu = fit['mu']
        self.alpha = fit['alpha']
        self.sigma = fit['sigma']
        self.drift = fit['drift']
        self.shifts = fit['shifts']
        self.rho5 = fit['rho5']
        self.mean_hw = fit['mean_hw']
        self.samples = int(samples)
        self.rail = float(rail)
        self._noise_std = None

    def _noise(self, n):
        T = self.samples
        w = self.rng.standard_normal((n, T))
        if abs(self.rho5) > 1e-6:            # lag-5 colored component
            w = (w + self.rho5 * np.roll(w, 5, axis=1)) / np.sqrt(1 + self.rho5**2)
        return w

    def _trace_for(self, key, nonce):
        """Synthetic trace for an explicit (key, nonce) — the shared generator
        used by query() (fixed self.key) and generate_h5() (batch)."""
        kb = np.frombuffer(bytes(key), dtype=np.uint8)[None]
        nb = np.frombuffer(bytes(nonce), dtype=np.uint8)[None]
        if self.target == 'kadd':
            hw = lab.kadd_words_hw(kb, nb)[0].astype(np.float64)      # (8,)
            leak = np.zeros_like(self.mu)
            for b in range(8):
                leak += self.amp * self.alpha[b] * (hw[b] - self.mean_hw[b])
        else:
            hw = lab.round1_sbox_hw(kb, nb)[0, self.column]
            leak = self.amp * self.alpha * (int(hw) - self.mean_hw)
        noise = self.sigma * self._noise(1)[0]
        drift = float(self.rng.choice(self.drift))
        t = self.mu + leak + noise + drift
        shift = int(self.rng.choice(self.shifts))
        t = np.roll(t, -shift)
        return np.clip(t, -self.rail, self.rail)

    def query(self, nonce):
        """(nonce 16 bytes) -> (trace f64[2000], ct 16 bytes). None on "flat"."""
        if self.rng.random() < self.flat_p:  # mimic the trigger race
            return None, None
        t = self._trace_for(self.key, nonce)
        ct = fpga_expected(bytes(self.key), bytes(nonce))
        return t, ct

    def generate_h5(self, out_path, n=2000, key_mode='random'):
        """Write a training-ready h5 (same schema as collect_dataset.py) of
        synthetic traces — lets the normal preprocess/train pipeline run on
        sim data at any amp."""
        keys, nonces, traces, cts = [], [], [], []
        while len(keys) < n:
            key = os.urandom(16) if key_mode == 'random' else self.key
            nonce = os.urandom(16)
            t = self._trace_for(key, nonce)
            traces.append(t)
            keys.append(bytes(key))
            nonces.append(bytes(nonce))
            cts.append(fpga_expected(bytes(key), bytes(nonce)))
        tr = np.array(traces, dtype=np.float32)
        with h5py.File(out_path, 'w') as f:
            f.create_dataset('traces', data=tr, compression='gzip')
            f.create_dataset('keys', data=np.frombuffer(b''.join(keys), np.uint8).reshape(-1, 16))
            f.create_dataset('nonces', data=np.frombuffer(b''.join(nonces), np.uint8).reshape(-1, 16))
            f.create_dataset('ciphertexts', data=np.frombuffer(b''.join(cts), np.uint8).reshape(-1, 16))
            f.attrs['adc_samples'] = self.samples
            f.attrs['fs_hz'] = 40e6
            f.attrs['crypto_clk_hz'] = 10e6
            f.attrs['gain_db'] = -2
            f.attrs['gain_note'] = 'SIMULATED (SimBoard) — leakage amp %g, noise model from real capture' % self.amp
            f.attrs['adc_src'] = 'clkgen_x4'
            f.attrs['key_mode'] = key_mode
            f.attrs['verified'] = True
            f.attrs['num_traces'] = int(n)
            f.attrs['sim_amp'] = self.amp
            f.attrs['source_bitstream'] = 'SIMULATED'
        print(f'[+] wrote {n} simulated traces -> {out_path}')
        return out_path

    def verify_key(self, candidate_key, nonce=None):
        """Interface parity with LiveQuery: sim CTs always match the oracle."""
        candidate_key = bytes(candidate_key)
        if len(candidate_key) != 16:
            return False, None, None
        nonce = self.rng.bytes(16) if nonce is None else bytes(nonce)
        exp = fpga_expected(candidate_key, nonce)
        return True, exp.hex(), exp.hex()

    def close(self):
        pass


def _self_test():
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', nargs='?', default='Dataset/main_unmasked_merged.h5')
    ap.add_argument('--column', type=int, default=0)
    ap.add_argument('--amp', type=float, default=1.0)
    ap.add_argument('--ntraces', type=int, default=2000)
    ap.add_argument('--generate', metavar='OUT.h5', default=None,
                    help='write a training h5 of n simulated traces and exit')
    args = ap.parse_args()
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'training'))

    key = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
    b = SimBoard(args.h5, key, column=args.column, amp=args.amp, seed=7)

    if args.generate:
        b.generate_h5(args.generate, n=args.ntraces)
        return

    fit = _fit_from_h5(args.h5, args.column)

    print(f'fit: n={fit["n"]} samples={fit["samples"]} col={args.column}')
    print(f'  mu range [{fit["mu"].min():.3f}, {fit["mu"].max():.3f}]')
    print(f'  sigma med {np.median(fit["sigma"]):.4f}, '
          f'alpha peak {fit["alpha"][np.argmax(np.abs(fit["alpha"]))]:.4f}')
    print(f'  drift std {fit["drift"].std():.4f}, jitter {fit["shifts"].min()}..'
          f'{fit["shifts"].max()}, lag-5 rho {fit["rho5"]:.3f}')

    # real per-column SNR (between/within class, as in view_dataset)
    def snr_of(traces, lbl):
        means = np.array([traces[lbl == c].mean(0) for c in np.unique(lbl)])
        vars_ = np.array([traces[lbl == c].var(0) for c in np.unique(lbl)])
        return means.var(0) / np.maximum(vars_.mean(0), 1e-12)

    import h5py as _h5
    with _h5.File(args.h5, 'r') as f:
        rtr = f['traces'][:].astype(np.float64)
        rk, rn = f['keys'][:], f['nonces'][:]
    rlbl = lab.round1_sbox_hw(rk, rn)[:, args.column].astype(np.int64)
    r_snr = snr_of(rtr, rlbl)
    real_db = 10 * np.log10(r_snr.max())

    # sim traces at same amp
    sim_tr = np.empty((args.ntraces, b.samples))
    sim_nt = []
    while len(sim_nt) < args.ntraces:
        n_ = np.random.default_rng(len(sim_nt) + 1).bytes(16)
        t, _ = b.query(n_)
        if t is None:
            continue
        sim_tr[len(sim_nt)] = t
        sim_nt.append(n_)
    slbl = lab.round1_sbox_hw(
        np.frombuffer(b''.join([key] * len(sim_nt)), np.uint8).reshape(-1, 16),
        np.frombuffer(b''.join(sim_nt), np.uint8).reshape(-1, 16)
    )[:, args.column].astype(np.int64)
    s_snr = snr_of(sim_tr, slbl)
    sim_db = 10 * np.log10(s_snr.max())

    print(f'\nSNR check: real {real_db:.1f} dB vs sim(amp={args.amp}) {sim_db:.1f} dB '
          f'(amp=1 should match the real capture)')
    print(f'  sim trace stats: mean {sim_tr.mean():.3f} std {sim_tr.std():.4f}, '
          f'range [{sim_tr.min():.3f}, {sim_tr.max():.3f}]')


if __name__ == '__main__':
    _self_test()
