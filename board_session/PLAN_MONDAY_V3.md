# PLAN v3 — MONDAY LATE/CRUNCHED BOARD, MAX-PROBABILITY LEGITIMATE KEY (Sep 7)

Time available: ~3.0–3.5 h (board late, deadline firm). Goal: full 128-bit
key from the UNMODIFIED core, public tag/ct or power traces only,
oracle-verified. State register: calibration + labeled demo only,
NEVER the recovery claim. Paper (paper_vlsid.tex) is already banking
itself as a floor; this plan maximizes the headline claim.

PRIORITY LADDER (cut from bottom up to fit 3.5 h):
  PA M-averaged capture + profile + train (the only lever with a real
  SNR math floor)        = KEEP, KEEP, KEEP
  Mixed assembly (FI certain + PA confident + brute) = KEEP
  Fresh-nonce oracle verification + verdict         = MANDATORY
  Multi-glitch bursts (cheap, 5 min)                = KEEP
  Aimed hunt at eo* (instrument calibration)        = SHRINK to 20 min
  VCCINT SNR probe                                   = DROP (use 1.0 V)
  Demo banking (instrument demo)                    = DROP (time only)

---------------------------------------------------------------------
CRUNCH SCHEDULE (3.5 h, 0:00 = board-on)
---------------------------------------------------------------------
0:00-0:05  GATE: sanity_check 5/5 + diag_extclk all-pass.
           Fail -> reflash, retry, fail again -> STOP. No debugging.

0:05-0:35  PA CAPTURE (the whole lever in one shot):
             .venv/bin/python collect_dataset.py -n 4000 -M 16 \
                 --gain 35 --no-program \
                 -o Dataset/crunch_M16.h5
           (M=16 average-during-capture = +12 dB; ~30 min wall @ 60/s.
            Random keys, single nonce per trace, valid PA pipeline.)

0:35-0:45  PREPROCESS:
             .venv/bin/python training/preprocess.py Dataset/crunch_M16.h5
             .venv/bin/python training/probe_leakage.py \
                 training/data/crunch_M16.npz
           Probe-leakage = per-column floor gate. KEEP GOING iff
           median top-1 over columns > 1.5x chance (chance = 11.1% for
           6-class S-box HW). KILL iff flat.

0:45-1:45  PA TRAINING + ATTACK (background, non-blocking):
             .venv/bin/python training/train.py training/data/crunch_M16.npz
                 --target sbox --arch mlp --column <0..63>
           All 64 columns in parallel xargs (8 at a time = fits 8-core box).
           Outputs: training/models/crunch_M16_c{0..63}_sbox_mlp.pt +
           per-column val-acc json (consumed by scores_export.py).
           Single-paste command:
             seq 0 63 | xargs -P 8 -I{} .venv/bin/python training/train.py \
                 training/data/crunch_M16.npz --target sbox --column {} \
                 --arch mlp --epochs 30

           0:45-1:25 (parallel)  FI LOTTERY (cheap bursts, no schedule cost):
             python3 glitch_cal.py --key 8826... --num-glitches 4 \
                 --eo-min 28 --eo-max 50 --width 67 --settle-s 0.03 \
                 --output clock_xor --vccint 1.0
           Bursts: 4 glitches/query strafes 4 consecutive cycles; the
           untried L3 lever. ANY tagdiff 5-45 hit -> localize (known key)
           -> bank (nonce, eo, off, w, col, bit) to faults_bank.npz.

1:25-1:35  FLOOR GATE on trained profiles (training/probe_leakage.py).
           KEEP iff >= 40/64 columns over floor. KILL PA arm iff < 40.
           Mixed assembly bar: FI_certain + PA_confident >= 52.

1:35-2:00  PA ATTACK at target key:
             .venv/bin/python training/scores_export.py \
                 --models-dir training/models/crunch/ --npz ... \
                 --key 8826... --nonce ... --ct-tag ...
           Exports attack_scores.npz (64,4) per-column posterior scores.

           (parallel)  FI COLLECTION at any banked hit configs:
             python3 glitch_collect.py --key 8826... --nonce <hit> \
                 --eo <eo> --offset <off> --width <w> -n 2000
           -> dfa_bitflip.py to recover the 2 key bits for that column
           -> append to fi_solved.json {col: true_h}.

