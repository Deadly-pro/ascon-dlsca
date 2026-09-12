# Offline Experiment Report (Sep 12, 2026) — no board used

Datasets: `run_pa_20260909_{032325,033731,034125}/cfg_g{30,35}_10mhz_clkgen.h5`
— 2138 traces pooled, 5 MHz crypto, 40 MS/s, random keys, **verify 100%**
against the oracle (223/223, 400/400 spot-checked). These are the only large
captures that both have a valid window and reproduce their labels.

All statistics use the project standard: permutation max-statistic null and
Holm correction where multiple hypotheses are involved.

---

## 1. The detectability sweep — granularity from 320 bits down to 1

Everything below is measured inside each round's known window (see §2), with
the traces integrated over one clock cycle (8 samples).

| granularity | predictor | result | verdict |
|---|---|---|---|
| **320 bits/round** | round state Hamming distance | **\|r\| 0.32 – 0.43** | **VISIBLE** |
| 5 bits (one column) | per-column HD, all 64 columns | \|r\| 0.063–0.092 vs null 0.092–0.107 | 0/64, not resolvable |
| 5 bits, aggregate removed | partial correlation | \|r\| 0.053–0.080 vs null 0.088–0.106 | 0/64, not resolvable |
| 1 bit | per-bit switching, 320 bits × 12 rounds | \|r\| 0.068–0.097 vs null 0.091–0.111 | 0/3840, Holm p = 1.0000 |
| 320 bits, joint | ridge stochastic model, 5-fold CV | R² ≈ null in all 12 rounds | no predictive power |

On the stochastic row: the *absolute* held-out R² is negative (≈ −0.19 to
−0.26 against a null mean of ≈ −0.23). That is an artefact of fitting 320
regressors on ~1700 training traces — the model generalizes worse than the
mean regardless of signal. The meaningful statistic is the **difference from
the permutation null**, which is ≈ 0 in every round. Strengthening the ridge,
standardizing features on train-fold statistics, and filtering near-constant
bits all left the comparison unchanged. So: no predictive power, but do not
quote the absolute R² as if it measured anything.

**The aggregate is measurable; nothing smaller than the aggregate is.**

The winner is scattered at every granularity — 12/12 distinct best columns,
11/12 distinct best bits — which is the signature of noise selection, not of
a leaky component.

---

## 2. Round localization — the enabling result

Each round's 320-bit HD correlates with the trace, peaking at:

    round   1    2    3    4    5    6    7    8    9   10   11   12
    sample 110  114  122  130  138  146  154  166  170  178  186  194

Strictly monotonic, **7.85 samples/round** vs `fs/crypto = 8.00` predicted,
**R² = 0.9987**. Replicated at gain 30: 7.89 samples/round, R² = 0.9972,
identical peak samples. 2138 traces, 5 capture runs, 2 gains.

This is what makes §1's finer-grained tests possible at all: it converts a
2000-sample blind search into a 24-sample known window, removing the
argmax-selection artifact and ~2x of the multiple-comparison penalty.

---

## 3. Frequency selection

Butterworth band-pass sweep, aggregate partialled out of both sides before
scoring columns (essential — the 64 column HDs *sum to* the aggregate, so a
raw correlation scores every column significant off that shared component):

| band | aggregate \|r\| | best column \|r\| (partial) | null | cols>null |
|---|---|---|---|---|
| 1.0 MHz | 0.3956 | 0.0749 | 0.0859 | 0/768 |
| 2.0 MHz | 0.5189 | 0.1065 | 0.0921 | 6/768 |
| **3.0 MHz** | **0.6218** | 0.1078 | 0.1114 | 14/768 |
| 3.5 MHz | 0.4638 | 0.0978 | 0.0991 | 4/768 |
| 4.0 MHz | 0.1598 | 0.0945 | 0.0904 | 1/768 |
| 5.0 MHz | 0.1079 | 0.0947 | 0.0991 | 2/768 |
| 8–18 MHz | 0.12–0.19 | 0.085–0.097 | — | ~1–3/768 |

