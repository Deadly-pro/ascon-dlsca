#!/usr/bin/env python3
r"""snr_sweep.py — find the analog operating point with the best real SNR.

For each (gain, offset) combo: capture ~N traces from the board, compute the
measured S-box col-0 SNR and KADD byte-SNR (between/within class, as in
view_dataset). This answers whether the programmable gain (applied BEFORE the
ADC) has untapped headroom once the DC level is centered with the offset DAC —
all earlier gain probes ran at offset 0 where clipping hid the answer.

If SNR is flat across gains => ADC/quantization not the limit => leakage is
intrinsic => hybrid enumeration or a real probe is the path.
If SNR rises with gain => collect the dataset at that operating point.

Usage:
    .venv/bin/python training/snr_sweep.py --ntraces 300
"""
import argparse
import os
import sys
import time

import h5py
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labels as lab


def snr_db(traces, y):
    y = np.asarray(y)
    classes = np.unique(y)
    if len(classes) < 2:
        return float('-inf')
    means = np.array([traces[y == c].mean(0) for c in classes])
    vars_ = np.array([traces[y == c].var(0) for c in classes])
    s = means.var(0) / np.maximum(vars_.mean(0), 1e-12)
    return float(10 * np.log10(s.max()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ntraces', type=int, default=300, help='traces per setting')
    ap.add_argument('--samples', type=int, default=2000)
    ap.add_argument('--bitstream',
                    default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         '..', 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--out', default=None, help='optional h5 of the best setting')
    args = ap.parse_args()

    import chipwhisperer as cw
    from cw305_ascon_shim import wrap

    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=args.bitstream, fpga_id='100t', platform='cw305')
    target.vccint_set(1.0)
    target.pll.pll_enable_set(True)
    target.pll.pll_outenable_set(False, 0)
    target.pll.pll_outenable_set(True, 1)
    target.pll.pll_outenable_set(False, 2)
    target.pll.pll_outfreq_set(10e6, 1)
    target.clkusbautooff = True
    target.clksleeptime = 1
    target.fpga_write(0x00, [0x19])
    t = wrap(target)

    scope = cw.scope()
    scope.adc.samples = args.samples
    scope.clock.adc_src = 'clkgen_x4'
    scope.clock.clkgen_freq = 40e6
    scope.trigger.triggers = 'tio4'

    # (gain, offset) grid: gain = programmable + ~20 dB fixed external.
    # offsets 100/700/900 were the clean DC-centering windows found earlier.
    grid = [(-2, 0), (-2, 700), (0, 700), (2, 700), (4, 700),
            (6, 700), (8, 700), (4, 100), (4, 900)]
    best = None
    rows = []
    for gain, off in grid:
        scope.gain.db = gain
        scope.adc.offset = off
        scope.clock.reset_adc()
        time.sleep(0.2)
        traces, keys, nonces = [], [], []
        n_valid = 0
        while n_valid < args.ntraces:
            key = os.urandom(16)
            nonce = os.urandom(16)
            t.loadEncryptionKey(key)
            t.loadInput(nonce)
            scope.arm()
            t.go()
            scope.capture()
            tr = scope.get_last_trace()
            if tr is None or tr.size != args.samples or tr.std() < 0.01:
                continue
            if np.abs(tr).max() > 0.49:      # same filter as collect_dataset.py
                continue
            traces.append(tr)
            keys.append(key)
            nonces.append(nonce)
            n_valid += 1
        tr = np.array(traces)
        kb = np.frombuffer(b''.join(keys), np.uint8).reshape(-1, 16)
        nb = np.frombuffer(b''.join(nonces), np.uint8).reshape(-1, 16)
        y_sbox = lab.round1_sbox_hw(kb, nb)[:, 0]
        y_kadd = lab.kadd_words_hw(kb, nb)[:, 3]
        s_sbox = snr_db(tr, y_sbox)
        s_kadd = snr_db(tr, y_kadd)
        row = {'gain': gain, 'offset': off, 'sbox_snr_db': s_sbox,
               'kadd_snr_db': s_kadd, 'clip': 0.0, 'std': float(tr.std())}
        rows.append(row)
        print(f"gain {gain:+2d} off {off:4d}: sbox {s_sbox:6.1f} dB  "
              f"kadd {s_kadd:6.1f} dB  std {row['std']:.4f}")
        if best is None or s_kadd > best['kadd_snr_db']:
            best = dict(row, traces=tr, keys=keys, nonces=nonces)

    scope.dis()
    target.dis()

    print(f"\n[+] best KADD SNR: gain {best['gain']:+d} offset {best['offset']} "
          f"-> {best['kadd_snr_db']:.1f} dB (sbox {best['sbox_snr_db']:.1f} dB)")
    if args.out:
        with h5py.File(args.out, 'w') as f:
            f.create_dataset('traces', data=best['traces'].astype(np.float32),
                             compression='gzip')
            f.create_dataset('keys', data=np.array(best['keys']))
            f.create_dataset('nonces', data=np.array(best['nonces']))
            for k_, v_ in best.items():
                if k_ not in ('traces', 'keys', 'nonces'):
                    f.attrs[k_] = v_
        print(f'[+] wrote best-setting traces -> {args.out}')


if __name__ == '__main__':
    main()