2:00-2:20  MIXED ASSEMBLY (the multiplier):
             .venv/bin/python training/merge_scores.py \
                 --pa attack_scores.npz \
                 --fi-solved fi_solved.json \
                 --out mixed_scores.npz
           Output: full candidate key, plus the count of FI+PA confident
           columns that actually combined.

2:20-2:30  FRESH-NONCE ORACLE VERIFY (the only valid claim):
             .venv/bin/python live_query.py --candidate <key_hex>
           PASS = headline (full key, unmodified core, public output only).
           FAIL or empty -> PA/FI didn't combine; honest log + ladder 2/3.

2:30-3:00  BANK: faults_bank.npz, attack_scores.npz, mixed_scores.npz,
           fi_solved.json, verdict.txt; restore VCCINT 1.0; clean console
           logs for the paper. If ladder 2 (no black-box), still bank
           everything: the floor paper is fully written already.

3:00-3:30  (BUFFER) re-run the winning artifact once for clean logs
           + screenshot-ready console output for the paper section.
---------------------------------------------------------------------
WHAT A "NATURAL" KEY MEANS HERE (the validity contract)
---------------------------------------------------------------------
- The recovery claim is sourced from public outputs (tag, ct) and/or
  power traces captured by VCCINT probing. Nothing else.
- The candidate key is verified by re-encrypting a fresh nonce and
  comparing the resulting tag/ct to the board's output (live_query.py
  verify). That's the oracle check.
- The state register (0x0e) is read only during the optional L1 cycle
  map (calibration); its values do NOT enter the recovery chain. If
  the L1 step is dropped, the chain is fully public.
- No locked bit, no partially-revealed state, no debug-port oracle.
- If PA gives N columns and FI gives M columns, with N + M < 52,
  we do NOT claim a key. We log the honest verdict and submit the
  floor paper (ladder 3, already drafted).

---------------------------------------------------------------------
WHAT I AM BUILDING/SANITY-CHECKING TONIGHT
---------------------------------------------------------------------
- [DONE] All scripts parse + selftest (40/40, 30/30, 5/5, KEY MATCH).
- [DONE] `merge_scores.py` mixes FI certain + PA scores (5/5).
- [DONE] Burst mode in glitch_cal (`--num-glitches` + set_burst_eo).
- [DOING NOW] Verify `collect_dataset.py -M 16` works in dry-run on a
  synthetic trace stream (we cannot run with hardware at night).
- [DOING] Confirm `preprocess.py` and `probe_leakage.py` accept M-averaged
  .h5 (each trace is one waveform regardless of averaging depth).
- [DOING] Pre-pull the 64-column training command into a single xargs
  invocation so Monday's PA training starts in one paste.

---------------------------------------------------------------------
HONEST ODDS (Sunday night estimate, late board)
---------------------------------------------------------------------
PA-only path (M=16 capture, all 64 columns, oracle verify):
  - M=16 helps but is not a panacea: ~25-35% full key by M-averaged
    profiles alone on this SNR.
FI-only path (round-11 faults + DFA): unchanged, ~25% (cycle map
  dropped in crunch; bursts help, but no aim).
MIXED assembly: ~35-45% (the multiplier buys 10 pts).
Labeled demo (instrumented): ~85% (dropped from time budget unless
  L1 cycle map runs in 20 min and frees time).

Headline ladder:
  Ladder 1 (mixed-assembly black-box key): 35-45% [vs 40-55% in V2]
  Ladder 2 (floor paper, no headline): 100% by construction
  Ladder 3 (instrumented demo, if time): 85% but only if ladder 1 fails

The -5 pt haircut from V2 -> V3 reflects the dropped VCCINT probe,
the dropped L1 cycle map, and the dropped demo capture window. The
single biggest recovery: if the M=16 PA capture lands clean and the
profiles flip 40+ columns over floor, ladder 1 is in play.
