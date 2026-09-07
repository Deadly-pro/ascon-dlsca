HW-vs-HD investigation verdict — Sep 7, 2026
============================================

Lead: user's friend broke GIFT on a board using HW-vs-HD ("Hamming distance /
slope") analysis. Hypothesis: the ASCON PA pipeline labeled static S-box
OUTPUT Hamming weight; CMOS leaks on register TRANSITIONS (HD) or on the
round-1 S-box INPUT register, so the real leak was mislabeled all along.

What was tested (all offline on existing captures + one fresh 0.92 V capture):
  1. HW(sbox_out) vs HD(col_in ^ col_out) vs HW(col_in) per column, raw / d1 /
     d2 traces, split-half with proper max-over-samples null.
  2. "Pure-key" labels (K0_c + K1_c, no nonce dilution) across 64 columns.
  3. Replication across avg32 / avg64 / prof16sc_m32 / crunch_M16 / vprobe_* /
     confirm_hwin (fresh).
  4. Fixed-key discrimination test (main_live + attack-condition reasoning).

RESULT: NO genuine crypto leakage at VCCINT shunt. The apparent
"breakthrough" (up to 64/64 columns with pure-key |r| > p99 on prof16sc_m32,
23/64 on the fresh confirm_hwin) is a MEASUREMENT ARTIFACT:

  * The random-key datasets re-write the KEY BYTES to the FPGA register file
    before EVERY trace (collect_dataset loads key+nonce per trace).
  * The key-write bus leak is enormous: sum-of-keybyte-HW correlates r = 0.60
    (prof16sc_m32 @ sample 621) / -0.57 (confirm_hwin @ sample 161) — by far
    the strongest signal in any trace.
  * The per-column "pure-key" POIs sat at the SAME samples as the key-write
    (confirm_hwin: key-write @161 == col1 keypart POI @161). They were echoes
    of the key load, not the ASCON crypto.
  * When the key is FIXED (the real attack condition), the key-write term is
    constant and vanishes. Fixed-key test (main_live, 3000 traces, 3000
    nonces): per-column true-label max |r| = 0.045-0.065, ALL below the null
    (0.079); all 4 key hypotheses give identical correlations -> no
    discrimination. Rank-1 counts ~37/64 were noise (ties).

So the HW-vs-HD insight is real for GIFT-on-breadboard (key schedule registers
transition every round; HD of consecutive round-key registers leaks) but does
NOT transfer to ASCON-on-CW305-VCCINT: ASCON has no key schedule, the key sits
static in the state, and at whole-FPGA VCCINT the crypto transitions are below
the measurement floor. The friend's setup measured a bare crypto device; the
CW305 VCCINT shunt measures a 100k-gate FPGA where the ASCON core is ~0.1%.

Lesson for any future PA attempt: ALWAYS include a fixed-key control capture.
Random-key captures with per-trace key reload produce a key-write artifact
that masquerades as key leakage. Gate: the leak must survive with the key
held constant (only nonce varying) before calling it crypto leakage.

The PA arm stands closed: no first-order per-trace leakage above floor at
VCCINT, at any voltage 0.88-1.00 V, any model (HW out, HW in, HD), now with
the key-reload artifact explicitly identified and controlled for.
