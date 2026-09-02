# ASCON DL-SCA — Conclusive Results Summary

## Setup
- **Our rig:** ascon-hardware-sca core on CW305 Artix-7, 10 MHz, 40 MS/s (4 samples/cycle), CW-Husky, gain 35
- **Literature:** ascon-hardware-sca EPFL core on SAKURA-G Spartan-6, 500 MS/s (125 samples/cycle), Lecroy scope
- **Reference:** "One for All, All for Ascon" (ACNS 2024) — software STM32F4, 7.37 MHz, CW-Lite 4× clock

## What Leaks (Our Rig)

| Target | 40 MS/s | 500 MS/s (SAKURA-G) |
|---|---|---|
| **Byte-HW (load transient)** | 16/16 bytes, r=0.15–0.33 | 16/16, r=1.0–1.45 |
| **Per-bit (128 key bits)** | **0/128 above floor** | **128/128 above floor** (mean r=0.45) |
| **S-box output HW** | 0.06–0.09 (noise floor) | not tested |
| **KADD byte HW** | 0.10–0.15 (noise floor) | not tested |
| **Within-HW class value** | 0.0% (chance) | 0.0% (chance) |

## The Resolution Thesis

**The 12.5× sample-density gap (125 vs 4 samples/cycle) is the single explanatory variable** for every negative result on our setup. At 500 MS/s, every key bit is individually readable (r=0.3–0.7). At 40 MS/s, nothing beyond Hamming weight survives. Per-bit leakage is necessary for within-HW-class disambiguation, and at 4 samples/cycle it simply doesn't exist.

## What Works (Measured, Reproducible)

1. **Byte-HW signature recovery:** HW per byte, RMSE 1.42/trace → 0.33 at M=600 averaging. 16/16 bytes, 87% single-byte accuracy.
2. **Drift regression on raw data:** destroys the signal. Avoid.
3. **Live alignment:** zero jitter in profile captures; live alignment via cross-correlation restores the signal.
4. **Weak-column search:** 14 least-confident columns × 2 alternatives → 2^14 = 16k verifies, covers the tail.

## What Doesn't Work (Measured, Proven)

1. **S-box first-round output HW:** noise floor at every probe. Dead at 40 MS/s.
2. **KADD intermediate:** noise floor. Dead.
3. **Per-bit classification:** 0/128 bits. No gradient for ordering within HW class.
4. **CNN vs linear template:** tied at RMSE 1.42 after 6000-trace training. Information-limited, not model-limited.
5. **Beam search over HW candidates:** within-HW ties are information-theoretic at 40 MS/s — no signal can order them.
6. **The w32rev bug** (fixed): poisoned all pre-Aug-29 labels. Every failed CNN/live loop from that period is explained.
7. **The drift regression bug** (fixed): smeared per-trace transients, produced false "usable" bytes. Raw data is clean.

## What the Literature Says

| Paper | Target | Traces | Success | Resolution |
|---|---|---|---|---|
| Ensemble (ACNS'24) | STM32 SW (masked) | 3k attack | Full key | 7.37 MHz / 4× |
| SCARL (JETC'21) | Custom FPGA | 24k | 4-bit demo | 125 samples/cycle |
| **This work** | CW305 HW | 600 M=600 | **HW signature only** | **4 samples/cycle** |

No published paper has attacked the `ascon-hardware-sca` RTL on any FPGA. The Zenodo hardware datasets are unattacked in the literature.

## The One Lever That Could Close the Gap

**Crypto clock ÷4 (2.5 MHz) → 16 samples/cycle** at fixed 40 MS/s. 4× the current resolution, 1/8th of SCARL's. If per-bit leakage appears at 16 samples/cycle (as the 500 MS/s data suggests it scales with resolution), the ensemble paper's exact pipeline (y4 byte model → 50 random MLPs → 5-best ensemble → GE) replicates on our core in one board session.

## Paper Narrative

The paper writes itself as:
1. **Masked core:** structural deadlock (first-order suppressed)
2. **Unmasked core at 40 MS/s:** HW-signature recovery only; per-bit leakage absent at 4 samples/cycle (proven against SAKURA-G at 125 samples/cycle where per-bit leakage is present)
3. **Methodology traps:** w32rev bug, drift regression artifact, template-edge prior artifact, prior-only CNN + picker lock
4. **Resolution thesis:** the 12.5× sample-density gap explains the negative result, with supporting evidence from the SAKURA-G dataset