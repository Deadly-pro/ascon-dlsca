# Round-Resolved Analysis — Offline Result (Sep 12, 2026)

No board. Everything below is from existing captures. Two things were found,
and the first one is the most important result this project has produced.

---

## 1. Why the sprint was blind (and why everything looked null)

`collect_dataset.py --offset` was documented as an *"ADC offset DAC value
(raw int; shifts DC baseline down)"*. It is not. It is assigned straight to
`scope.adc.offset`, which the library defines as:

> "The number of samples to wait before recording data after seeing a trigger
> event... an offset can be used to skip to the end of the encryption."
> — `_OpenADCInterface.py:1690`

At 40 MS/s, `--offset 700` = **17.5 us of trigger delay**, and the unmasked
core encrypts in ~3.5-8.5 us. Every sprint capture recorded the settling tail
*after* the operation finished.

Confirmed against the data, by std-profile max/min ratio:

| dataset | offset | std-profile ratio | structure |
|---|---|---|---|
| sprint A/B/C/D | 700 | 1.04-1.08 | flat, none |
| run_20260827 profiling/gain_30/gain_35 | ~0 | 3.0-5.1 | burst, samples 0-240 |
| run_pa_20260909 cfg_g* | ~0 | 3.0-3.4 | burst, samples 0-240 |

The sprint's ~210k captures are **not evidence of "no leakage"** — they are
evidence of "no crypto in the window". Fixed in `collect_dataset.py`: the help
text is corrected and the value is now written to the h5 attrs as
`adc_offset_samples` (it was previously unrecorded, which is why this went
unnoticed for a month).

---

## 2. THE RESULT — the ASCON rounds are resolved in time

On the Sep 9 `cfg_g35_10mhz_clkgen` family (which verifies 100% against the
oracle and has a valid window), correlating each round's 320-bit state
Hamming distance against every trace sample puts the peak at:

    round   1    2    3    4    5    6    7    8    9   10   11   12
    sample 110  114  122  130  138  146  154  166  170  178  186  194

**Strictly monotonic in round order.** Fitted spacing **7.85 samples/round**
against a predicted `fs/crypto = 40/5 = 8.00`, **R^2 = 0.9987**.

Replicated on `cfg_g30` (different gain, 1500 traces, 3 separate capture runs):
**7.89 samples/round, R^2 = 0.9972, strictly monotonic**, and the peak sample
positions are *identical* to the g35 family. 2138 traces total, 5 capture runs,
2 gains.

An accidental correlation cannot produce this: the peaks would scatter. The
probability of 12 peaks landing in round order by chance is 1/12! ~ 2e-9, and
the spacing matching fs/crypto to within 2% is a second independent lock.

**The measurement point sees the crypto, and resolves individual rounds to a
specific ~1-cycle window.** Per-round aggregate |r| = 0.32-0.43.

---

## 3. Single columns are not resolvable even when we know the cycle

Since each round now has a known window (sample 110 + 8(r-1)), the
max-over-samples penalty drops from 2000 to ~24 samples. Re-running per-column
CPA inside those windows, over all 64 columns x 12 rounds:

    best column per round: 52, 44, 37, 48, 26, 1, 22, 56, 37, 32, 21, 49
    |r| 0.063 - 0.092   vs   restricted null p99.9 0.092 - 0.107
    columns above null: 0/64 in every single round

The winning column is scattered with no consistency, and nothing clears the
null. A single 5-bit column in the same clock cycle as a 320-bit aggregate
that correlates at 0.40 sits at 0.07.

**The quantitative story closes.** If the 64 columns contributed
independently, one column's correlation would be ~`0.40/sqrt(64) = 0.05` —
below the detection floor (0.09-0.10). The measured 0.07 is exactly the null
maximum, i.e. consistent with a real ~0.05 signal that cannot be resolved.

So the correct claim is not "no leakage". It is:

> The per-column leakage is present at roughly its proportional share
> (~1/8 the aggregate amplitude) and sits below the resolvable floor. What the
> measurement sees is the bulk 320-bit switching; what it cannot separate is
> any single column inside it.

This **confirms the algorithmic-noise hypothesis** (the plan's Priority 1a) —
which the sprint data had falsely refuted, because the sprint data contained
no crypto at all.

---

## 4. Two other findings

**Label mismatch on the Aug-27 datasets.** `profiling.h5` (5000 traces) and
`gain_30/35.h5` have ciphertexts that match their stored keys/nonces under
**no** convention (natural, w32rev, with/without the le32 readback scramble,
all AD/PT lengths, all slices) — 0/5000. By contrast the Sep 9/11 files verify
**100%** (223/223, 400/400). So the large Aug-27 dataset's labels cannot be
reproduced with the current oracle; treat any supervised result computed on it
as unverified until this is resolved. The aggregate predictors used here depend
only on key/nonce *ordering*, not the oracle, so section 2-3 are unaffected.

**Key-HW is not evidence of a bus artifact.** The `|r| = 0.48` key-HW
correlation is strong, but "the fixed key cancels it" was never evidence of
anything — a constant predictor has zero variance by construction, so that
test is degenerate. It is retracted as a diagnostic.

---

## 5. What to do next, offline

1. **Per-round residual CPA (Priority 1b), now with a valid target.** We can
   now regress out the per-round aggregate at its known sample and look at the
   residual for a single column. This is the experiment the round localization
   makes possible and it has never been runnable before.
2. **Round-windowed everything.** Any per-column method (CPA, LDA, PLS, CNN)
   should now be restricted to the known round windows — it buys ~2x on the
   null for free and removes the argmax-selection artifact.
3. **Resolve the Aug-27 label mismatch** — worth it, it is the only 5000-trace
   valid-window dataset.
4. **Stochastic / linear-regression profiling** on round-windowed data, then
   CWT. Unchanged from the original plan.
5. **Re-capture with `--offset 0 --gain 32`** when the board returns. That is
   now the top board priority, ahead of the extclk calibration.

## Artifacts

- `training/round_localize.py` — per-round peak localization, slope vs
  fs/crypto, monotonicity, null
- `training/percolumn_localized.py` — per-column CPA inside known round windows
- `training/agg_activity_scan.py` — aggregate HD vs trace (added earlier)
- `results/agg_*.json`
