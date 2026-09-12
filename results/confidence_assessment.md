# Confidence Assessment — round-HD signal and the attack plan

Written after a deliberate attempt to falsify the conclusions before building
anything on them. One of the checks found an error in my own recent analyses,
and one of them substantially undercuts the attack plan. Both are recorded
here.

---

## Claim 1 — The ASCON round sequence is present in the trace and is
## temporally resolved. **Confidence: very high (I would bet on it).**

Evidence:

| check | result |
|---|---|
| per-round net-HD peak samples | 105, 113, 121, ..., 192 — **strictly monotonic in round order** |
| fitted spacing vs predicted | 7.85 / 7.89 samples/round vs `fs/crypto = 8.00` |
| fit quality | R² = 0.9987 (gain 35), 0.9972 (gain 30) |
| replication | 5 independent capture runs, 2 gains, 2138 traces |
| peak sample identity | **identical sample positions** across gains and runs |
| interface partialling | survives: 0.1955 → 0.3137 unchanged after removing nonce_hw and key_hw |
| P(monotone order by chance) | 1/12! ≈ 2×10⁻⁹ |

**What could still break it:** the predictor is a function of (key, nonce), and
the interface leaks too. A confound would have to reproduce both the exact
round ordering *and* the exact `fs/crypto` spacing. Nothing known does that.
I consider this established.

## Claim 2 — The observable is the per-round NET state change (the register
## toggle), not combinational layer switching. **Confidence: high.**

| predictor | \|r\| (unsmoothed) |
|---|---|
| net HD (state in → state out) | **0.549 – 0.599** |
| substitution-layer HD | 0.066 |
| diffusion-layer HD | ~0.044 |
| S-box output HW | 0.041 |

The decisive fact is not the magnitudes but the **independence**:

    corr(sbox-layer HD, net HD)  = +0.053
    corr(diff-layer HD, net HD)  = +0.079

The layer HDs are *nearly uncorrelated* with the net HD despite having similar
variance (std 8.5 and 7.8 vs 9.4). So the trace is not tracking "switching
activity" in general — it is tracking the net per-cycle state change
specifically. That is exactly the signature of the state register bank
toggling once per clock, with the faster combinational glitching filtered out
(consistent with the PDN filtering found in the band-pass sweep).

## Claim 3 — The factorable per-column attack recovers the key.
## **Confidence: LOW. The audit did not support this, and my earlier budget
## curve does not apply to it.**

This is the correction. The attack needs the **substitution-layer per-column
HD**, because that is the only quantity that is bitwise across columns and
therefore depends on exactly 2 key bits.

What the data says:

- the substitution-layer *aggregate* HD correlates at **0.066** (round 1, best
  sample in window) against a null of ~0.056-0.074 — **not significant**;
- since the aggregate is the sum of 64 per-column terms, the per-column
  substitution-layer signal is bounded near **0.066/8 ≈ 0.008**;
- and because the substitution-layer HD is nearly **independent** of the net HD
  (corr 0.053), the strong 0.55-0.60 net-HD signal carries **no implication**
  that a factorable signal exists.

**Where my budget curve went wrong.** I derived `rho_col = rho_agg × σ_col/σ_agg`
using the aggregate's variance, then applied it to the substitution-layer
predictor. That transfer is only valid if the two are the same signal at
different granularity. They are not — they are nearly uncorrelated predictors.
**The "131k traces → 100% recovery" figure is therefore not supported for the
factorable attack.** It may still hold for a per-column *net-HD* attack, but
the per-column net HD is **not** factorable: the diffusion layer's light cone
means column *j*'s net toggle depends on S-box outputs at ~11 positions
(~22 key bits), not 2.

## Claim 4 — The full-key objective has a smooth gradient.
## **Confidence: medium-high.**

Simulated at the measured effect size (deterministic objective structure):

    0 bits wrong  0.4163 (+8.94σ)      8 bits   0.2644 (+5.16σ)
    1 bit         0.3901 (+8.28σ)     16 bits   0.1402 (+2.08σ)
    4 bits        0.3398 (+7.03σ)     32 bits   0.0687 (+0.30σ)

