# Model Training Workspace

This directory is the staging area for the deep-learning side of the ASCON
DL-SCA project: dataset EDA, preprocessing, feature/label selection, and the
training/evaluation pipeline.

## Scripts

| script | purpose |
|--------|---------|
| `overview.py` | side-by-side health comparison of every `Dataset/*.h5` |
| `eda.py` | per-dataset report: health, alignment, active region, leakage scans, spectrum |
| `preprocess.py` | align, crop to op window, z-score → `training/data/*.npz` with `labels_sbox` (N,64) + `labels_kadd` (N,8) |
| `labels.py` | vectorized label generators, verified against `ascon_ref.py` (self-test in `python3 labels.py`) |
| `train.py` | train cnn1/cnn2/mlp profile on a target byte/column, 80/20 trace split, accuracy vs chance → `training/results/*.json` |
| `attack.py` | guessing-entropy / key-rank evaluation of a trained profile on the held-out 20 % |

## Running

From the repo root (use the project venv, `.venv/`, which has CPU torch):

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r training/requirements.txt
.venv/bin/python training/overview.py
.venv/bin/python training/eda.py Dataset/main2.h5
.venv/bin/python training/preprocess.py Dataset/main2.h5
.venv/bin/python training/train.py training/data/main2.npz --target kadd --column 3 --arch mlp
.venv/bin/python training/attack.py training/data/main2.npz \
    --model training/models/main2_c3_kadd_mlp.pt --target kadd --column 3
