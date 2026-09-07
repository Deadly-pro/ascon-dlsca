# Runbook: clock-glitch key recovery on ASCON (Friday board session)

References: `GLITCH_PAPER_PLAN.md` (study + full attack plans), `runbook_20260830.md`
(PA pipeline, same conventions). Run from repo root. Board-interactive commands
use board-host python (`python3`, has chipwhisperer+torch); offline work uses
`.venv/bin/python`. **No commits** until told.

---

## Day 0 — BEFORE the board (all offline, do this now)

Everything below is no-hardware and is the actual make-or-break. Do NOT burn
board time on things that can be validated offline.

1. **Write + sim-validate the bit-flip DFA solver** (`training/dfa_bitflip.py`):
   - **DONE.** Implements Nakamura et al. bit-flip-only DFA: round-11 S-box input
     recovery via masked-DDT intersection, key recovered from tag. Validated:
     **15 faults/column (960 total) → 64/64 columns → full 128-bit key**, reliable
     across seeds/keys. Known-column model (matches nonce-misuse: fault injected
     into a specific column, random bit). The dy reconstruction is exact 92.7%,
     subset 7.3% — handled by the paper's 4 masked DDTs.
   - Self-test: `.venv/bin/python training/dfa_bitflip.py --selftest`
   - Real-data path: `.venv/bin/python training/dfa_bitflip.py --faults <npz>`
     (npz needs `correct_tag` (16,), `tags` (N,16), `cols` (N,), optional `bits`).
   - **Open item for the board**: column *identification* from random faults.
     The solver assumes the fault column is known (from glitch calibration).
     Random-column inference needs the paper's 51200-pattern enumeration —
     not implemented. Plan: calibrate glitch (offset,width) → column mapping,
     then group faults by column.
2. **Write the glitch calibration script** (`glitch_cal.py`):
   - J16 high (external clock). `scope.glitch.enabled=True`, `clk_src='pll'`,
     `fpga_vco_freq=600e6`, `output='clock_xor'`.
   - Sweep (offset,width) over the crypto window; classify each capture
     correct / faulty-CT / crash via `fpga_expected`.
   - Trigger from `tio4`, same trigger as capture, so glitch lands at known cycle.
3. **Start the DOM masked build** (P1, highest schedule risk):
   - Vendor `ascon-hardware-sca/hardware/ascon_lwc` v2 into
     `vivado_ascon/rtl_lwc_dom/`.
   - Reuse `ascon_top.sv` if the LWC 1.2.0 port list matches (verify with
     `tb_verify.sv` before building).
   - CHECK the fresh-randomness source (320 bits every other cycle) on CW305 —
     on-chip LFSR ok, external TRNG = blocker to flag. Then `bash build_bitstream.sh`.
4. **Write the SHFA/GF distinguisher** (offline): extend `ascon_ref` with a
   2-share DOM model, simulate share-collapse faults, validate ~34-fault recovery.

**Gates for Friday:** (1) DFA solver passes simulated faults, (2) calibration
script exists, (3) DOM build status known (built / blocked / not started).

---

## Phase G0 — Board gates (20 min)

```bash
# 1. KAT gate: MUST print 5/5.
python3 sanity_check.py -b vivado_ascon/ascon_cw305_top.bit
#    FAIL -> reflash, rerun. Still failing -> STOP (not a software problem).

# 2. Set J16 HIGH (external clock from Husky) and confirm the extclk path:
python3 test_extclk_r.py
#    Should print byte-HW / per-bit r numbers (baseline) AND pass ct_sanity.
#    If ct_sanity fails -> clock not reaching core -> check J16 + 20-pin.
```

---

## Phase G1 — Glitch calibration (1.5-2 h) [UNMASKED CORE, P0]

Goal: find (offset,width) that produces reproducible wrong-CT-but-valid outputs.

```bash
python3 glitch_cal.py --key <known_hex> --sweep 10000 --max-ext-offset 120
```
- Known key K (oracle side) so every output is judged against `fpga_expected`.
- Output: table of (ext_offset, offset, width) → correct/faulty/crash.
- Pick 2-4 (offset,width) in the **faulty window**; verify reproducibility
  (same key+nonce, N=20 repeats → same faulty bytes).

**If no faulty window found** (all correct or all crash):
- Try `output='glitch_only'`, higher `fpga_vco_freq`, and/or slower crypto
  clock (PLL1 5 MHz) to widen the window.
- Log the negative; the paper's fallback is sim-validated DFA only.

---

## Phase G2 — Fault localization + DFA (1-2 h)

1. With K known, compute expected per-round state (`ascon_ref`). For each
   reproducible faulty CT, invert p^6 → identify flipped register(s).
   This maps (offset,width) → (round, bit). Target the last two rounds of p^6.
2. Run the solver:
```bash
.venv/bin/python training/dfa_bitflip.py --key <hex> --faults glitch_faults.npz
```
   - Gather 3-10 injections per fault class → solver → candidate key →
     `LiveQuery.verify_key` on a fresh query.
   - **Success = full key recovered + verified. STOP for the day here and log.**

---

## Phase G3 — Masked DOM (P1, only if P0 succeeded AND DOM build exists)

1. Flash DOM bitstream → `sanity_check.py` 5/5.
2. Re-run G1 calibration (masked core is 2 cycles/round — expect a different
   window; faults of interest: unmasked tag compare, single-share collapse).
3. Feed faulty pairs to the SHFA/GF solver → key recovery.

**If DOM build is blocked** (randomness source / adapter / time): fall back to
simulated share-collapse results from Day-0 item 4. Log as such in the paper.

---

## Day-end report (write to board_session/run_YYYYMMDD_HHMM/verdict.txt)

```
unmasked:   calibration window found?  faulty(offset,width)=...
            reproducible?  DFA key recovered?  verify_key pass?
masked DOM: built?  flashed?  calibration window?  key recovered?
fallback:   sim-DFA pass?  sim-SHFA pass?
```

**Friday minimum win:** full key on unmasked via glitching + verified. That
plus the existing PA-negative = publishable paper (leakage fails, faults break).
**Stretch:** DOM v2 collapse. **Fallback if both slip:** PA-negative + sim-fault
methods paper.
