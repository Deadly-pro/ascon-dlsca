# Model Training Workspace

This directory is the staging area for the deep-learning side of the ASCON
DL-SCA project: dataset EDA, preprocessing, feature/label selection, and the
training/evaluation pipeline.

## Scripts

| script | purpose |
|--------|---------|
| `overview.py` | side-by-side health comparison of every `Dataset/*.h5` |
| `eda.py` | per-dataset report: health, alignment, active region, leakage scans, spectrum |
| `preprocess.py` | align, crop to op window, z-score, second-order centered-product features, per-byte HW labels → `training/data/*.npz` |
| `train.py` | MLP profile on a target byte, train/val/test by trace, accuracy vs chance → `training/results/*.json` |

## Running

From the repo root (use the project venv, `.venv/`, which has CPU torch):

```bash
python3.12 -m venv .venv && .venv/bin/pip install -r training/requirements.txt
.venv/bin/python training/overview.py
.venv/bin/python training/eda.py Dataset/main2.h5
.venv/bin/python training/preprocess.py Dataset/main2.h5
.venv/bin/python training/train.py training/data/main2.npz --byte 3
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

4. **No strong first-order leakage on the KADD intermediate.** KADD-SNR peaks
   at ~4 dB (100-trace demo, sample ~182 / ~4.5 µs). This is expected: the core
   is masked (d=1, 2-share), so first-order CPA/SNR on a single intermediate
   should be weak. A meaningful attack will need either second-order (centered
   product) features or a focus on glitches/combination leakage — not plain
   HW-of-one-intermediate labels.

5. **Amplitude scaling differs across gains.** run1/run2 (gain 25) clip ~42 %
   of traces; main.h5 (gain −5) never clips but has the weakest signal. For
   training pick one gain regime and normalize consistently (per-trace
   z-score or global min/max).

### Recommended next steps for training

- Collect a fresh training set at a stable gain with `--samples 2000` to cut
  the dead window; verify with `overview.py` that clip ≈ 0 % and flat ≈ 0 %.
  (`main2.h5` is this capture and is the primary training set.)
- Preprocess: align to the trigger edge, crop to 0–50 µs, band-pass filter,
  per-trace normalization.
- Start with second-order / higher-order features (e.g. adjacent-sample
  products after centering) or DL-SCA targeting the masked S-box output,
  evaluating with train/val/test split by key/nonce.

## First training results (masked d=1 core, second-order features)

`preprocess.py` aligns, crops to 0–50 µs, z-scores, and builds centered-product
features at lags 1 and 4 samples (one crypto clock @ 10 MHz ≈ 4 samples).
Labels are the Hamming weight (0–8) of each byte of S[3] after ASCON init + KADD
(from `ascon_ref.py`). A 3-layer MLP (128–256–256) is trained on 70 %, validated
on 15 %, tested on the held-out 15 %; every trace has a unique random key, so
test accuracy above chance (11.1 %) means the model generalizes to unseen keys.

| npz | traces | byte | test acc | vs chance (11.1 %) |
|-----|--------|------|----------|--------------------|
| `main2.npz` | 9151 | 3 | 28.0 % | 2.5× |
| `main.npz` | 8028 | 3 | 26.1 % | 2.4× |
| `main2.npz` | 9151 | 0 | 23.6 % | 2.1× |

**Takeaway:** the model recovers key-dependent leakage on held-out keys — a real,
generalizing DL-SCA signal on the masked core. All 8 S[3] bytes train to
24–28 % (byte 3 strongest). Byte 3 in `main2.npz` is the current best target at
28.0 % test accuracy. Next step is moving from HW-classification accuracy to
actual key recovery (guessing entropy) — byte-level HW alone is not enough to
recover a 128-bit key; we need a 256-class byte-value profile or a
factorable-key attack on the first-round S-box output.
