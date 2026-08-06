# Model Training Workspace

This directory is the staging area for the machine-learning side of the ASCON
SCA project: dataset EDA, preprocessing, feature/label selection, and the
training/evaluation pipeline (to be added).

## Scripts

| script | purpose |
|--------|---------|
| `overview.py` | side-by-side health comparison of every `Dataset/*.h5` |
| `eda.py` | per-dataset report: health, alignment, active region, leakage scans, spectrum |
| (next) `preprocess.py` | window/crop, alignment, filtering, feature extraction |
| (next) `train.py` | model training + metrics |

## Running

From the repo root:

```bash
python3 training/overview.py
python3 training/eda.py Dataset/main.h5 --subsample 4000
python3 training/eda.py Dataset/run1.h5
```

Plots are written to `training/plots/<dataset>/` (gitignored).

## Dataset Conclusions (captures to date)

The table below comes from `training/overview.py` (KADD-SNR measured in the
0–50 µs window where the crypto operation actually sits):

| file | traces | clip | flat | gain | KADD-SNR (0–50 µs) | verdict |
|------|--------|------|------|------|--------------------|---------|
| `main.h5` | 8028 | 0 % | 0 % | −5 dB | −1.8 dB | usable, lowest signal |
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
- Preprocess: align to the trigger edge, crop to 0–50 µs, band-pass filter,
  per-trace normalization.
- Start with second-order / higher-order features (e.g. adjacent-sample
  products after centering) or ML-SCA targeting the masked S-box output,
  evaluating with train/val/test split by key/nonce.
