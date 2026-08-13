# Model Training Workspace

This directory is the staging area for the deep-learning side of the ASCON
DL-SCA project: dataset EDA, preprocessing, feature/label selection, and the
training/evaluation pipeline.

## Scripts

| script | purpose |
|--------|---------|
| `overview.py` | side-by-side health comparison of every `Dataset/*.h5` |
| `eda.py` | per-dataset report: health, alignment, active region, leakage scans, spectrum |
| `preprocess.py` | align, crop to op window, z-score → `training/data/*.npz` with `labels_sbox` (N,64) + `labels_kadd` (N,8) + `ref` (alignment reference for live traces) |
| `labels.py` | vectorized label generators, verified against `ascon_ref.py` (self-test in `python3 labels.py`) |
| `train.py` | train cnn1/cnn2/mlp profile on a target byte/column, 80/20 trace split, accuracy vs chance → `training/results/*.json` |
| `attack.py` | guessing-entropy / key-rank evaluation of a trained profile on the held-out 20 % |
| `adaptive.py` | closed-loop adaptive chosen-plaintext (ACPPA) engine + `--validate` offline premise check |
| `../live_query.py` | board-side single-trace fixed-key capture primitive used by `adaptive.py --attack` |

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
.venv/bin/python training/adaptive.py --validate --npz training/data/main2.npz \
    --model training/models/main2_c1_sbox_cnn2.pt --column 1
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

### Adaptive chosen-plaintext (`adaptive.py`) — validated, result is negative

The closed-loop ACPPA engine exists (`adaptive.py --attack`, needs the board via
`live_query.py`), but the offline `--validate` premise check has already answered
the key question: **there is no exploitable per-trace signal in the round-1
S-box on this masked core**, so adaptive nonce selection has nothing to amplify.

Measured on the held-out 20 % (1831 traces) with the trained sbox profile:

| column | HW-class top-1 | vs chance | key-bits top-1 (ties count against) | per-trace drift E[Δlogp] |
|--------|----------------|-----------|--------------------------------------|--------------------------|
| 1 | 24.5 % | 20 % (4.8σ, real but tiny) | 9.3 % vs 25 % (**below chance**) | **−0.053 (anti-correlated)** |
| 0 | 19.1 % | 20 % (at chance) | 12.2 % vs 25 % (below chance) | −0.0009 |

Root causes, both structural:
1. **Class collisions**: 62 % of random nonces map the true key hypothesis to
   the same HW class as another hypothesis → a single trace cannot separate
   them (identical score). The separating-nonce heuristic *does* fix this
   (col 0 reaches sep=4, col 1 is capped at sep=3 by the S-box truth table),
   yet sep=4 traces still rank the true key at chance (23.1 % vs 25 %) — so
   collisions were never the binding constraint.
2. **No drift**: per-trace `E[logp_true − logp_other]` is ≤ 0, so accumulating
   evidence over more traces drives the posterior *away* from the true key, not
   toward it. The masking (d=1, 2-share) genuinely suppresses the first-order
   S-box intermediate; the residual HW-class signal is real but far too weak to
   convert into key-bits rank.

**Conclusion for the writeup:** the masked core defeats the standard profiled
S-box key-recovery attack (offline GE at chance, adaptive adds nothing), which
is the expected security property. The KADD intermediate is the only real leak
(~2× chance, all 8 bytes) but depends on the full 128-bit key, so it cannot be
factorized into a per-byte key rank. `adaptive.py` remains wired for a board
session, but its offline verdict should be treated as the result, not a setup
step to be re-run.

### Unmasked core (d=0 bitstream) — first-order leakage returns

With the unmasked `ascon_cw305_top.bit` (sanity check 5/5 on hardware), fresh
captures `Dataset/main_unmasked.h5` + `main_unmasked_b2.h5` (merged, 6243
traces, gain −2 dB, adc offset 700, samples 2000) show the masking was doing
its job:

| target | masked (main2) | unmasked (merged) |
|--------|----------------|-------------------|
| S-box val top-1 (chance 11.1 %) | ~11 % (at chance) | **28–35 % (2.5–3×)** |
| KADD byte 3 val top-1 | 1.9× | 2.3× |
| KADD-SNR | 1.6 dB | **2.5 dB** |
| S-box SNR peak | −23 dB | −19 dB (sample 1108) |

The unmasked S-box leaks (real, generalizing, several sigma above chance) but
still too weakly for **single-trace** ACPPA discrimination: the live
`adaptive.py --attack` converges in 6–16 queries with posterior 1.000 yet on
the **wrong** hypothesis — the CNN overfits (95 % train / 30 % val on 3.7k
traces) and its majority-class bias locks the loop onto hyp 3. Root causes:
weak S-box SNR (−19 dB) + insufficient trace count for a generalizing profile.

### Virtual-board study (`sim_board.py`, `training/sim_sweep.py`) — no hardware

To turn "the loop converges only above some SNR" into a measured result, the
noise + leakage model is fitted from the real unmasked capture
(`sim_board.py --self-test`; amp=1 reproduces the measured S-box SNR within
2 dB, ADC rail, DC drift, jitter and lag-5 noise color included) and exposed
through the same `query(nonce)` interface as `live_query.py`, so the identical
loop code runs against it:

