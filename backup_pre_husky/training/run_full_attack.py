#!/usr/bin/env python3
r"""run_full_attack.py — Automated 64-column full key recovery pipeline.

Runs fine-tuning and adaptive ACPPA attack across all 64 round-1 S-box columns
to recover the full 128-bit key from the CW305 hardware.
"""
import argparse
import os
import sys
import subprocess

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
    ap.add_argument('--base-model',
                    default=None,
                    help='Base profile template; default: per-column unmasked '
                         'main_unmasked_merged_c{col}_sbox_cnn1.pt (NEVER use '
                         'the masked main2 scaffold — collapses to majority-HW)')
    ap.add_argument('--M', type=int, default=4,
                    help='Nonce-repetition averaging (SNR lever)')
    ap.add_argument('--cal', action='store_true',
                    help='Likelihood-ratio scoring (logits/T - log prior)')
    ap.add_argument('--gain', type=int, default=20)
    ap.add_argument('--ntrain', type=int, default=300)
    ap.add_argument('--max-queries', type=int, default=300)
    ap.add_argument('--sim', action='store_true', help='Use SimBoard virtual board')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset', 'main_unmasked_merged.h5'))
    ap.add_argument('--sim-amp', type=float, default=8.0)
    args = ap.parse_args()

    py = sys.executable
    os.makedirs(os.path.join(ROOT, 'training', 'models'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'results'), exist_ok=True)

    print(f'[+] Starting 64-column full 128-bit key extraction target key: {args.key}')
    print(f'[+] base model: {args.base_model or "per-column main_unmasked_merged_c{col}_sbox_cnn1.pt"}')
    print(f'[+] npz: {args.npz}  M={args.M}  cal={args.cal}')

    for col in range(64):
        base_model = args.base_model or os.path.join(
            ROOT, 'training', 'models',
            f'main_unmasked_merged_c{col}_sbox_cnn1.pt')
        model_path = os.path.join(ROOT, 'training', 'models', f'main_unmasked_c{col}_liveft.pt')

        # Step 1: Fine-tune if model doesn't exist
        if not os.path.exists(model_path):
            print(f'\n=== [Column {col:02d}/63] Step 1: Online Live Fine-Tuning ===')
            ft_cmd = [
                py, os.path.join(ROOT, 'training', 'live_finetune.py'),
                '--model', base_model,
                '--npz', args.npz,
                '--random-keys',
                '--column', str(col),
                '--ntrain', str(args.ntrain),
                '--epochs', '15',
                '--gain', str(args.gain),
                '--online',
                '--active-mode', 'separating',
                '--out', model_path,
                '--bitstream', args.bitstream
            ]
            if args.sim:
                ft_cmd.extend(['--sim', '--sim-h5', args.sim_h5, '--sim-amp', str(args.sim_amp)])
            subprocess.run(ft_cmd, check=True)

        # Step 2: ACPPA key recovery
        print(f'\n=== [Column {col:02d}/63] Step 2: ACPPA Key Extraction ===')
        attack_cmd = [
            py, os.path.join(ROOT, 'training', 'adaptive.py'), '--attack',
            '--model', model_path,
            '--npz', args.npz,
            '--column', str(col),
            '--key', args.key,
            '--max-queries', str(args.max_queries),
            '--M', str(args.M),
            '--gain', str(args.gain),
            '--bitstream', args.bitstream
        ]
        if args.cal:
            attack_cmd.append('--cal')
        if args.sim:
            attack_cmd.extend(['--sim', '--sim-h5', args.sim_h5, '--sim-amp', str(args.sim_amp)])
        subprocess.run(attack_cmd, check=True)

    print('\n[+] 64-column key extraction complete!')

    # Step 3: End-to-end full 128-bit key assembly & verification
    import json
    import glob
    recovered_key = bytearray(16)
    recovered_cols = 0
    results_dir = os.path.join(ROOT, 'training', 'results')

    for col in range(64):
        files = glob.glob(os.path.join(results_dir, f'adaptive_c{col}_q*.json'))
        if not files:
            print(f'[!] Column {col} missing result file!')
            continue
        # Get latest result
        latest = max(files, key=os.path.getmtime)
        with open(latest, 'r') as f:
            res = json.load(f)
        k0, k1 = res['k0'], res['k1']
        bit = col % 8
        recovered_key[col // 8] |= (k0 << bit)
        recovered_key[8 + (col // 8)] |= (k1 << bit)
        recovered_cols += 1

    rec_hex = recovered_key.hex()
    print(f'\n==================================================')
    print(f'   RECOVERED KEY ({recovered_cols}/64 cols): {rec_hex}')
    print(f'   TARGET KEY:                   {args.key}')
    print(f'==================================================')

    if rec_hex == args.key.lower():
        print('[+] SUCCESS: Recovered key matches target key byte-for-byte!')
    else:
        diffs = sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(recovered_key, bytes.fromhex(args.key)))
        print(f'[!] MISMATCH: {diffs} bit errors out of 128 bits.')


if __name__ == '__main__':
    main()
