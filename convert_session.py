#!/usr/bin/env python3
r"""convert_session.py — flatten live-loop session H5s into the flat
dataset format (traces/keys/nonces) that sim_board.py and the standard
training pipeline expect.

Usage:
    .venv/bin/python convert_session.py Dataset/live_xfm_session_*.h5 \
        -o Dataset/session_unmasked_flat.h5
"""
import argparse
import glob

import h5py
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('h5', nargs='+')
    ap.add_argument('-o', '--out', required=True)
    args = ap.parse_args()

    paths = sorted(p for pat in args.h5 for p in glob.glob(pat))
    traces, keys, nonces = [], [], []
    for path in paths:
        with h5py.File(path, 'r', locking=False) as f:
            for name in sorted(f.keys()):
                g = f[name]
                if 'traces' not in g:
                    continue
                key = np.asarray(g.attrs['key'], dtype=np.uint8)
                traces.append(g['traces'][:])
                keys.append(np.repeat(key[None], len(g['nonces']), axis=0))
                nonces.append(g['nonces'][:])
    traces = np.concatenate(traces).astype(np.float32)
    keys = np.concatenate(keys)
    nonces = np.concatenate(nonces)
    print(f'[+] {len(paths)} sessions -> {len(traces)} traces '
          f'{traces.shape[1]} samples')
    with h5py.File(args.out, 'w') as f:
        f.create_dataset('traces', data=traces)
        f.create_dataset('keys', data=keys)
        f.create_dataset('nonces', data=nonces)
    print(f'[+] wrote {args.out}')


if __name__ == '__main__':
    main()
