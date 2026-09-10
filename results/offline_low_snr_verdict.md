# Offline Low-SNR Verification — Final Verdict (Sep 10, 2026)

Question: can ANY offline per-trace method extract key-bit leakage from the
existing 5,000-trace unmasked profiling capture (`board_session/pa_assets/
profiling.npz`, 5000 unique keys x 1200 aligned samples)?

Answer, established by a four-step verified program:

**NO — per-trace first-order methods are dead on this capture. The SNR
barrier is analog, not algorithmic. Every method that "works" in the
literature was implemented and measured at/below the majority-class floor.**

## Step 1 — CPA, HW vs HD vs key-hyp (`training/step1_cpa_hd.py`)
Non-profiled correlation over all 64 columns x 4 hypotheses x 3 targets:
- `hw` (S-box output HW): best |r| mean 0.0452, max 0.0612
- `hd` (register-transition HD): mean 0.0442, max 0.0648
- `keyhw` (the 2 secret key bits THEMSELVES): |r| = 0.000 — exactly zero

## Step 1b — Null calibration (`training/step1b_null_floor.py`)
- Permutation null (30 perms, labels shuffled): max|r| mean 0.0435,
  p99.9 = 0.0631
- Observed 0.0452 mean is AT the null; observed max 0.0612 is BELOW p99.9
- The 64/64 "rank-1" is the class-prior structure, not per-trace signal —
  keyhw = 0.000 is the clean proof (the secret correlates with nothing)
- Peak samples scatter across the window (median 609, IQR 427-795 of 1200),
  consistent with noise argmax, not a leakage clock cycle
- 57/64 "held-out rank-1" at the argmax sample is an argmax-selection
  artifact (prior-driven; same trap as the paper's trap 1/2)

## Step 2 — POI selection + denoising (`training/step2_poi_denoise.py`)
LDA (pooled covariance, fit on half A, scored on half B, 64 columns):
| method | mean acc | majority floor | cols above floor |
|---|---|---|---|
| raw 1200 samples | 22.5% | 37.5% | 0/64 |
| SOST POI-8/16/32 | 16.8-18.3% | 37.5% | 0/64 |
| POI spatial avg (sqrt-K SNR gain) | 14.9-15.8% | 37.5% | 0/64 |
| Haar DWT-4/6 | 17.9-19.1% | 37.5% | 0/64 |

Linear filters and feature selection cannot raise first-order SNR above
the floor when the underlying per-sample correlation is at null.

## Step 3 — Gaussian templates
Covered by step 2 (LDA with pooled covariance IS the template attack
linearization); redundant as a separate run.

## Step 4 — Joint multi-head CNN (`training/train_joint.py`)
Shared backbone + 64 column heads, 30 epochs: val-acc 22.8% vs 37.5%
floor. Data-sharing across columns does not help either — consistent with
per-column models (28.5% mean val, all below floor).

## Step 4b — M-trace averaging offline: BLOCKED
The capture has 5000 UNIQUE keys — every key appears exactly once — so
same-key averaging groups cannot be formed offline. The averaging lever
requires same-key repeated captures, which is a live-protocol capability.

## What this means for the attack plan

1. The offline profiling capture is a valid SBOX-label dataset but carries
   no per-trace key information at this gain/SNR. No amount of model
   cleverness (CNN/MLP/LDA/POI/wavelet/joint) changes that — measured, not
   assumed.
2. The verified working path remains the board-side one:
   - live on-board fine-tuning: 90.7% vs 72% floor (board-verified)
   - closed-loop separating-nonce attack: 2 bits, 32 queries, posterior
     0.999 (board-verified, fine-tuned profile)
   - M=64 nonce-repetition averaging: rank-1 0.25 -> 0.94 (board-verified)
3. A full-key offline run would require a NEW capture with same-key
   repetition (e.g. 16 keys x 64 nonces x M=16 average = 16k traces) —
   that is a board session, not an offline computation.
4. Paper/poster claims stay as revised: per-column leakage demonstrated
   via the live fine-tuning path; full-key assembly = ongoing work.

## Artifacts
- `training/step1_cpa_hd.py`, `training/step1b_null_floor.py`,
  `training/step2_poi_denoise.py`, `training/step4b_mavg_offline.py`
- `results/step1_cpa_hd.json`, `results/step1b_null_floor.json`,
  `results/step2_poi_denoise.json`, `results/step2_acc.npz`
