# CRACK PLAN — MUST crack a key, no fallback (6 hrs: 10:00-16:00)

Every command is ready to copy-paste. Run in order. Decision branches marked **[→]**.

---

## TEST 0 — Board gate (2 min, non-negotiable)

```bash
# Linux
.venv/bin/python verify_state.py -b vivado_ascon/ascon_cw305_top.bit -n 5
# Windows
.venv\Scripts\python verify_state.py -b vivado_ascon\ascon_cw305_top.bit -n 5
```
**PASS** = `5/5 state readbacks match oracle exactly` → continue.
**FAIL** → reflash bitstream, retry once. Still fail = wrong board/bitstream, STOP.

```bash
# Also confirm the core is byte-exact on KATs (one-line sanity)
.venv/bin/python sanity_check.py -b vivado_ascon/ascon_cw305_top.bit
```
**PASS** = 5/5 KATs match.

---

## TEST 1 — Find the config (15 min)

Run this config grid, 1000 traces each, measure edge. Copy-paste each block, record the edge.

### Config A — PRIMARY: gain 35, extclk (phase-locked, never tested)
```bash
.venv/bin/python collect_dataset.py -n 1000 --samples 1200 --gain 35 --extclk -o Dataset/cfgA.h5
.venv/bin/python training/template_edge.py --h5 Dataset/cfgA.h5 --n 1000 --fit-k 700
```
**Record:** `mean +X.XXXX nats`

### Config B — gain 35, clkgen (baseline)
```bash
.venv/bin/python collect_dataset.py -n 1000 --samples 1200 --gain 35 -o Dataset/cfgB.h5
.venv/bin/python training/template_edge.py --h5 Dataset/cfgB.h5 --n 1000 --fit-k 700
```

### Config C — gain 35, 5 MHz, extclk (more samples/cycle)
```bash
.venv/bin/python collect_dataset.py -n 1000 --samples 1200 --gain 35 --crypto-mhz 5 --extclk -o Dataset/cfgC.h5
.venv/bin/python training/template_edge.py --h5 Dataset/cfgC.h5 --n 1000 --fit-k 700
```

### Config D — gain 30, extclk
```bash
.venv/bin/python collect_dataset.py -n 1000 --samples 1200 --gain 30 --extclk -o Dataset/cfgD.h5
.venv/bin/python training/template_edge.py --h5 Dataset/cfgD.h5 --n 1000 --fit-k 700
```

**[→] Decision:**
- Any config edge > 0.05 → **best config found, go TEST 1.5 then TEST 2 with that config**
- Best edge 0.02-0.05 → collect 5000 profiling at best config, then TEST 1.5 + TEST 2
- ALL edges < 0.02 → **Hail Mary block (TEST 4)** — the core isn't leaking S-box at any config

Record best config as: **GAIN**, **MHZ**, **EXTCLK**(yes/no)

---

## TEST 1.5 — Validate M-averaging works (10 min, saves 2 hrs if broken)

Before burning 90 min on the attack, confirm the retry-fixed M=64 actually averages noise down (~8×). Uses the best config's `.h5` as the template:
```bash
.venv/bin/python training/edge_vs_m.py \
  --profile-h5 Dataset/cfgA.h5 \
  --gain <GAIN> --crypto-mhz <MHZ> [--extclk] \
  --M-max 64 --nonces 30 --out Dataset/edge_vs_m.h5
```
**Read the output table:**
- `noise_ratio_m64 ≈ 0.125` → averaging works, go attack
- `noise_ratio_m64 > 0.3` → averaging is broken (pool not filling) — **fix retries/collection before attacking**
- `edge_m64` should be ~`edge_m1 × 8` (or better) — if it's flat, M-averaging won't help

