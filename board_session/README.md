# Board Session Runbook — 1 hour, new unmasked rprimas core

**Goal**: use one hour of board time to *conclusively* determine whether the new
unmasked ASCON core can be cracked by the linear-template attack, and at what
operating point. Whether it cracks or not, the session produces a decisive
negative or positive result plus reusable data.

**Prepared offline (this session)**:
- `training/edge_vs_m.py` — one-pass live measurement of template edge vs M-averaging
- `live_query.py` / `collect_dataset.py` / `live_loop_transformer.py` — `--crypto-mhz` lever
- `training/live_loop_transformer.py` — retry-fixed M-pooling (`--retries` now = consecutive-flat tolerance)
- `training/template_edge.py` / `offline_template_attack.py` — truth-encoding bug fixed

**Critical known facts (from offline analysis of 3 real sessions)**:
- The M=64 Aug-25 session was actually **effective M≈10** (retry cap bug) — noise
  reduced only 3.2×, not 8×. The retry fix is worth ~2.5× and is now in place.
- New core M=1 edge at gain 55 (clipped): +0.0038 nats. Old core at gain 35: +0.185 nats.
  The core leaks 45× less than the old dataset — gain/clock operating point is everything.
- Hypotheses are well-separated in principle (class spread ≥ 2 for all 64 columns),
  so nonce selection is NOT the bottleneck. SNR is.

---

## The Decision Tree

```
verify_state 5/5 ?
  NO  -> reflash bitstream, retry once, else STOP (board/bitstream problem)
  YES -> continue

gain sweep (30-50) M=1 edge
  best edge < 0.02 nats -> try 5 MHz crypto
      still < 0.02 -> VERDICT: NO LEAK. Core not leaking first-order S-box.
                     (RTL/masking/trigger problem — not an attack problem)
      > 0.02        -> proceed at 5 MHz
  best edge > 0.02   -> proceed at best gain, 10 MHz

edge vs M (M=1..64, one pass)
  edge(M=64) > 0.1 nats and noise_ratio ~1/sqrt(M)  -> attack VIABLE
  edge(M) flat / noise_ratio stuck                   -> averaging broken OR sim artifact

template attack (M=64, 120 queries, 2 episodes)
  full key verified via oracle -> CRACKED (write the bit-match + q-to-crack)
  no crack -> report bit-match trajectory; strong signal => raise M/query budget
```

---

## Phases & Time Budget

| Phase | Time | Command (orchestrated by `run_session.sh`) | Produces |
|-------|------|------|----------|
| 0. Gate | 2 min | `verify_state.py -n 5` | 5/5 observability proof |
| 1. Gain sweep | 10 min | `collect_dataset.py` × 5 gains + `template_edge.py` | edge(gain) table |
| 1b. 5 MHz contingency | 5 min | `collect_dataset.py --crypto-mhz 5` + `template_edge.py` | edge at 5 MHz (only if needed) |
| 2. Edge vs M | 10 min | `edge_vs_m.py --M-max 64 --nonces 30` | edge(M), noise_ratio(M), argmax(M) |
| 3. Profiling set | 3 min | `collect_dataset.py -n 5000` | profiling.h5 (reusable) |
| 4. Attack | 10 min | `live_loop_transformer.py --evidence template --M 64` | crack result + session h5 |
| Summary | 2 min | — | verdict.txt + log |

Total: **~40 min** of board time, leaving slack for trigger-race retries. The
orchestrator `board_session/run_session.sh` runs all of it, logs to
`board_session/run_<ts>/session.log`, and writes a `verdict.txt`.

## Run It

```bash
# one shot, everything (recommended)
bash board_session/run_session.sh

# or manually, phase by phase (see run_session.sh for exact args)
.venv/bin/python verify_state.py -b vivado_ascon/ascon_cw305_top.bit
```

## Reading the Results

- **edge(gain) at M=1**: `> 0.05` is a strong leak, `0.02-0.05` weak but real,
  `< 0.02` effectively no first-order S-box signal.
- **noise_ratio(M)**: should track `1/sqrt(M)` (0.5 at M=4, 0.25 at M=16, 0.125 at
  M=64). If it does NOT, the M-pool averaging is broken (retry logic, alignment).
- **edge(M) growth**: real board averaging should give ~sqrt(M) edge growth. If
  edge(M=1) is already > 0.1, the attack is viable without heavy averaging.
- **attack outcome**: `FULL KEY VERIFIED` = cracked. Otherwise the printed
  bit-match% after 120 queries tells you how close: > 90% means one more
  episode/query-budget would do it; < 50% means the operating point is marginal.

## What Conclusive Looks Like

**Success**: crack one or more keys, verify via oracle, and have the edge-vs-M
curve + profiling set as reusable evidence. Then the paper's "unmasked core is
crackable" claim is backed by the honest on-board number.

**Failure (no leak)**: all gains × both clocks give edge < 0.02 and 5/5
verify_state still passes. That is itself the result: *the bitstream is not
leaking first-order S-box signal — the RTL/synthesis still collapses masking or
the trigger misses the burst*, and it redirects effort to RTL, not to more
attack tuning.

## Gotchas

- **Disk**: check `df -h` first — Omni-RISC VCD dumps have filled the disk before.
- **Do not run the full attack before the gain sweep + edge-vs-M**: the gain
  lever is worth ~45×, the averaging fix ~2.5×. Find the operating point first.
- **`--retries 128`** in the attack: without it the M=64 pool silently degrades
  to ~10 traces (the exact bug that sank the Aug-25 session).
- **sim cannot validate the template attack** (self-consistency problem). Board is
  the only validator — the phase-2 measurement IS the validation.
