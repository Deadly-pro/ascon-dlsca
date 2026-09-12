# Attack Plan v2 — factorable round-1 signal, with corrected arithmetic

Supersedes `board_attack_plan.md`. Written after two corrections from review,
both of which changed the plan.

---

## 0. Corrections applied

**C1 — the generalization was wrong and is replaced.** I previously wrote that
"only quantities depending on *both* key and nonce carry recoverable
information — i.e. permutation-dependent ones, which are exactly the
non-factorable ones." That is self-contradicting, because the proposed 6-bit
predictor is itself a counterexample: it depends on key and nonce (so it has
real per-trace variance under a fixed key) *and* it is factorable, because
round 1's light cone has not yet spread.

**Correct principle:**

> A quantity is attackable under a fixed key iff (a) it varies with the NONCE
> (a key-only quantity is constant and has nothing to correlate), and (b) its
> LIGHT CONE is still narrow enough to enumerate. Both hold only early in the
> permutation, before diffusion saturates the cone. By later rounds condition
> (b) fails — which is why per-column net HD is unattackable there.

**C2 — the margin was computed against the wrong null.** My 2.9x figure used
`null = sqrt(2 ln(64 * W) / N_eff)`, which corrects only for the 64 hypotheses
of a *single* predictor. The family actually tested is up to
`320 predictors x 64 hypotheses x W samples`. Corrected below.

---

## 1. Corrected arithmetic

Measured inputs: aggregate net-HD correlation `rho_agg = 0.55` (unsmoothed,
round 1), `sigma_agg = 8.726`, single toggle bit `sigma = 0.5`.

    rho_toggle = 0.55 * 0.5 / 8.726 = 0.0315

per (word, position) toggle predictor. Family-wise null
`= sqrt(2 ln(family) / N_eff)`:

| predictors | hyps | W | family | N_eff=10k | 32.8k | 131k | 262k | 524k |
|---|---|---|---|---|---|---|---|---|
| 1 | 64 | 25 | 1,600 | 0.82x | 1.49x | **2.97x** | 4.20x | 5.94x |
| 1 | 64 | 5 | 320 | 0.93x | 1.68x | 3.36x | 4.75x | 6.72x |
| 10 | 64 | 5 | 3,200 | 0.78x | 1.42x | 2.84x | 4.02x | 5.68x |
| **320** | **64** | **25** | **512,000** | **0.61x** | **1.11x** | **2.23x** | **3.15x** | **4.45x** |
| 320 | 64 | 5 | 102,400 | 0.66x | 1.19x | 2.38x | 3.36x | 4.75x |
| 320 | 64 | 1 | 20,480 | 0.71x | 1.28x | 2.56x | 3.62x | 5.12x |

**The honest number for the full attack is 2.23x at N_eff = 131,072, not
2.9x.** The 320-predictor family costs us a third of the margin.

N_eff needed for a 3x margin:

| family | N_eff | M=16 | M=64 | M=256 |
|---|---|---|---|---|
| 1 predictor, W=25 | 133,709 | 8,357 | 2,089 | 522 |
| 320 predictors, W=25 | 238,250 | 14,891 | 3,723 | 931 |
| 320 predictors, W=5 | 209,082 | 13,068 | 3,267 | 817 |
| 320 predictors, W=1 | 179,914 | 11,245 | 2,811 | 703 |

**A single predictor is nearly as expensive as all 320** — because the null is
logarithmic in the family size. So there is no cheap "test one predictor
first" escape.

---

## 2. The pilot problem (Addition 1, sized correctly)

The proposed pilot at 5,000-10,000 traces **cannot detect the predicted
signal**:

- if those are **M=1** traces (N_eff = 5k-10k), the margin at the full family
  is **0.61x-0.71x** — below the null *by prediction*. A null result is
  guaranteed and therefore uninformative.
- if they are **M=64** traces, N_eff = 320k-640k and the margin is 3.5x-4.5x —
  well powered, but that is 320k-640k captures (100-200 min), i.e. not a
  cheap pilot.

**The pilot must be specified in N_eff, and in N_eff terms there is no cheap
pilot.** What a small pilot *does* buy is an upper bound: at N_eff = 10,000 the
detection floor is

    rho_min = 0.0315 / 0.61 = 0.052