**[→] If noise_ratio is good → TEST 2. If bad → fix the pool logic first (don't waste the attack time).**

---

## TEST 2 — CRACK ATTEMPT (120 min)

### 2a. Profiling set (only if best edge was 0.02-0.05, else use the cfg .h5)
```bash
# Use the best config's gain/mhz/extclk flags from TEST 1
.venv/bin/python collect_dataset.py -n 5000 --samples 1200 \
  --gain <GAIN> --crypto-mhz <MHZ> [--extclk] -o Dataset/profiling.h5
```

### 2b. The attack
```bash
.venv/bin/python training/live_loop_transformer.py --evidence template \
  --profile-h5 Dataset/profiling.h5 \
  --gain <GAIN> --crypto-mhz <MHZ> [--extclk] \
  --M 64 --retries 128 --integrator naive \
  --episodes 6 --max-queries 120 --save-h5 Dataset/attack.h5
```
6 episodes × 120 queries ≈ 90 min. **Watch bit-match climb.** Stop early if `FULL KEY VERIFIED` appears.

**[→] If no crack after 6 episodes:** go TEST 3.

---

## TEST 3 — Escalation (60 min)

### Option A: M=256 (more averaging)
```bash
.venv/bin/python training/live_loop_transformer.py --evidence template \
  --profile-h5 Dataset/profiling.h5 \
  --gain <GAIN> --crypto-mhz <MHZ> [--extclk] \
  --M 256 --retries 512 --integrator naive \
  --episodes 3 --max-queries 200 --save-h5 Dataset/attack256.h5
```

### Option B: try the other config (esp. 5 MHz if not primary)
```bash
# collect profiling at config C (5 MHz extclk) then attack
.venv/bin/python collect_dataset.py -n 3000 --samples 1200 --gain 35 --crypto-mhz 5 --extclk -o Dataset/profiling5.h5
.venv/bin/python training/live_loop_transformer.py --evidence template \
  --profile-h5 Dataset/profiling5.h5 --gain 35 --crypto-mhz 5 --extclk \
  --M 64 --retries 128 --integrator naive \
  --episodes 4 --max-queries 150 --save-h5 Dataset/attack5.h5
```

---

## TEST 4 — Hail Mary (only if ALL edges < 0.02)

The core isn't leaking S-box at any (gain, clock, phase) config. The one REAL leak found is the **key-register HW popcount** (r=0.44, but only total # of 1-bits — cannot recover bits). Two remaining hardware hacks:

### Option A: gain 40 + extclk (old sweep failed at 40, retry with more retries)
```bash
.venv/bin/python collect_dataset.py -n 1000 --samples 1200 --gain 40 --extclk \
  --max-retry 50 -o Dataset/g40.h5
.venv/bin/python training/template_edge.py --h5 Dataset/g40.h5 --n 1000 --fit-k 700
```

### Option B: 2.5 MHz crypto (adc_mul=16, 16 samples/cycle)
```bash
.venv/bin/python collect_dataset.py -n 1000 --samples 1200 --gain 35 --crypto-mhz 2.5 --extclk \
  --max-retry 50 -o Dataset/g25.h5
.venv/bin/python training/template_edge.py --h5 Dataset/g25.h5 --n 1000 --fit-k 700
```

If either shows edge > 0.02 → collect profiling + attack with TEST 2/3 commands at that config.

---

## Time budget

| Block | Time | Cumulative |
|-------|------|------------|
| 0. Gate | 2 min | 10:02 |
| 1. Config hunt | 15 min | 10:17 |
| 1.5 Validate M-averaging | 10 min | 10:27 |
| 2. Crack attempt | 120 min | 12:27 |
| 3. Escalation | 60 min | 13:27 |
| 4. Hail Mary | 60 min | 14:27 |
| Buffer | — | 16:00 |

## Critical notes
- **extclk** requires the target PLL set FIRST (connect_target does this) — collect_dataset with `--extclk` reprograms automatically.
- **--retries 128** is mandatory for M=64 (else the pool silently degrades to ~10 traces — the bug that sank the Aug-25 session).
- Sim mode does NOT validate the attack (self-consistency problem) — the board is the only validator.
- If verify_state passes but edges are ~0 everywhere, the bitstream is the unmasked core but the S-box simply isn't leaking at this SNR — that's the honest negative result.
