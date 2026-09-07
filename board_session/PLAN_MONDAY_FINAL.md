# MONDAY FINAL PLAN — last board session before Sep 10 (VLSID)

Principle: BANK A PROVEN FULL-KEY ARTIFACT IN HOUR 1, before any gamble.
Everything after is upside. Worst-case exit = guaranteed demo key crack.
Timebox: ~6 h board time. Fixed key: 8826d916cdfb21c6c1ff91a761565a70.
J16 = 1 all day. Runbook: also read runbook_monday.md (same scripts).

=====================================================================
EVERYTHING WE KNOW (evidence-based, as of Saturday)
=====================================================================
PROVEN ON BOARD (Fri):
  * All clock paths work (PLL1 / ext / glitch-module) — original gate failure
    was a host API bug (raw target = stock AES; must use wrap()).
  * Real deterministic finalization faults exist, ct intact:
      eo=31/off=3359/w=67: 1-bit flip, word1 bit27, at finalization ENTRY
        (key-injection stage). 62-bit tag diff. 187/187 identical.
      eo=45: output-latch 1-bit flip (1-bit tag diff). Leaks nothing.
  * Round-11 S-box-input band (DFA-solvable, tagdiff 5-45): EMPTY at w=67
    for the ONE nonce tried, across full offset resolution + all widths at
    eo=44. Faults are data-dependent → nonce is the unexplored dimension.
  * glitch_only mode hangs the core deterministically (we saw it: identical
    garbage tags 2500/2500 = frozen/stale registers).
PROVEN OFFLINE (sim, selftested):
  * state_disclosure: frozen mid-init state + public nonce -> FULL KEY,
    self-verified (IV+nonce check), 40/40. One faulted query suffices.
  * fullkey_assemble: (64,4) per-column scores -> full key via bounded
    brute force + public-output oracle verify. 30/30; needs >=52/64
    confident columns (4^8..4^12 budget, 8s..35min).
  * dfa_bitflip: 15 faults/col -> full key (needs round-11 faults).
  * scores_export: end-to-end 64-column loop -> assemble -> key (perfect
    classifier). Board path ready.
  * offline_model_id: eo=31 fault identified from public tag ONLY.
VALIDITY (checked vs upstream clones):
  * dbg_state -> REG_CRYPT_STATEOUT 0x0e is OUR local addition (official
    ascon-hardware AND ascon-hardware-sca have no dbg/state ports).
  * => state disclosure = instrumented / debug-port threat-model claim.
  * => valid-vs-official claims: FI+DFA (needs round-11 faults) and
    PA+assembly (needs >=52 confident columns).

=====================================================================
RANKED ALTERNATIVES (all considered)
=====================================================================
A. State disclosure (hang + STATEOUT read + invert)   — P(work) ~85%
   Instrumented claim; guaranteed-quality DEMO. Sim 40/40; hang behavior
   board-confirmed; register verified in built bitstream.
B. FI nonce-hunt + vccint for round-11 faults + DFA  — P(full key) ~25%
   The only plausible VALID full break; one config = one column is the
   grind risk (need ~64 configs x 15 faults).
C. PA M-averaging + joint training + assembly         — P(full key) ~15%
   Valid claim; -19 dB single-trace SNR needs M>=16 everywhere; gate at
   floor-check kills it fast if profiles are weak (Friday evidence says
   they will be at M=1; M=16 untested).
D. eo=31 fault + differential-of-entry DFA            — intractable
   (12 rounds of diffusion; no algebraic path). Considered, rejected.
E. EM probe / other hardware                          — not available by Mon.
F. Pure negative-results paper                        — guaranteed but
   weakest; keep as the floor ONLY if A also fails (unlikely).

=====================================================================
THE PLAN (fail-safe ordering)
=====================================================================
HOUR 0 (10 min) — GATE
  sanity_check.py 5/5 + diag_extclk.py all-PASS. Fail -> reflash, retry,
  fail again -> STOP (call me; do not debug hardware blind).

