#!/usr/bin/env python3
r"""husky_day.py — one-shot orchestration for the Husky day session.

Run the full pipeline: connect → pick_gain → collect → preprocess → train →
attack → verify. Each step is a subprocess; the script exits on failure so
you can fix and re-run from the next step.

Usage:
    # Dry-run on SimBoard (test the flow)
    .venv/bin/python training/husky_day.py --sim

    # Real run on Husky
    .venv/bin/python training/husky_day.py \
        --key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 \
        --gain 20 --ntraces 3000 --M 16

    # Resume from step (e.g. after collect, re-train)
    .venv/bin/python training/husky_day.py --step train --model-only
"""
import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

STEPS = ['setup', 'collect', 'preprocess', 'train', 'attack']


def run(cmd, label, timeout=None):
    print(f'\n{"=" * 60}')
    print(f'  [{label}]')
    print(f'  {" ".join(cmd)}')
    print(f'{"=" * 60}')
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=False, text=True, timeout=timeout)
    ok = r.returncode == 0
    print(f'  [{label}] {"PASS" if ok else "FAIL"} in {time.time()-t0:.0f}s')
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--key', default='0f1e2d3c4b5a69788796a5b4c3d2e1f0',
                    help='target 16-byte key hex')
    ap.add_argument('--gain', type=int, default=None,
                    help='scope gain (auto-detected from pick_gain if omitted)')
    ap.add_argument('--ntraces', type=int, default=3000)
    ap.add_argument('--M', type=int, default=16,
                    help='traces per adaptive query (averaged, +10log10 dB)')
    ap.add_argument('--max-queries', type=int, default=400)
    ap.add_argument('--step', choices=STEPS + ['all'], default='all',
                    help='start from this step (resume support)')
    ap.add_argument('--sim', action='store_true',
                    help='SimBoard dry-run (no hardware)')
    ap.add_argument('--sim-amp', type=float, default=8.0)
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon',
                                         'ascon_cw305_top.bit'))
    args = ap.parse_args()

    py = sys.executable
    # outputs
    h5 = os.path.join(ROOT, 'Dataset', 'husky_run.h5')
    npz = os.path.join(ROOT, 'training', 'data', 'husky_run.npz')
    model = os.path.join(ROOT, 'training', 'models', 'joint_husky.pt')
    gain = args.gain

    if args.sim:
        # SimBoard dry-run: use existing data as simulated Husky capture
        h5 = os.path.join(ROOT, 'Dataset', 'main_unmasked_merged.h5')
        npz = os.path.join(ROOT, 'training', 'data', 'main_unmasked_merged.npz')
        model = os.path.join(ROOT, 'training', 'models', 'joint_husky.pt')
        print('[!] SIM MODE: using existing data, no hardware')
        print(f'[!] h5 = {h5}, npz = {npz}, model = {model}')

    start = 0 if args.step == 'all' else STEPS.index(args.step)

    # ---- step 0: setup + pick_gain ----
    if start <= 0 and not args.sim:
        if not run([py, os.path.join(ROOT, 'pick_gain.py'),
                    '-b', args.bitstream, '--n', '10'],
                   'pick_gain'):
            sys.exit(1)
        # parse gain from output? user sets it manually
        print('[!] Set --gain <BEST> from above output and re-run')
        sys.exit(0)

    if args.sim and start <= 0:
        print('[skip] pick_gain (sim mode)')

    # ---- step 1: collect dataset ----
    if start <= 1 and not args.sim:
        if gain is None:
            sys.exit('--gain required (from pick_gain output)')
        if not run([py, os.path.join(ROOT, 'collect_dataset.py'),
                    '-n', str(args.ntraces), '-o', h5,
                    '--gain', str(gain), '-b', args.bitstream],
                   'collect_dataset', timeout=600):
            sys.exit(1)
    elif args.sim and start <= 1:
        print(f'[skip] collect_dataset (sim mode: using {h5})')

    # ---- step 2: preprocess h5 -> npz ----
    if start <= 2:
        if not os.path.exists(h5):
            sys.exit(f'{h5} not found — run collect first')
        if not run([py, os.path.join(ROOT, 'training', 'preprocess.py'),
                    h5, '--window', '400'],
                   'preprocess'):
            sys.exit(1)

    # ---- step 3: train joint model ----
    if start <= 3:
        if not os.path.exists(npz):
            sys.exit(f'{npz} not found — run preprocess first')
        if not run([py, os.path.join(ROOT, 'training', 'train_joint.py'),
                    npz, '--window', '400', '--epochs', '40',
                    '--out', model],
                   'train_joint', timeout=600):
            sys.exit(1)

    # ---- step 4: parallel full-key attack ----
    if start <= 4:
        if not os.path.exists(model):
            sys.exit(f'{model} not found — run train first')
        cmd = [
            py, os.path.join(ROOT, 'training', 'adaptive_parallel.py'),
            '--npz', npz,
            '--joint-model', model,
            '--key', args.key,
            '--max-queries', str(args.max_queries),
            '--M', str(args.M),
        ]
        if args.sim:
            cmd += ['--sim', '--sim-amp', str(args.sim_amp)]
        else:
            cmd += ['--gain', str(gain), '--bitstream', args.bitstream]
        if not run(cmd, 'parallel_attack', timeout=1800):
            print('[!] Attack did not converge fully. Re-run with higher M')
            sys.exit(1)

    print(f'\n{"=" * 60}')
    print('  ALL DONE')
    print(f'  Dataset: {h5}')
    print(f'  Model:   {model}')
    print(f'  Key:     {args.key}')
    print(f'  M:       {args.M}')
    print(f'{"=" * 60}')


if __name__ == '__main__':
    main()