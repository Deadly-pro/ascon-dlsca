# PLAN MONDAY V4 — voltage-first, board-time-minimal (Sep 7, final)

Session: ~3.5 h board (late start). Fixed key 8826d916cdfb21c6c1ff91a761565a70.
Goal: full 128-bit key, UNMODIFIED core, public tag/ct + traces only,
oracle-verified. State port: calibration/demo only — NEVER the claim.

Core idea: ONE 25-min voltage-envelope scan feeds BOTH tracks:
  - V_FI  = lowest KAT-passing voltage (setup-marginality frontier)
  - V_PA  = voltage with most columns over leakage floor (hazard leakage)
The two can differ. Both come from the same scan; no extra board time.

===================================================================
HOUR 0:00-0:10 — GATE (no exceptions)
===================================================================
  python3 sanity_check.py -b vivado_ascon/ascon_cw305_top.bit
  python3 diag_extclk.py
  Both pass -> continue. Reflash once if not, retry, then STOP.
  Check: python3 set_vccint.py --read   (baseline voltage, usually 1.0)

===================================================================
HOUR 0:10-0:35 — PHASE 1: VOLTAGE ENVELOPE SCAN (one paste, ~25 min)
===================================================================
  bash board_session/scan_voltages.sh
  Runs automatically:
    1.00 -> 0.97 -> 0.95 -> 0.92 -> 0.90 -> 0.88 V, each: set + KAT gate,
    then 300-trace M=16 random-key probe capture. Stops descending at
    first KAT fail. Ends with offline preprocess + probe_leakage per
    voltage (LEAKS count), and prints the decision rule.
  READ OUT: V_FI (lowest pass), V_PA (most LEAKS), frontier log.
  If ALL voltages flat (no LEAKS anywhere): PA is dead at every voltage —
  FI becomes the only track, jump to Phase 3 with V_FI.

===================================================================
HOUR 0:35-1:15 — PHASE 2: PA AT THE WINNING VOLTAGE (~40 min)
===================================================================
  python3 set_vccint.py --vcc <V_PA> --kat
  python3 collect_dataset.py -n 4000 -M 16 --gain 35 --no-program \
      -o Dataset/crunch_M16.h5
  .venv/bin/python training/preprocess.py Dataset/crunch_M16.h5
  .venv/bin/python training/probe_leakage.py training/data/crunch_M16.npz
  FLOOR GATE (hard): >= 40/64 columns over floor -> PA arm LIVE.
  < 40 -> PA arm dead: log, go Phase 3 (FI carries the day).

===================================================================
HOUR 1:15-1:45 — PHASE 3: FI AT THE FRONTIER (~30 min)
===================================================================
  python3 set_vccint.py --vcc <V_FI> --kat
  # aimed burst hunt in the finalization band:
  python3 glitch_cal.py --key 8826d916cdfb21c6c1ff91a761565a70 \
      --num-glitches 4 --eo-min 28 --eo-max 50 --width 67 \
      --settle-s 0.03 --output clock_xor
  Readout: any '*** DFA-BAND HIT' (tagdiff 5-45) -> bank (nonce,eo,off,w).
  No hits at V_FI: try --vccint V_FI+0.03 (one notch safer) and rerun.
  (If scan stopped at 0.90: also try 0.90 once — the KAT gate protects.)
  Escalate widths {150, 300} only if eo-band completely empty.

  (parallel, separate shell, no schedule cost) FI columns via DFA:
  for each banked hit config: glitch_collect -> dfa_bitflip -> append
  {col: true_h} to fi_solved.json (2 key bits per column, black-box).

===================================================================
HREE 1:45-2:15 — PHASE 4: PA ATTACK + TRAINING (~30 min, CPU only)
===================================================================
  seq 0 63 | xargs -P 8 -I{} .venv/bin/python training/train.py \
      training/data/crunch_M16.npz --target sbox --column {} \
      --arch mlp --epochs 30
  (models -> training/models/crunch_M16_c{0..63}_sbox_mlp.pt)
  .venv/bin/python training/scores_export.py \
      --npz training/data/crunch_M16.npz --models-dir training/models/ \
      --key 8826d916cdfb21c6c1ff91a761565a70 \
      --nonce <nonce_used_in_capture> --ct-tag <its 20B hex> \
      -o attack_scores.npz
  (scores_export needs the capture nonce+ct_tag; read them from the
   crunch_M16.h5 attributes or use --nonce/--ct-tag from a fresh pair)

