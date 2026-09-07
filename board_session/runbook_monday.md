# Runbook: Monday one-shot full-key session (Sep 7)

Timebox: one board day. Goal: full 128-bit key out of the unmasked NIST core,
verified against the public-output oracle. Three tracks, ordered so the
cheapest/highest-information steps run first and the gates pick the track.

All commands from repo root. Board python = `python3`; offline = `.venv/bin/python`.
Fixed session key: 8826d916cdfb21c6c1ff91a761565a70. J16 = 1 all day.

Pre-flight status (done Fri night): all 5 scripts parse + `--help` under
board python3; selftests green: state_disclosure 40/40, fullkey_assemble 30/30,
dfa_bitflip KEY MATCH, collect_dataset has `-M/--avg-m` + random keys.

## Sunday prep — DONE (Fri night, all selftested)

1. [DONE] `training/scores_export.py`: runs all 64 columns at the target key,
   exports (64,4) scores + oracle pair; selftest recovers the full key
   end-to-end offline (`--selftest`). Board use: `--key <hex> --model-frm
   "training/models/mon_c{col}.pt" --npz training/data/prof_mon.npz --M 16`.
2. [DONE] `set_vccint.py`: set/read core voltage without reflashing, with
   `--kat` gate (restores 1.0 V automatically if the core fails).
3. [DONE] All runbook scripts parse + `--help` under the right interpreter;
   selftests green: state_disclosure 40/40, fullkey_assemble 30/30,
   dfa_bitflip KEY MATCH, scores_export full-chain KEY RECOVERED.
4. Print this file; tape it to the desk.

## Phase 0 — bring-up (10 min, hard gate)

```bash
python3 sanity_check.py -b vivado_ascon/ascon_cw305_top.bit   # MUST be 5/5
python3 diag_extclk.py                                        # all 5 PASS
```
sanity fails -> reflash bitstream, rerun; fails again -> STOP (hardware).

## Phase 1 — disclosure calibration (10 min, capped 15)

```bash
python3 glitch_disclose.py --key 8826d916cdfb21c6c1ff91a761565a70 \
    --nonce 000102030405060708090a0b0c0d0e0f
```
- `RECOVERED KEY ... MATCH` -> instrumented key-out works: run attack demo
  (`--load-key-random`), save disclose_result.npz, note the debug-port caveat,
  CONTINUE (this is a demo, not the paper's main claim).
- No disclosure in 15 min -> dump the raw state, log, move on. Do NOT debug
  live; it's the lowest-value track.

## Phase 2 — VCCINT SNR probe (20 min)

```bash
# three small random-key M-averaged captures, one per voltage
python3 set_vccint.py --vcc 1.00 --kat
python3 collect_dataset.py -n 300 -M 16 --gain 35 --no-program -o Dataset/probe_v100.h5
python3 set_vccint.py --vcc 0.95 --kat
python3 collect_dataset.py -n 300 -M 16 --gain 35 --no-program -o Dataset/probe_v095.h5
python3 set_vccint.py --vcc 0.92 --kat
python3 collect_dataset.py -n 300 -M 16 --gain 35 --no-program -o Dataset/probe_v092.h5
python3 set_vccint.py --vcc 1.00    # restore before anything else
```
(`--no-program` keeps the resident bitstream; set_vccint --kat verifies the
core passes KAT at each voltage and auto-restores 1.0 V if not.)
Then per file: `.venv/bin/python training/snr_sweep.py Dataset/probe_vXXX.h5`.
GATE: pick voltage with best per-column SNR (>= +3 dB over 1.0V to bother).
Restore 1.0 V if no winner. Record numbers in the verdict file.

## Phase 3 — FI lottery ticket (15 min)

```bash
python3 glitch_cal.py --key 8826d916cdfb21c6c1ff91a761565a70 \
    --nonce-hunt 30 --eo-min 28 --eo-max 50 --width 67 --repeat 5 \
    --settle-s 0.03 --output clock_xor
# if zero band hits, repeat at reduced voltage:
python3 glitch_cal.py --key ... --nonce-hunt 30 --vccint 0.92 \
    --eo-min 28 --eo-max 50 --width 67 --repeat 5 --output clock_xor
```
- ANY `*** DFA-BAND HIT` (bitdiff 5..45) -> go Phase 4A (fastest valid key).
- none after both runs -> Phase 4B (PA track).

## Phase 4A — FI track (2-3 h timebox, valid-vs-official claim)

At each band hit (same nonce as the hit!):
```bash
python3 glitch_collect.py --key <hex> --nonce <hit nonce> \
    --ext-offset <eo> --offset <off> --width <w> --count 2000 --output clock_xor
.venv/bin/python training/dfa_bitflip.py --faults glitch_faults.npz   # + localize info
```
Each config yields ~1 column (deterministic fault). Hunt neighboring
(offset,width) at the hit nonce for more columns; need 15 faults/col, 64 cols.
Coverage gate: <10 distinct columns after 90 min -> abandon to 4B (or accept
partial + log honestly). Assemble is NOT needed here — dfa_bitflip solves
columns directly; verify with a fresh query via `live_query.py`.

## Phase 4B — PA track (3-4 h timebox, valid-vs-official claim)

```bash
# 1. profiling capture at the Phase-2 voltage (random keys = shortcut-safe)
python3 collect_dataset.py -n 6000 -M 16 --gain 35 -o Dataset/prof_mon.h5
# 2. preprocess + train per-column AND joint
.venv/bin/python training/preprocess.py Dataset/prof_mon.h5
.venv/bin/python training/train.py training/data/prof_mon.npz --target sbox --column 0 --arch cnn1
.venv/bin/python training/train_joint.py ...        # 64-head joint model
# 3. floor-gate every column (THE gate: need >=52/64 over floor by >=5 pts)
.venv/bin/python training/probe_leakage.py ...
# 4. board finetune at a known profiling key (proven domain-gap closer)
.venv/bin/python training/live_finetune.py --model ... --npz ... --key <prof key hex> --column 0 --ntrain 300 --fresh
# 5. attack: separating-nonce queries at the TARGET key, accumulate (64,4)
python3 scores_export.py --key <target key hex> ...       # Sunday-built adapter
# 6. assemble
.venv/bin/python training/fullkey_assemble.py --scores attack_scores.npz
```
GATES:
- after step 3: >12 columns below floor -> PA cannot finish; STOP, log, paper
  falls back to FI-partial/negative + disclosure-demo story.
- after step 5: check confident-column count; if 52..55 -> expect minutes of
  brute force; if 56+ -> seconds.

## Phase 5 — close-out (20 min, mandatory)

```bash
# whichever track won: verify on a fresh query
python3 live_query.py -b vivado_ascon/ascon_cw305_top.bit --key <RECOVERED hex> --nonce <fresh hex>
```
Write `board_session/run_20260907_*/verdict.txt`: track used, query count,
M, voltage, verification result, time. Save npz artifacts. Restore VCCINT=1.0
if touched.

## Decision tree (one line)
sanity ok -> disclose demo -> SNR probe -> FI lottery -> band hit? 4A : 4B
-> gate passed? finish+verify : log honest negative + fallback story.

## If EVERYTHING fails
The paper still has: PA-negative catalog (thorough), verified FI path +
fault-model identification from public outputs, sim-validated DFA (15 f/col)
+ assembly (30/30), disclosure demo under explicit threat model. That is a
complete, honest methods-and-analysis paper. Do not fabricate a key.