```

Plots are written to `training/plots/<dataset>/` and derived features to
`training/data/` (both gitignored). Results land in `training/results/`.

## Dataset Conclusions (captures to date)

The table below comes from `training/overview.py` (KADD-SNR measured in the
0–50 µs window where the crypto operation actually sits):

| file | traces | clip | flat | gain | KADD-SNR (0–50 µs) | verdict |
|------|--------|------|------|------|--------------------|---------|
| `main2.h5` | 9151 | 0 % | 0 % | −5 dB | 1.6 dB | best — short window, tight alignment |
| `main.h5` | 8028 | 0 % | 0 % | −5 dB | −1.8 dB | usable, 12× dead window |
| `run1.h5` | 1000 | 41.7 % | 0 % | 25 dB | −3.0 dB | usable (filtered), heavy clipping |
| `run2.h5` | 1000 | 42.3 % | 50.2 % | 25 dB | −1.5 dB | drop — half the traces are flat |
| `pilot.h5` | 7 | 0 % | 0 % | −5 dB | 112 dB (artifact) | diagnostic only |

### Key findings

1. **The window is far too long.** The active crypto region is in the first
   ~50 µs (first ~2000 samples @ 40 MHz), but captures are 600 µs / 24000
   samples. The whole window shows variance, so the per-sample leakage scans
   are diluted by 12× of idle/USB-re-enable noise. Fix: collect with
   `--samples 2000` (and consider `extclk_x4`) for training data.

2. **run2.h5 is unusable** — 50 % of traces are flat (`std < 0.01`), almost
   certainly a trigger/timing problem during that session. It must not be used
   for training.

3. **Alignment jitter is a real problem.** run1 shows 28 µs (±560 samples)
   spread; main.h5 is much better (5.6 µs). Traces must be re-aligned
   (cross-correlation against the mean) before any feature extraction or CNN
   input, or the leakage peaks smear out.

4. **No strong first-order leakage on the round-1 S-box output.** SNR is
   ≈ −23 dB in first order AND second order (lags 1/4/8/16). This is expected:
   the core is masked (d=1, 2-share), so first-order leakage on a masked
   intermediate should be weak. The KADD intermediate (S[3] after init+KADD)
   leaks far more: first-order SNR ≈ −12.4 dB, ~12 dB stronger than the S-box.

5. **Amplitude scaling differs across gains.** run1/run2 (gain 25) clip ~42 %
   of traces; main.h5 (gain −5) never clips but has the weakest signal. For
   training pick one gain regime and normalize consistently (per-trace
   z-score or global min/max).

### Label provenance

All labels are computed with `labels.py` and verified **byte-for-byte against
`ascon_ref.py`** (the hardware-verified oracle, 5/5 KATs on the CW305 bitstream)
via the self-test (`python3 training/labels.py`): `round1_sbox_hw` and
`kadd_words_hw` both pass 100 % of checks. The bit-sliced S-box used in
`labels.py` matches the published ASCON S-box table under a bit-reversal
convention of both input and output — same function, different column packing.

- `labels_kadd` (N,8): HW of each byte of S[3] after the 12-round init
  permutation + key XOR. Depends on the **full** 128-bit key (not factorable
  per byte) → used for profiled *intermediate recovery*, not per-byte key rank.
- `labels_sbox` (N,64): HW of the round-1 S-box output per column. Each column
  depends on only 2 key bits → factorable for key-rank, but this is the target
  the masking suppresses.

### Recommended next steps for training

- Collect a fresh training set at a stable gain with `--samples 2000` to cut
  the dead window; verify with `overview.py` that clip ≈ 0 % and flat ≈ 0 %.
  (`main2.h5` is this capture and is the primary training set.)
- Preprocess: align to the trigger edge, crop to 0–50 µs, band-pass filter,
  per-trace normalization.
- Start with second-order / higher-order features (e.g. adjacent-sample
  products after centering) or DL-SCA targeting the masked S-box output,
  evaluating with train/val/test split by key/nonce.

## Training results (masked d=1 core, held-out random-key traces)

`preprocess.py` aligns, crops to 0–50 µs, and z-scores. `train.py` trains a
profile on 80 % of traces and validates on the held-out 20 %; every trace has a
unique random key, so validation accuracy above chance means the model
generalizes to unseen keys. All 8 KADD bytes leak at ~2× chance regardless of
architecture:

| target | arch | best val | vs chance |
|--------|------|----------|-----------|
| KADD byte 0 | mlp (products) | 21.6 % | 1.9× (11.1 %) |
| KADD byte 3 | mlp (products) | 20.5 % | 1.9× |
| KADD byte 5 | mlp (products) | 21.0 % | 1.9× |
| KADD byte 3 | cnn2 (2nd-order) | 18.2 % | 1.6× |
| KADD byte 3 | cnn1 (1st-order) | 11.6 % | 1.0× |
| S-box col 1 | cnn2 (2nd-order) | 24.4 % | 1.2× (20 %) |

**Takeaway:** the model recovers key-dependent leakage on held-out keys — a
real, generalizing DL-SCA signal on the masked core, concentrated on the KADD
intermediate. The centered-product MLP (raw + lags 1,4, 5995-dim) is the
strongest and cheapest; cnn1 on the raw trace is at chance, as expected for a
masked core.

### Guessing entropy (`attack.py`)

`attack.py` scores the trained profile on the same held-out 20 % never touched
during training, with `train.py`'s exact split (same npz + seed):

- **KADD target** — intermediate recovery. Each trace carries a different
  random key and the target depends on the full 128-bit key, so there is no
  global key hypothesis to rank; the honest metric is the mean rank of the true
  intermediate HW class per trace (chance = 5 for 9 classes). Byte 3: mean rank
  3.17 (MLP), top-1 18.6 % — the model places the true intermediate top-3 on
  average.
- **S-box target** — key-rank control. Per column only 2 key bits are unknown
  (4 hypotheses); accumulated-log-prob key-bits GE stays at ~2.2–2.5 / 4
  (chance 2.5): the naive first-order target is defeated, as the masking
  intends.

A clean key-recovery GE (as in the unmasked ~800-trace literature figures)
requires a **fixed-key attack capture** — collect one with
`collect_dataset.py --key <hex>` and point `attack.py --target sbox` at it.