HOUR 0:10-1:00 — BANK THE ARTIFACT + BUILD THE CYCLE MAP (Track A)
  python3 glitch_disclose.py --key 8826d916cdfb21c6c1ff91a761565a70 \
      --nonce 000102030405060708090a0b0c0d0e0f
  * MATCH -> run the attack demo immediately:
    python3 glitch_disclose.py --load-key-random (saves disclose_result.npz)
    => BANKED: full-key recovery demo, one faulted query, verified.
       (Claim = observability/debug-port threat model on OUR instrumented
       build — NOT a break of the official core. It is the demo floor and
       the calibration tool, not the headline.)
  * No match -> widen (--eo-min 0 --eo-max 30, --width 30/150, repeat 5).
    STILL no match -> the run auto-banks disclose_rawdump.npz; mapping is
    fixed offline (calibration key is inside the npz). Move on regardless.

  THEN — A2: BUILD THE eo->STAGE MAP (guided-search calibration, ~20 min):
  The frozen STATEOUT after a glitch_only hang tells us EXACTLY which
  crypto cycle each (repeat, eo, width) config stops on (match offline vs
  forward-computed states under the known calibration key). Use repeat to
  step the core cycle-by-cycle through the finalization; record:
     cycle number of finalization round-10 start / round-11 start / latch
  => eo* = the round-11 S-box-input cycle number. This converts the black-
  box hunt from a 22-cycle blind scan into an aimed shot at 2-3 cycles.
  (This is the legitimate use of our instrumentation: calibrate with it,
  attack black-box. The VALID claim still rides on Track B/C below.)
  Hard rule: cap Track A at 60 min total. Do not debug live beyond that.

HOUR 1:00-1:30 — FI LOTTERY (Track B — now AIMED, not blind)
  If A2 produced eo*: hunt at eo* ± 2 with full offset sweep and multiple
  nonces (the state map aims the shot; nonce+width vary the fault):
  python3 glitch_cal.py --key ... --nonce-hunt 30 --eo-min <eo*-2> \
      --eo-max <eo*>+2 --width 67 --repeat 5 --settle-s 0.03
  (No map -> fall back to the blind band --eo-min 28 --eo-max 50.)
  Any '*** DFA-BAND HIT' (bitdiff 5..45) -> note (nonce, eo, off, w),
  continue hunting 10 more nonces for MORE hits, then go HOUR 2B.
  No hits -> retry once with --vccint 0.92. Still none -> skip to 2A.

HOUR 1:30-2:00 — VCCINT SNR probe (feeds Track C decision)
  set_vccint.py --vcc X --kat + 3x collect_dataset -n 300 -M 16
  --no-program -> snr_sweep.py. Pick voltage only if >= +3 dB over 1.0V.

HOUR 2:00-4:30 — BRANCH (auto-selected by the above):
  2B (if band hits): glitch_collect at each hit nonce+config (count 2000)
      -> localize -> dfa_bitflip. Coverage gate: >=10 distinct columns by
      4:00 else abandon to 2A-continue. Each config = 1 column; hunt
      neighboring (offset,width) at hit nonces for new columns.
  2A-continue (no band hits): PA campaign at best voltage:
      collect_dataset -n 6000 -M 16 random keys -> preprocess -> train
      per-col + joint -> probe_leakage floor gate.
      GATE: >=52/64 columns over floor -> scores_export -> fullkey_assemble
      (minutes of brute force). <52 -> STOP PA, log, do paper writing.

HOUR 4:30-5:00 — VERIFY + BANK EVERYTHING
  * Whichever key came out: live_query.py fresh-nonce verification (PASS =
    paper claim). Save all npz + write verdict file. Restore VCCINT 1.0.

HOUR 5:00-6:00 — PAPER ASSETS (offline, while board still available)
  * Re-run the winning artifact once more for clean logs/numbers.
  * Screenshot-ready console outputs for: disclosure demo, any DFA/PA key,
    fault-model identification (offline_model_id), SNR probes.
  * Final verdict.txt with the claim table + query counts.

=====================================================================
PAPER CLAIM LADDER (what we write, by outcome)
=====================================================================
  1. A + B/C both work: "clock-glitch key recovery on NIST ASCON core:
     black-box DFA full key + observability-based single-fault disclosure"
     — strongest.
  2. A only: "verified FI path, fault localization from public outputs,
     instrument-guided fault placement (cycle map), single-query full-key
     disclosure under an explicit state-observability threat model, +
     sim-validated black-box DFA/assembly pipelines" — honest and
     complete, with the instrument limitation stated plainly.
  3. Nothing works: PA-negative catalog + FI fault-model ID + all four
     sim-validated solvers + methodology-trap documentation. (Floor; only
     if A fails too — unlikely given 40/40 sim + confirmed hang behavior.)
NEVER: fabricate. A wrong key claim kills the paper AND the author.
NEVER present the state-register read as an attack on the official design:
  the port is ours. Valid roles = calibration + explicitly-labeled demo.

Saturday status: all scripts written, parse-checked, selftested (40/40,
30/30, KEY MATCH x2). Zero coding left for Monday. Memory updated.
