# Board Attack Plan — full-key recovery from the round-HD signal

**Status: the attack is designed, the budget is derived, the board run is specified.**

---

## 1. The insight

Sprint Run A was `2048 nonces x M=64 = 131,072 captures` under a single key.
That is exactly the configuration this attack needs. It failed for one reason
only: `--offset 700` put the window 17.5 us after the trigger, past the end of
the 3.5-8.5 us encryption. **The experiment was right; the window was wrong.**

## 2. Why the attack factorises

The *full-round* per-column HD does not factorise — linear diffusion rotates
bits within each word, so column c's round switching depends on neighbouring
positions. The **substitution layer** does factorise, because ASCON applies it
bitwise across the 64 positions:

    S'_c = Sbox(S_c ^ RC)          for each 5-bit column c

Column c's switching therefore depends on exactly 5 bits, of which only two
are secret:

    IV[c] (public) , K1[c] , K2[c] (KEY) , N1[c] , N2[c] (public)

With `load_state` packing S[1] = big-endian key[0:8], S[2] = key[8:16]:

    column c's key bits = bit (c%8) of key byte (7 - c//8)
                          bit (c%8) of key byte (15 - c//8)

**4 hypotheses per column, 64 columns, 128 bits. Flipping those two bits
changes only that column.**

## 3. Why it now clears the noise floor

Under proportional leakage the per-column correlation follows from the
measured aggregate:

    rho_col = rho_agg * sigma_col / sigma_agg
            = 0.41 * 1.053 / 8.726 = 0.0495

and the max-over-hypotheses null with 4 hypotheses in a W-sample window is

    null = sqrt( 2 ln(4W) / N_eff )        N_eff = N_stored * M

Measured per-column |r| on the real captures (2138 traces) was 0.063-0.092
against null 0.092-0.107 — i.e. **right at the null, consistent with a real
0.0495 that 2138 traces cannot resolve.** That was the whole problem: not
absent leakage, insufficient trace count.

## 4. The budget curve (simulated at the measured effect size)

    N_eff      null     margin   cols recovered
      2,138   0.0656    0.75x    67.4%
     10,000   0.0303    1.63x    90.1%
     50,000   0.0136    3.65x   100.0%   <- threshold, full key
    100,000   0.0096    5.16x   100.0%
    131,072   0.0084    5.90x   100.0%   <- the Run A configuration
    500,000   0.0043   11.53x   100.0%

**Threshold: N_eff ~ 50,000.**

    Run A configuration (2048 x M=64) = 131,072   ->  5.90x margin

## 5. The board run

One capture, ~40 minutes (measured rate on the sprint):

    cd /home/deadly-pro/ascon-dlsca
    .venv/bin/python collect_dataset.py \
      --key 0123456789abcdef0123456789abcdef \
      --offset 0 --gain 32 \
      -n 2048 -M 64 -s 2000 \
      -o board_session/attack/A_fixedkey_off0_N2048_M64.h5

**Preflight gate (do not skip):** after ~8 traces, confirm
`adc_offset_samples = 0` in the attrs AND that the std-profile max/min ratio
is ~3-5, not ~1.0. A ratio near 1 means the window is still wrong (this is
exactly how the sprint failed silently). `capture_sprint.sh` already has the
clip/flat preflight; add the ratio check.

**Headroom option:** `-M 256` gives 4x more effective N (~2.7 h). Worth it if
the first run's per-column correlations come in below 0.0495.

**For the algorithm-development set** (cheaper, run first if time is short):

    -n 512 -M 1        -> N_eff 512, expect ~60% of columns, partial key

## 6. The attack itself

`training/percolumn_sbox_attack.py` (to be written):

1. Load the fixed-key capture; compute per-column round-1 S-box HD for each
   of the 4 key hypotheses x 64 columns.
2. Correlate each against the trace **inside the known round-1 window**
   (sample 110 +/- 12; do not search all 2000 samples — that is what inflated
   the null before).
3. Take the argmax hypothesis per column -> 2 bits per column -> 128 bits.
4. **Verify against the stored ciphertexts** with `ascon_ref.ascon_encrypt`.
   The h5 files carry `ciphertexts`, so the recovered key can be checked
   end-to-end, not just by correlation margin.

Optional amplification, both already evidenced:
- band-pass 2-4 MHz (1.9x on the aggregate)
- round-window matched filter (integrate the whole cycle)

## 7. Fallback if the per-column attack falls short

The aggregate objective has a **smooth gradient** (measured, section below), so
a full-key search is not the hopeless case the KADD work suggested:

    wrong bits   score      sigma above random
       0        0.4163       +8.94
       1        0.3901       +8.28
       4        0.3398       +7.03
       8        0.2644       +5.16
      16        0.1402       +2.08
      32        0.0687       +0.30    <- information exhausted

1-bit flips are detectable (8.28 vs 8.94 sigma). The basin is ~16-32 bits, so
a search started within that radius converges, while a random start (64 bits
away) has no gradient — meaning the fallback needs a *partial* key seed, not a
cold start. The per-column attack, if it works, provides exactly that seed.

**Retraction:** the earlier "1-bit flip scores like random" finding was about
the KADD objective with a weak profile, not this one. The round-HD objective
is smooth.

## 8. Honest risk

**The budget curve is a model, not a measurement.** It assumes leakage
proportional across columns, which is what makes `rho_col = 0.41 * 1.053/8.726`
valid. That assumption predicted the aggregate correctly (0.41 measured), and
it is physically reasonable (each column's gates contribute their own
switching), but it is not confirmed for the per-column term.

If real `rho_col` is 3x lower than predicted, N_eff must be 9x higher
(~450k -> M=64 with 7000 nonces, or M=256 with 2048). **The first board capture
settles this immediately**: measure the per-column correlations on a small
M=1 set before committing to the long run.

## 9. Order of work

1. **Now (offline):** write `percolumn_sbox_attack.py`; validate it recovers
   the key on simulated traces at the exact predicted SNR, so a board failure
   is unambiguous.
2. **Board, short:** fixed-key M=1, 512 nonces, offset 0. Measure per-column
   correlations -> confirms or kills the model.
3. **Board, long:** the M=64 (or M=256) full run.
4. **Attack + verify** against the stored ciphertexts.

## Artifacts

- `training/landscape_probe.py` — objective geometry (needs a fixed-key
  valid-window capture to evaluate on real data)
- `training/synthetic_landscape.py` — landscape at the measured SNR
- `training/recovery_budget.py` — the budget curve above
- `training/percolumn_localized.py` — the windowed per-column test on real data