1-bit flips are detectable, and the basin is ~16-32 bits beyond which
information is exhausted. The caveat is the same as before: this is a model at
the measured SNR, not a measurement. And a basin of 16-32 bits means a search
needs a seed inside that radius — a cold start (64 bits away on average) has
no gradient.

---

## Errors found in my own recent work

**E1 — Boxcar smoothing was actively harmful.** I had been integrating traces
over one clock cycle (8 samples) before correlating. It monotonically *reduces*
the signal:

| round | none | boxcar 3 | boxcar 8 | boxcar 16 |
|---|---|---|---|---|
| 1 | **0.5492** | 0.5038 | 0.3001 | 0.1722 |
| 2 | **0.5989** | 0.3940 | 0.3075 | 0.1793 |
| 6 | **0.5798** | 0.4010 | 0.4114 | 0.2486 |
| 12 | **0.5457** | 0.4612 | 0.3502 | 0.1985 |

So `agg_activity_scan`, `round_localize`, `percolumn_localized`,
`residual_cpa`, `perbit_localized` and `stochastic_profile` were all run at
roughly **half the available sensitivity**. Their *conclusions* (things at the
null) are not invalidated — a weaker version of a null result is still a null —
but their measured magnitudes understate what is there, and any of them could
flip if re-run unsmoothed. The round localization in Claim 1 was done on
smoothed data and still worked, which is evidence for how strong it is.

**E2 — The "3 MHz band is 1.9× better than broadband" claim is wrong.** The
band-pass sweep measured 0.6218 at 3 MHz against a *smoothed* broadband of
0.33. Against the correct **unsmoothed** broadband of 0.55-0.60, the band-pass
gain is small, not 1.9×. The band-pass result is not useless (0.62 is
marginally the best number seen) but it is not the lever I described.

Neither error was caught by a test; both were caught by re-deriving from the
raw data during this audit. That is an argument for running the audit *before*
the board, which is what happened.

---

## An unexplained observation

The strongest single correlation found anywhere is at **sample 201 (5.0 µs)**,
*after* round 12 (sample 192):

    key_hw     0.6387
    HW(state S0, i.e. the load)   0.4578

Both peak at the same sample. HW(S0) = HW(IV) + HW(key) + HW(nonce), so it is
largely the same signal as key_hw — expected. What is unexplained is *where*
it sits: at the end of the operation, not at the load. It is either the output
register write, the finalization, or a late key/nonce register access. **Not
resolved, and it is the strongest signal in the dataset** — worth chasing.

---

## What this means for the plan

The board run is still the right next step, but **its purpose changes**: it is
no longer "execute a validated attack", it is "establish whether any factorable
signal exists at the trace counts we can afford."

Revised order:

1. **Board: fixed-key, offset 0, M=1 first (512 nonces), unsmoothed.** Measure
   the per-column correlations for *each candidate factorable predictor* —
   substitution-layer HD, S-box output HW, per-column state HW — against a
   proper null. This is the decisive test and it is cheap.
   - Note: per-column state HW only yields `K1[c] + K2[c]` (the sum), ~1.58
     bits/column → ~101 of 128 bits. Useful but insufficient alone.
2. **Only if a factorable predictor clears**, scale M and run the attack.
3. **Otherwise**, the route is the full-key objective with a smooth gradient
   but no cold-start gradient — which needs either a seed from somewhere, or a
   different measurement point (EM probing).

**Bottom line on confidence:** the *measurement* conclusions are solid and I
would defend them. The *attack* conclusion is not, and the specific predictor
it depended on is contradicted by the data. I would not have found that
without this audit, and I would rather report it now than after a 40-minute
capture and a failed attack.

## Artifacts

- `training/confidence_audit.py` — the interface/layer/timing audit
- `results/board_attack_plan.md` — needs revision per above (superseded in
  part by this document)