===================================================================
HOUR 2:15-2:35 — PHASE 5: MIXED ASSEMBLY + VERIFY (~20 min)
===================================================================
  # pure PA:
  .venv/bin/python training/fullkey_assemble.py --scores attack_scores.npz
  # or mixed (if fi_solved.json exists):
  .venv/bin/python training/merge_scores.py --pa attack_scores.npz \
      --fi-solved fi_solved.json --out mixed_scores.npz
  .venv/bin/python training/fullkey_assemble.py --scores mixed_scores.npz
  -> candidate key hex
  # THE ONLY VALID CLAIM — fresh-nonce oracle verify:
  .venv/bin/python live_query.py --candidate <key_hex>  (or the
  scores_export/selftest verify path if board packed up)

===================================================================
HOUR 2:35-3:00 — PHASE 6: BANK + CLEANUP (~25 min)
===================================================================
  python3 set_vccint.py --vcc 1.00       # ALWAYS restore
  Bank: vscan.log, vprobe_*.h5, crunch_M16.h5, attack_scores.npz,
  fi_solved.json, verdict_v4.txt, all console logs (tee'd)
  If key verified: copy key + query/fault counts into verdict_v4.txt.
  If not: verdict records honest negative + everything banked.

===================================================================
COMMAND MAP (single-line, copy-paste blocks)
===================================================================
GATE:    python3 sanity_check.py -b vivado_ascon/ascon_cw305_top.bit && python3 diag_extclk.py
SCAN:    bash board_session/scan_voltages.sh
SET-V:   python3 set_vccint.py --vcc X.XX --kat
CAPTURE: python3 collect_dataset.py -n 4000 -M 16 --gain 35 --no-program -o Dataset/crunch_M16.h5
PREPROC: .venv/bin/python training/preprocess.py Dataset/crunch_M16.h5
PROBE:   .venv/bin/python training/probe_leakage.py training/data/crunch_M16.npz
TRAIN:   seq 0 63 | xargs -P 8 -I{} .venv/bin/python training/train.py training/data/crunch_M16.npz --target sbox --column {} --arch mlp --epochs 30
EXPORT:  .venv/bin/python training/scores_export.py --npz training/data/crunch_M16.npz --models-dir training/models/ --key 8826d916cdfb21c6c1ff91a761565a70 --nonce <hex> --ct-tag <hex> -o attack_scores.npz
ASSEMBLE: .venv/bin/python training/fullkey_assemble.py --scores attack_scores.npz
MERGE:   .venv/bin/python training/merge_scores.py --pa attack_scores.npz --fi-solved fi_solved.json --out mixed_scores.npz
VERIFY:  .venv/bin/python live_query.py --candidate <key_hex>

===================================================================
DECISION TREE (what to run when — no thinking required on the day)
===================================================================
scan says LEAKS at some V  ->  Phase 2 (PA at V_PA) + Phase 3 in parallel
scan says ALL FLAT         ->  skip Phase 2, Phase 3 at V_FI + blind band
floor gate >= 40/64        ->  PA arm LIVE (Phase 4 attack)
floor gate < 40/64          ->  PA arm dead -> Phase 3 FI carries, then
                                Phase 5 assembles whatever FI got
FI band hits exist         ->  collect + dfa per hit (Phase 3 parallel)
no band hits               ->  Phase 5 on PA scores alone; ladder 2/3 paper
candidate key from assembly->  fresh-nonce verify; PASS = headline
verify FAIL                 ->  ladder 2/3 paper (no key claim)

===================================================================
VALIDITY CONTRACT (unchanged, hard rules)
===================================================================
- Claim sources: public tag/ct + VCCINT power traces ONLY.
- State port reads: calibration/demo only, never in recovery chain.
- FI columns must come from dfa_bitflip on banked PUBLIC-tag faults.
- Fresh-nonce oracle verification is mandatory for any key claim.
- No key claim if PA-confident + FI-certain < 52 columns.
- Never fabricate. Wrong key claims kill the paper and the author.

Honest odds with V4: ladder-1 (black-box key) ~35-45%. The scan buys
real information (V_PA could genuinely raise columns-over-floor), and
the burst-mode FI hunt at the frontier is a real untried lever. The
floor paper is 100% by construction (paper_vlsid.tex macros flip only
on verified outcomes).