```bash
# fit + self-check (amp=1 must match the real capture's SNR)
.venv/bin/python sim_board.py Dataset/main_unmasked_merged.h5 --column 0

# SNR threshold experiment: profile trained on sim data, attacked on the
# virtual board at each amp (1 = real SNR; higher = stronger leakage)
.venv/bin/python training/sim_sweep.py --amps 1 2 4 8 16 --ntrain 3000

# or, a single closed loop against the virtual board
.venv/bin/python training/adaptive.py --attack --sim \
    --npz training/data/sim_a8.npz \
    --model training/models/sim_a8_c0_sbox_cnn1.pt --column 0 \
    --key 000102030405060708090a0b0c0d0e0f --sim-amp 8.0
```

Verified so far: amp=1 false-converges exactly like the real board (hyp 3,
wrong) — cross-validating the sim against hardware; amp=8 with a sim-trained
profile converges correctly (hyp 0, right key bits) in ~10 queries.

**SNR threshold (seed-averaged, `training/results/sim_sweep.json`):**

| amp (leakage vs real) | profile HW-class val | attack correct (5 seeds) |
|-----------------------|----------------------|--------------------------|
| 1× (real, −19 dB) | ~79 % | 0/5 — always locks onto hyp 3 |
| 4.5× (+13 dB) | ~74 % | 0/5 |
| 6× (+16 dB) | 50 % | 3/5 (transition) |
| 8× (+18 dB) | ~93 % | **5/5** |
| 16× (+24 dB) | ~98 % | 5/5, converges in 6 q |

**Paper result:** reliable profiled ACPPA key recovery on the round-1 S-box
requires the leakage ~8× stronger (+18 dB) than this core emits. The unmasked
core's −19 dB S-box SNR sits ~18 dB below the threshold, so even unmasked the
adaptive loop converges to the *wrong* key bits with posterior 1.0 — the
profile's class prior dominates when the per-trace signal is that weak.
Masking removes the first-order signal entirely (chance), which is the expected
security property.

### Full-key KADD ACPPA (`training/kadd_acppa.py`) — measured result

Built the full-key attack the user's loop design requires: 8 per-byte KADD
profiles (mlp, 21.6–24.1 % val vs 11.1 % chance — KADD leaks, ~2× chance per
byte), a beam-search ACPPA loop that scores candidate full keys by their
predicted KADD HW vector per trace, and ciphertext-verified termination.

**Per-trace evidence (sim gate, real SNR, amp=1):** the true key scores
+3.1 nats/trace above random keys and is top-1 among 8 candidates 62 % of the
time (chance 12.5 %) — the KADD signal is genuinely discriminative.

**But the beam search cannot find the key (300 queries, 0/16 bytes):**
1. **Not factorable.** KADD byte 0 depends on all 16 key bytes (verified) —
   no per-byte divide-and-conquer.
2. **No gradient.** A 1-bit flip of the true key scores like a random key
   (−716 vs −773, overlapping) — 12 rounds of diffusion scramble the HW
   vector completely, so there is no local structure to hill-climb.
3. **2^128 search.** A random 512-key beam has probability ~2^-119 of
   containing the true key; mutation can't bridge the gap without a gradient.

**Verdict:** on this capture SNR, full 128-bit d=0 recovery via ACPPA is not
achievable — the only strong target (KADD) is not searchable, and the only
searchable target (round-1 S-box, 2 bits/column) is 18 dB too weak (proven on
board + sim). The blocker is **analog SNR, not training or algorithm**.
Path forward: the hybrid enumeration design (rank S-box-column candidates by
KADD evidence) or a real probe on the FPGA core supply for the missing ~18 dB.

### Live on-board training (`live_finetune.py`) — Scheme A

Instead of (or in addition to) the virtual board, the profile can be
**fine-tuned live on the board**: capture traces at a KNOWN key with random
nonces, label them exactly via the oracle (key is known in the lab, so labels
are exact, not hypothesized), and fine-tune the pretrained profile on
(live_trace, exact_label) pairs. This adapts the profile to the device's true
noise/leakage shape and to the board's live trace distribution.

```bash
# 1. fine-tune on the board at a known key (board required)
.venv/bin/python training/live_finetune.py \
    --model training/models/main_unmasked_merged_c0_sbox_cnn1.pt \
    --npz training/data/main_unmasked_merged.npz \
    --key 000102030405060708090a0b0c0d0e0f --column 0 \
    --ntrain 300 --epochs 20 --lr 1e-4 \
    --out training/models/main_unmasked_c0_liveft.pt

# 2. attack a FRESH key with the fine-tuned profile (board required)
.venv/bin/python training/adaptive.py --attack \
    --npz training/data/main_unmasked_merged.npz \
    --model training/models/main_unmasked_c0_liveft.pt \
    --column 0 --key <NEW-16-BYTE-HEX> --max-queries 500
```

Design notes (verified on the sim board):
- **Random nonces for training, separating nonces for attack.** Random nonces
  spread the true HW class across traces (labels are diverse, the model can
  learn all classes). Separating nonces collapse every training label onto a
  single class for a fixed key — useless for training, but exactly what
  amplifies the posterior during the attack.
- Preprocessing and features are identical to the attack path
  (`Profile.preprocess` + `build_input`), and the checkpoint format matches
  `train.py`, so `adaptive.py` / `attack.py` load the fine-tuned model
  unchanged.
- End-to-end verified on the sim board: fine-tune at K1 → attack fresh K2 →
  converges to the correct key bits.
- `--sim` flag exercises the identical loop against `SimBoard` (no board
  needed) for validation.
