#!/usr/bin/env python3
r"""run_full_attack.py — 64-column full-key recovery on hardware or SimBoard.

For each of the 64 round-1 S-box columns: runs the unified active loop
(training/active_loop.py) in ATTACK mode against the target key, then
assembles the 128 recovered bits and verifies the full key against the ASCON
oracle.

Usage (hardware, Husky or CW-Lite — scope auto-detected):
    .venv/bin/python training/run_full_attack.py \
        --key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 --gain 20

Usage (SimBoard, no hardware):
    .venv/bin/python training/run_full_attack.py \
        --key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 \
        --sim --sim-amp 8.0

Results: one JSON line per column in training/results/active_*_attack/summary.jsonl,
plus a final assembly report printed at the end.
"""
import argparse
import glob
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--key', default='0f1e2d3c4b5a69788796a5b4c3d2e1f0',
                    help='Target 16-byte key hex to recover')
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit'))
    ap.add_argument('--npz', default=os.path.join(ROOT, 'training', 'data',
                                                    'main_unmasked_merged.npz'))
    ap.add_argument('--base-model-dir', default=os.path.join(
        ROOT, 'training', 'models',
        'main_unmasked_merged_c{col}_sbox_cnn1.pt'),
        help='per-column model path template with {col}')
    ap.add_argument('--gain', type=int, default=20)
    ap.add_argument('--max-traces', type=int, default=100,
                    help='max traces per column attack')
    ap.add_argument('--sim', action='store_true', help='Use SimBoard virtual board')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset',
                                                     'main_unmasked_merged.h5'))
    ap.add_argument('--sim-amp', type=float, default=8.0)
    args = ap.parse_args()

    py = sys.executable
    os.makedirs(os.path.join(ROOT, 'training', 'results'), exist_ok=True)

    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('--key must be 16 bytes hex')

    print(f'[+] 64-column full-key recovery, target key: {args.key}')
    print(f'[+] base model template: {args.base_model_dir}')

    rows = []
    for col in range(64):
        model = args.base_model_dir.format(col=col)
        if not os.path.exists(model):
            print(f'[!] column {col:02d}: model missing ({model}) - skipping')
            continue
        out = os.path.join(ROOT, 'training', 'results', f'active_c{col}_full')
        print(f'\n=== [Column {col:02d}/63] active loop (attack mode) ===')
        cmd = [
            py, os.path.join(ROOT, 'training', 'active_loop.py'),
            '--model', model,
            '--npz', args.npz,
            '--column', str(col),
            '--epochs', '1',
            '--max-traces', str(args.max_traces),
            '--attack-key', args.key,
            '--gain', str(args.gain),
            '--out', out,
        ]
        if args.sim:
            cmd += ['--sim', '--sim-h5', args.sim_h5, '--sim-amp', str(args.sim_amp)]
        subprocess.run(cmd, check=True)

        # read back the summary for this column
        log = os.path.join(out, 'summary.jsonl')
        if os.path.exists(log):
            with open(log) as f:
                rows.append(json.loads(f.readlines()[-1]))
        else:
            print(f'[!] column {col:02d}: no result - skipped')

    # ---- assemble the 128-bit key ----
    import numpy as np
    sys.path.insert(0, os.path.join(ROOT, 'training'))
    import labels as lab

    hyps = lab.all_hypotheses()
    bits = np.zeros(128, dtype=np.uint8)
    any_missing = False
    for row in rows:
        col = row['column']
        k0, k1 = row['k0'], row['k1']
        bits[col] = k0
        bits[64 + col] = k1
        if not row['converged']:
            any_missing = True

    candidate = bytes(np.packbits(bits, bitorder='little'))
    truth = np.unpackbits(np.frombuffer(key, dtype=np.uint8), bitorder='little')
    match = 100.0 * (1 - np.count_nonzero(bits != truth) / 128.0)

    print(f'\n=== FULL KEY RESULT ===')
    print(f'  columns attacked : {len(rows)}/64')
    print(f'  converged        : '
          f'{sum(1 for r in rows if r["converged"])}/{len(rows)}')
    print(f'  correct bits     : {match:.1f}%')
    print(f'  recovered key    : {candidate.hex()}')
    print(f'  target key       : {key.hex()}')
    if any_missing:
        print('  [n] some columns did NOT converge; assembled key is incomplete')
    if match == 100.0:
        print('  result: FULL KEY RECOVERED')
    else:
        print('  result: key not fully recovered')

    # save assembly report
    out = os.path.join(ROOT, 'training', 'results', 'full_key_assembly.json')
    with open(out, 'w') as f:
        json.dump({'target_key': key.hex(), 'recovered_key': candidate.hex(),
                   'accuracy_pct': match, 'columns': rows}, f, indent=2)
    print(f'  wrote {out}')


if __name__ == '__main__':
    main()