**The aggregate signal peaks at 3 MHz (0.62) — below the 5 MHz clock — and is
weakest exactly at 5 MHz (0.108).** Broadband it was 0.33. So the measurable
crypto energy is concentrated in a 2–4 MHz band, not at the clock fundamental.
That is a concrete, actionable refinement for any future capture or model.

Per-column: **14/768 at the peak band, with best |r| below its own null.**
No band resolves a column.

**A caveat worth recording:** a first version of this sweep scored 295/768
columns "significant" at 3 MHz. That was wrong — the null permuted the column
predictors, which destroys their coupling to the aggregate that the real data
has. Partialling both sides collapsed it to 14/768. This is the same class of
error as the seven documented false positives, and it is the reason the
partial-correlation null is now the default for any per-column test.

---

## 4. Corrections and retractions

- **The sprint was blind.** `--offset 700` is a trigger delay of 17.5 µs at
  40 MS/s (library-confirmed), and the core encrypts in 3.5–8.5 µs. All ~210k
  sprint captures recorded the settling tail after the operation. Std-profile
  ratio: sprint 1.04–1.08 (flat) vs valid datasets 3.0–5.1 (burst at samples
  0–240). Fixed in `collect_dataset.py` — help text corrected, and the value
  is now recorded as `adc_offset_samples`.
- **Retracted:** "the fixed key cancels the key-write artifact." A constant
  predictor has zero variance by construction, so that test could never have
  shown anything. The `|r| = 0.48` key-HW correlation remains unexplained but
  is no longer evidence of a bus artifact.
- **Unusable dataset:** `run_20260827_091330/profiling.h5` (5000 traces) and
  `gain_30/35.h5` have ciphertexts matching their stored keys/nonces under
  **no** convention — 0/5000 across natural/w32rev, all AD/PT lengths, all
  slices, no-scramble and le32-scramble readback, and a 60×60 key/nonce
  cross-grid. The Sep 9/11 files verify 100% by contrast. Nothing supervised
  should be run on the Aug-27 files until this is resolved.

---

## 5. What the aggregate result does and does not establish

**Establishes:** the CW305 VCCINT measurement sees the ASCON round sequence,
resolves it to a specific clock cycle (R² = 0.9987 against the predicted
spacing), and the bulk 320-bit switching correlates at 0.32–0.43 (0.62 in the
3 MHz band).

**Does not establish:** any resolvable single column or single bit. Both sit
at their nulls. If 64 columns contributed independently, one would correlate
at ~`0.40/sqrt(64) ≈ 0.05` — below the ~0.09–0.10 floor. The measured 0.07 is
the null maximum, i.e. consistent with a real ~0.05 component that cannot be
separated.

So the honest claim is: **per-column leakage is present at roughly its
proportional share and sits below the resolvable floor.** The measurement sees
the bulk and cannot decompose it.

---

## 6. Next, in priority order

1. **Board (when available): `--offset 0 --gain 32`**, and band-pass 2–4 MHz.
   Both are now evidenced: the window matters, and 3 MHz beats broadband by
   ~1.9x for the aggregate.
2. **Re-capture at 5 MHz with the correct offset** and re-run §1 — the
   cfg_g* data is only 2138 traces; the sweep is sample-limited, not
   method-limited, at the fine-grained end.
3. **Resolve the Aug-27 label mismatch** — 5000 traces is the best asset if
   it can be recovered.
4. **EM near-field** (separate track) — the only route that changes the
   measurement point rather than the analysis, which is what the evidence
   says is the binding constraint.

## Artifacts added

`training/round_localize.py`, `percolumn_localized.py`, `residual_cpa.py`,
`perbit_localized.py`, `stochastic_profile.py`, `bandpass_columns.py`,
`agg_activity_scan.py`; `results/round_resolved_findings.md`, this file.