so a null pilot establishes "no factorable signal above rho ~ 0.05" — a real
result, but a *different* claim from "the predicted 0.0315 is absent." Those
two must not be conflated in the decision rule, or a guaranteed-null pilot will
be misread as evidence against the model.

---

## 3. Revised board plan

**One decisive run, not a pilot plus a run.** Since the cheap pilot is
underpowered and the full run is required regardless, do it once:

    cd /home/deadly-pro/ascon-dlsca
    .venv/bin/python collect_dataset.py \
      --key 0123456789abcdef0123456789abcdef \
      --offset 0 --gain 32 -n 4096 -M 64 -s 2000 \
      -o board_session/attack/A_off0_N4096_M64.h5

    N_eff = 4096 * 64 = 262,144  ->  margin 3.15x at the full 320-predictor family
    ~77 min at the measured 57 captures/s

Preflight (do not skip): attrs show `adc_offset_samples = 0`, std-profile
max/min ratio ~3-5 (not ~1.0), and round peaks reproduce near
samples 105, 113, 121, ... — the same three checks that would have caught the
sprint failure.

**Why 4096 and not 2048:** 2048 x M=64 = 131,072 gives only 2.23x, which is
inside the region where a marginal result is ambiguous. 4096 costs 40 more
minutes and buys a clean 3.15x.

**Note on the null:** `sqrt(2 ln m / N)` is an extreme-value bound that assumes
independent tests. The 320 predictors overlap heavily in their key cones, so
the *empirical* permutation null — permuting traces and maximising over the
entire family — will be somewhat lower and the margin correspondingly better.
The empirical null is the one we pre-register and use.

---

## 4. Pre-registered decision rule

Fixed BEFORE looking at the data, using the empirical permutation null
(max over the full 320 x 64 family, windowed):

| outcome | action |
|---|---|
| max \|r\| clears the family null with margin >= 3 | proceed to joint pooling (BP) then seeded search (steps 3/4) |
| margin 1-3 — **ambiguous, not null** | run belief propagation on the SAME data; do not re-capture hoping for a cleaner number |
| max \|r\| at or below the null | stop. Factorable signal absent above the detection floor. Write up as the negative result alongside the KADD_2/sample-201 finding |

No post-hoc threshold adjustment. If the result lands marginal, the answer is
"ambiguous," not "significant."

---

## 5. Belief propagation (Addition 2 — agreed, second step)

The 320 predictors share key bits in overlapping 6-bit cones, so they are not
independent tests — which is exactly the structure a factor graph handles.
Pooling weak overlapping evidence jointly, rather than requiring any single
predictor to clear significance alone, is standard divide-and-conquer SCA.

Two reasons it is the right second step:
- it is a **single joint statistic**, so it largely sidesteps the family-wise
  penalty that costs the independent-testing route its margin (section 1);
- it uses the redundancy the overlapping cones provide, which independent
  testing discards.

It is real implementation work, so it triggers on *ambiguous*, never as a
substitute for a clean result.

---

## 6. Negative branch, concrete

- **Cleanly null** -> stop. The factorable-signal question is answered "no"
  above the stated floor, with real evidence, and it joins the KADD_2 finding
  in the write-up. Do not capture more chasing a number the pilot ruled out.
- **Marginal/ambiguous** -> BP on the same data. Not a reason to re-run.
- **Clearly significant** -> full-budget attack + seeded search + verify.
- **EM probing** stays a separate Tuesday+ track in all branches; it is not
  the fallback for an ambiguous board result.

---

## 7. Carryover (unchanged)

Permutation max-statistic null; Holm across the full family; the 4-key
invariance gate; **no boxcar smoothing** (E1 — it cost up to 3x); verification
against real ciphertext/tag before any claim is final.

---

## 8. Standing caveat

`rho_toggle = 0.0315` is derived from the proportional-leakage model, not
measured. It successfully predicted the aggregate (0.55 measured), and the
toggle predictor is a genuine component of that aggregate, so the derivation is
better founded than the one I retracted — but it remains a projection. **The
run above is sized to test it, not to assume it.**

## Artifacts

- `training/confidence_audit.py` — the audit that produced these findings
- `results/confidence_assessment.md` — claim-by-claim confidence
- `results/board_attack_plan.md` — superseded by this document
