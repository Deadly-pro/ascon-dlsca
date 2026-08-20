#!/usr/bin/env python3
import os
import sys
import subprocess

KEY_HEX = "0f1e2d3c4b5a69788796a5b4c3d2e1f0"  # Target key to break
BITSTREAM = "vivado_ascon/ascon_cw305_top.bit"
NPZ = "training/data/main2.npz"

os.makedirs("training/models", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("[+] Starting 64-column full key recovery...")

for col in range(64):
    model_path = f"training/models/main_unmasked_c{col}_liveft.pt"

    # 1. Live fine-tuning for column
    if not os.path.exists(model_path):
        print(f"\n--- [Col {col}/63] Step 1: Live Fine-Tuning ---")
        cmd_ft = [
            ".venv/bin/python", "training/live_finetune.py",
            "--model", "training/models/main2_c0_sbox_cnn2.pt",
            "--npz", NPZ,
            "--random-keys",
            "--column", str(col),
            "--ntrain", "300",
            "--epochs", "15",
            "--gain", "20",
            "--online",
            "--active-mode", "separating",
            "--out", model_path,
            "--bitstream", BITSTREAM
        ]
        subprocess.run(cmd_ft, check=True)

    # 2. Adaptive key extraction attack
    print(f"\n--- [Col {col}/63] Step 2: ACPPA Attack ---")
    cmd_attack = [
        ".venv/bin/python", "training/adaptive.py", "--attack",
        "--model", model_path,
        "--npz", NPZ,
        "--column", str(col),
        "--key", KEY_HEX,
        "--max-queries", "300",
        "--M", "1",
        "--gain", "20",
        "--bitstream", BITSTREAM
    ]
    subprocess.run(cmd_attack, check=True)

print("\n[+] Full 128-bit key extraction complete! Results saved in results/")