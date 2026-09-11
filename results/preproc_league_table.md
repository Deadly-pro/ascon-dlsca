# Preprocessing League Table — Session 1 (Sep 11, 2026)

All methods tested offline on `board_session/pa_assets/profiling.npz`
(5000 random-key traces, 1200 samples, board-verified labels).
Protocol: 80/20 split, per-column HW-class accuracy vs majority floor,
and >floor+5pt column count. Same harness, same gate, no per-method tuning.

## Results (this session)

| Method | Mean acc | Majority floor | Cols >floor+5 | Cost |
|---|---|---|---|---|
| **PLS** (sklearn, 8 comps, supervised cross-covariance) | 21.5% | 37.6% | **0/64** | 20 min |
| **MIA** (histogram/KDE, 32 POIs, 8 bins) | 19.0% | 37.6% | **0/64** | 1.5 min |
| **Product traces** (2nd-order, 40 POIs → top-64 pairs) | 19.4% | 37.6% | **0/64** | 3 min |

Uniform chance = 16.7%. All three land at or near it, far below the
majority-class floor (37.6%).

## Cumulative table — every offline method tried on this capture

| Method | Mean acc | Floor | Cols >floor+5 | Source |
|---|---|---|---|---|
| Raw 1200-sample LDA | 22.5% | 37.5% | 0/64 | step2 |
| Joint 64-head CNN (shared backbone) | 22.8% | 37.5% | 0/64 | step4 |
| PLS (supervised projection) | 21.5% | 37.6% | 0/64 | step6 |
| Product traces (2nd-order) | 19.4% | 37.6% | 0/64 | step6 |
| MIA (histogram) | 19.0% | 37.6% | 0/64 | step6 |
| Haar DWT-4 approximation | 19.1% | 37.5% | 0/64 | step2 |
| SOST POI-32 | 18.3% | 37.5% | 0/64 | step2 |
| Haar DWT-6 | 17.9% | 37.5% | 0/64 | step2 |
| SOST POI-16 | 17.5% | 37.5% | 0/64 | step2 |
| SOST POI-8 | 16.8% | 37.5% | 0/64 | step2 |
| POI spatial average (32/16) | 14.9–15.8% | 37.5% | 0/64 | step2 |
| **Per-trace CPA, HW target** | \|r\| 0.0452 | null 0.0435 | at null | step1 |
| **Per-trace CPA, HD target** | \|r\| 0.0442 | null 0.0435 | at null | step1 |
| **Per-trace CPA, key bits** | **\|r\| = 0.000** | null 0.0435 | **exactly zero** | step1 |

## What this establishes

1. **13 distinct preprocessing/attack formulations now measured, all 0/64
   columns above floor.** Linear (LDA, PLS), nonlinear (CNN, MIA),
   2nd-order (product traces), feature-selection (POI/SOST), and
   fixed-basis (DWT) families are all exhausted at this capture.
2. **The per-trace key-bit correlation is exactly 0.000** — the strongest
   single piece of evidence. The secret is not linearly present per trace.
3. **Board-side contrast (same day):** live fine-tuning on 100 traces
   reached 49.4% mean train accuracy (vs 72% live floor) — yet the
   closed-loop on col 0 CONVERGED to the true hypothesis at posterior 0.997
   in 35 queries, while col 1 (48% profile) diverged to a wrong hypothesis.
   The CNN extracts something the offline statistics cannot see, but at
   100 traces it is too weak to be reliable per column.

## Interpretation

The preprocessing ceiling is real and measured, not assumed. Every method
that reshapes or re-projects the *per-trace* representation lands at uniform
chance. The only signal that has ever produced a verified result on this
platform is the **task-adapted nonlinear profile** (fine-tune + closed loop),
and its limiting factor is **training data per column**, not feature
engineering.

## Artifacts
- `training/step6_preproc_rank.py` — the league-table harness (PLS/prod/MIA)
- `results/step6_mia.json`, `results/step6_acc_*.npz`
- `results/step1_cpa_hd.json`, `results/step1b_null_floor.json`,
  `results/step2_poi_denoise.json`, `results/step2_acc.npz`
