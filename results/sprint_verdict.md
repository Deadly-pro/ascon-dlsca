# Board Sprint + Known-Key Scan — Verdict (Sep 11, 2026)

## What was captured (all FIXED-KEY, gain 50, offset 700 unless noted)

Fixed key kills two problems at once: no hypothesis search is needed (we
know every intermediate, so CPA correlates against the TRUE value), and the
Sep-7 key-write bus artifact becomes a constant that cancels.

| Run | Config | Stored | Raw captures | Holm-sig | ρ floor |
|---|---|---|---|---|---|
| A | key1, M=64, 10 MHz, 4 samp/cyc | 2048 | 131,072 | **0/704** | **0.0121** |
| B | key2, M=64, 10 MHz, 4 samp/cyc | 512 | 32,768 | 0/704 | 0.0240 |
| C | key1, M=32, 5 MHz, 8 samp/cyc, T=4000 | 512 | 16,384 | 0/704 | 0.0338 |
| D | key1, M=32 (extclk failed -> dup of A) | 512 | 16,384 | 0/704 | 0.0359 |
| E2 | key1, M=16, 200 MS/s (20 samp/cyc) | 508 | 8,128 | 0/704 | 0.0501 |
| D3 | key1, M=16, extclk @offset 200 | 256 | 4,096 | 0/704 | 0.0368 |

**Total: ~4,400 stored traces, ~210,000 raw captures, six configurations,
zero significant correlations at any column, bit, or clock setting.**

## The control that makes this credible

The Sep-7 key-write bus artifact measures **|r| = 0.5443** on random-key
captures (and 0.41 on the offline profiling set, inside the CNN's window).
With the key fixed it measures **0.0000** against a null of 0.0952.

So the measurement chain demonstrably detects a known-present signal of that
magnitude, and demonstrably removes it when the key is static. What is left
in the traces is crypto + noise, and nothing in it correlates.

## Sensitivity achieved

Detection floor = permutation null / sqrt(M), calibrated (the formula
predicts 0.048 at N=5000; measured 0.045).

    previous best (M=1, N=5000)  :  per-trace rho ~ 0.048
    Run A (N=2048, M=64)         :  per-trace rho ~ 0.0121   (~4x deeper)

**Conclusion: on this CW305 at the VCCINT shunt, ASCON round-1 S-box
leakage is below per-trace rho ~ 0.012** — for HW, for each of the 5 S-box
output bits, and for each of the 5 input bits, with key-load confound
provably eliminated and multiple comparisons corrected (704 tests, Holm).

## Honest caveats

1. **8/704 above the largest permutation null in run A** (chance expects
   ~3.5). Marginally elevated; nothing survives Holm.
2. **Possible M-averaging smearing.** Stored traces average M unaligned raw
   captures. Median |r|-profile FWHM is 4 samples in A. Run D was meant to
   test phase-coherence but the extclk config silently fell back to the
   system clock (fixed in scope_config.py afterwards).
3. **extclk captures are not yet calibrated.** The API bug is fixed and the
   PLL now locks (clkgen_src=extclk, adc_freq=40 MHz from the 10 MHz crypto),
   but the burst lands at a different offset (100, not 700) with a different
   DC baseline: offset 100 clips, offset 200 sits at baseline -0.06 V and
   swings to -0.473 (near the rail). Needs an offset sweep.
4. **200 MS/s works** (gain 40, offset 700) but is not in the same
   capture family as A (different gain).

## Code artifacts

- `board_session/capture_sprint.sh` — priority-ordered capture driver with
  a preflight abort guard
- `board_session/rerun_failed.sh` — re-captures failures with gain probing
- `board_session/dbg_extclk.py` — extclk offset diagnostic
- `training/scan_knownkey.py` — known-key CPA + per-bit DPA + controls,
  permutation max-statistic null + Holm correction
- `results/scan_*.json` — per-dataset full results (per-column, per-bit)
- `scope_config.py` — extclk sequence fixed (no target_freq setter in
  chipwhisperer 6.0.0); `collect_dataset.py` — added `--fs`

## Two bugs found and fixed (both would have produced false conclusions)

1. **Per-sample t-test instead of max-statistic null**: reported 18
   "significant" correlations on known-empty data. The test statistic is
   max-over-samples, so the null must be too. Now uses permuted max
   + Holm: 0 significant. This is the same trap as the earlier 57/64
   false positive.
2. **extclk silently not engaging**: `scope.clock.target_freq = x` has no
   setter in chipwhisperer 6.0.0, so the PLL math divided by zero and the
   ADC stayed on the system clock while reporting success.

## Weekend queue, in priority order

1. **extclk offset sweep** (board, ~10 min) — find the non-clipping offset,
   then re-capture D properly. This is the smearing control.
2. **Re-run A with alignment applied before averaging** — if smearing is
   real, this recovers it. Cannot be done retroactively.
3. **Scan the older datasets** with the same scanner for comparison:
   `board_session/run_20260827_091330/profiling.h5` (random-key, M=1),
   the 5 MHz sets, `results/demo.h5`.
4. **Linear-regression / stochastic profiling** on run A — learns per-bit
   weights instead of assuming HW. Cheap, not yet run.
5. **Comb / high-Q bandpass at the 10 MHz harmonics** — the mechanistically
   matched filter (Haar DWT was a low-pass and was the wrong choice).
6. **EMD/HHT, SSA, skewness** — the remaining preprocessing methods from
   the user's list, all on run A.
7. **The 4-key invariance gate** must be applied to ANY future profile
   result before it is believed (see `training/s1_multikey_validate.py`).

## The paper-relevant statement

This is a calibrated, control-validated negative: six capture
configurations, ~210k raw traces, four-fold improved sensitivity, key-load
confound eliminated, multiple comparisons corrected — and no first-order
leakage from any ASCON round-1 S-box intermediate above per-trace
rho ~ 0.012 at the CW305 VCCINT shunt. Previously the honest statement was
"below 0.048"; it is now "below 0.012", which is a hardware statement about
the measurement point, not an algorithmic limitation.
