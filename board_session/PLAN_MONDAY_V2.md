# PLAN v2 — MONDAY MAX-PROBABILITY LEGITIMATE KEY RECOVERY (Sep 7, final)

Goal: full 128-bit key from the UNMODIFIED official core, public outputs /
traces only, verified against the public-output oracle. The state register
is used ONLY for calibration (cycle map) and the labeled demo — never as
the recovery claim.

Honest odds: this maximizes but cannot guarantee. Estimate after stacking
all levers: 40-55% black-box full key. Guaranteed regardless: submittable
paper (paper_vlsid.tex skeleton done; outcome macros).

## THE FIVE LEGITIMATE LEVERS (all black-box)

L1 CYCLE MAP (instrument as calibration only, 20 min):
    glitch_only hang + repeat stepping; frozen state matched offline under
    the KNOWN calibration key -> exact cycle index of finalization
    round-10 / round-11 / latch. => eo* (round-11 S-box-input cycle).
    Friday's failure was a BLIND scan; this aims every shot.

L2 AIMED FAULT HUNT at eo* (2 h):
    clock_xor at eo* +/- 3, FULL offset sweep, width grid {67, 150, 300},
    many nonces (each nonce redeals faultable transitions), optional
    --vccint 0.92/0.90 (global setup marginality). Every FTL fault with
    tagdiff 5..45 -> localize_fault (known key) -> BANK
    (nonce, eo, off, w, col, bit, faulty_tag) to faults_bank.npz.

L3 MULTI-GLITCH BURSTS (untried, cheap):
    Husky num_glitches up to 32; fire 2-4 glitches at eo*, eo*+1, eo*+2 in
    ONE query -> a fault lands in the round-11/12 window with higher
    probability than single probing. Each burst query still yields ONE
    tag (classify by tagdiff).

L4 M-AVERAGED PROFILING (the untested PA lever, 2 h):
    collect_dataset.py -n 6000 -M 16 RANDOM keys (profiling traces get
    +12 dB at capture; Friday's dead verdict was M=1 profiles).
    -> preprocess -> train per-column + joint -> probe_leakage floor gate.
    Gate: >= 40/64 columns over floor = viable; < 40 = PA contributes
    nothing, rely on L2/L3 columns alone (need >= 52 from FI then).

L5 MIXED ASSEMBLY (the multiplier, offline, minutes):
    Merge banked FI columns (exact bits -> +inf score for the true
    hypothesis, -inf others) with PA scores (64,4) -> fullkey_assemble.
    Bar: FI_cols + PA_confident_cols >= 52 (then <= 4^12 brute force,
    minutes, oracle-verified). Selftest 30/30; mixed-source input is
    scores + we set FI columns' scores ourselves before assembly.

## SCHEDULE (6 h board)

0:00-0:10  GATE: sanity_check 5/5 + diag_extclk all-pass.
0:10-0:40  L1 cycle map (calibration key). Output: eo*. Fallback if hang
           unreadable: blind band eo 28..50 (Friday's map).
0:40-0:50  Bank the demo (glitch_disclose --load-key-random) — the
           labeled threat-model artifact, NOT the headline. 10 min cap.
0:50-2:50  L2+L3 aimed hunt at eo* (offset x width x nonce x vccint;
           bursts interleaved). BANK every localized fault. Success
           metric: distinct columns banked >= 12.
2:50-3:00  Checkpoint: FI columns banked? >=12 -> L4 shorter (n=3000);
           <12 -> L4 full (n=6000, PA must carry more).
3:00-5:00  L4 M-averaged profiling + training + floor gate + finetune +
           scores_export at target key.
5:00-5:20  L5 mixed assembly -> candidate -> verify (live_query fresh
           nonce). PASS = headline claim, full query/fault counts logged.
5:20-6:00  Bank artifacts: faults_bank.npz, attack_scores.npz,
           mixed_scores.npz, verdict file; restore VCCINT 1.0; clean
           console logs for the paper.

## HARD RULES
- Instrument (stateout) reads: calibration + demo ONLY. Any number used
  for the recovery claim must come from tag/ct or traces.
- Every FI fault is banked the moment it localizes — no re-collect later.
- Fixed key 8826d916cdfb21c6c1ff91a761565a70 for calibration/hunt;
  final demo can rotate.
- Gates decide, not hopes: floor gate (L4), column-count checkpoints.
- No fabricated results. Paper macros flip only on verified outputs.

## PAPER MAPPING (paper_vlsid.tex)
- \blackboxtrue  iff L5 verification PASS  (Section 5A)
- \demoonlytrue  iff demo banked, no black box (Section 5B)
- \negativeonlytrue iff nothing (Section 5C barrier analysis)
Sections 3, 4, 6 are outcome-independent: write them Sunday.
