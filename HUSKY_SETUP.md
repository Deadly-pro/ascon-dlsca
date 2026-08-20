# CW-Husky Setup & Runbook

ChipWhisperer-Husky is the capture scope for the ASCON-128 side-channel attack
on the CW305 target board. All Python scripts in this repo auto-detect the
scope model (CW-Husky vs CW-Lite/CW-Pro) via `scope_config.py` and apply the
correct ADC clock settings, so the same commands work with either scope.

## 1. Physical connections

```
[CW305 target]  ---- 20-pin ribbon ----  [CW-Husky]   (trigger, clock, IO)
[CW305 target]  ---- USB (SAM3U)   ----  PC           (FPGA programming, regs)
[CW-Husky]      ---- USB-C         ----  PC           (ADC capture)
```

- CW305 power via its USB cable, as before.
- The 20-pin ribbon goes Husky -> CW305 (pin 1 = red stripe, marked on both).
- The analog power trace travels over the 20-pin ribbon (no SMA needed).
- On CW-Lite the same wiring applies minus the USB-C.

## 2. Linux USB permissions (once per machine)

Skip if a NewAE board already worked (same vendor ID 0x2B3E). Otherwise run
in a terminal with sudo:

```bash
sudo sh -c 'echo "SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"2b3e\", MODE=\"0666\"" > /etc/udev/rules.d/99-newae.rules'
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## 3. Bring-up order (each must pass before the next)

```bash
# 1) Scope detected + firmware
.venv/bin/python -c "import chipwhisperer as cw; s=cw.scope(); print(s)"

# 2) Full rig check (scope + bitstream + register map + one verified capture)
.venv/bin/python check_setup.py -b vivado_ascon/ascon_cw305_top.bit

# 3) Gain probe at the real capture config (auto-detects Husky vs CW-Lite)
.venv/bin/python pick_gain.py -b vivado_ascon/ascon_cw305_top.bit --gains 25,20,15,10,5,0,-5,-10,-15
```

If the scope firmware is outdated (warning printed), update it:

```bash
.venv/bin/python -c "import chipwhisperer as cw; cw.update_firmware('husky')"
```

## 4. Clock setup (what the code does for you)

`scope_config.setup_scope_clock()` is called by every capture script:

| Scope     | ADC clock config                          | Resulting sample rate |
|-----------|-------------------------------------------|-----------------------|
| CW-Lite/Pro | `adc_src='clkgen_x4'`, `clkgen_freq=40e6` | 40 MS/s |
| CW-Husky  | `clkgen_src='system'`, `adc_mul=1`, `clkgen_freq=40e6` | 40 MS/s |

On the Husky the old `adc_src='clkgen_x4'` would silently map to `adc_mul=4`
(160 MS/s), which is why the code sets the fields explicitly.

## 5. Capture a dataset

```bash
# 3000 traces, random keys, verified against the ASCON oracle
.venv/bin/python collect_dataset.py -n 3000 \
    -o Dataset/main_husky.h5 \
    --gain <GAIN FROM STEP 3> \
    -b vivado_ascon/ascon_cw305_top.bit
```

## 6. Active training loop (model picks inputs, trains, guesses key)

Train mode (random key per epoch, labels oracle-exact):

```bash
.venv/bin/python training/active_loop.py \
    --model training/models/main_unmasked_merged_c0_sbox_cnn1.pt \
    --npz training/data/main_unmasked_merged.npz \
    --column 0 --epochs 30 --max-traces 120 \
    --gain <GAIN FROM STEP 3> \
    --out training/models/active_c0
```

Attack mode (fixed unknown key, no online updates):

```bash
.venv/bin/python training/active_loop.py \
    --model training/models/active_c0/ep030_c0.pt \
    --npz training/data/main_unmasked_merged.npz \
    --column 0 --epochs 1 --max-traces 300 \
    --attack-key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 \
    --gain <GAIN FROM STEP 3> \
    --out training/models/active_c0_attack
```

Epoch semantics:
- Each epoch loads a fresh random key (train mode) or the fixed attack key
  (attack mode)
- The model picks each next nonce (posterior-aware separating selection),
  captures, trains on the trace (replay-buffer SGD), then reports its key guess
- The epoch ends when the same guess repeats `--stable-n` times with posterior
  above `--converge-p`, or when `--max-traces` is exhausted
- Every epoch appends a JSON line to `<out>/summary.jsonl` and saves a
  checkpoint `<out>/epNNN_c0.pt`

Watch `summary.jsonl`: in train mode the CORRECT rate should rise across
epochs as the model adapts to the device. Switch to attack mode with
`--attack-key` once it stabilizes, then run the 64-column attack:

```bash
for col in {0..63}; do
  .venv/bin/python training/active_loop.py \
    --model "training/models/main_unmasked_merged_c${col}_sbox_cnn1.pt" \
    --npz training/data/main_unmasked_merged.npz \
    --column "$col" --epochs 1 --max-traces 100 \
    --attack-key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 \
    --gain <GAIN FROM STEP 3> \
    --out "training/models/active_c${col}_attack" 2>&1 | tail -2
done
```

## 7. Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| `Could not find ChipWhisperer` | USB unplugged; check udev/driver rules |
| `adc_freq = 0.0 MHz` | Scope PLL not locked; re-run, or replug USB-C |
| All captures flat (std < 0.001) | 20-pin ribbon loose, or CW305 amplifier jumper at 0 dB (should be +20 dB) |
| Trigger timeout warnings | Expected; traces are still valid, alignment is software-based |
| Ciphertext mismatch in check_setup | FPGA running stock AES from SPI flash; re-program bitstream |

## 8. Code layout

| File | Purpose |
|------|---------|
| `scope_config.py` | Scope/target auto-detect + clock setup (single source of truth) |
| `check_setup.py` | One-shot bring-up check for new machines/teammates |
| `live_query.py` | Single-trace capture primitive (used by active loop) |
| `pick_gain.py` | Gain sweep at the real capture config |
| `pilot_gain.py` | Legacy calibration pilot (kept for reference) |
| `collect_dataset.py` | Bulk dataset capture to HDF5 |
| `training/active_loop.py` | Unified train-while-guessing closed loop |
| `training/adaptive.py` | ACPPA attack engine (column attacks) |
| `training/snr_sweep.py` | SNR/gain operating-point sweep |