# ASCON-128 DL-SCA on CW305

Deep-learning side-channel analysis of a masked (d=1, 2-share) ASCON-128 hardware core on NewAE CW305 + ChipWhisperer-Lite. Python capture/training pipeline with SystemVerilog RTL and Vivado bitstream build.

## Project

- **Target**: NewAE CW305 (Artix-7 XC7A100T-FTG256) running `compact-yet-fast-ascon` threshold-implemented ASCON-128
- **Scope**: ChipWhisperer-Lite, 40 MS/s, `clkgen_x4`, trigger on `tio4`, crypto clock 10 MHz on PLL1
- **Stack**: Python 3 (3.12 for training venv) · `chipwhisperer==6.0.0` · numpy/h5py/matplotlib/scipy · torch (CPU) + scikit-learn for training
- **RTL**: SystemVerilog (`vivado_ascon/rtl/`) + Verilog wrappers (`vivado_ascon/fpga/`) · Vivado 2026.1
- **Entry**: `sanity_check.py` (board-level KAT), `collect_dataset.py` (capture), `live_query.py` (single-trace adaptive), `sim_board.py` (virtual board), `training/` (DL pipeline)

## Commands

```bash
# Setup (two separate venvs)
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
python3.12 -m venv .venv && .venv/bin/pip install -r training/requirements.txt

# Oracle self-test (no hardware)
python3 verify_oracle.py

# Board sanity check (bitstream + KAT + one verified capture)
python3 sanity_check.py -b vivado_ascon/ascon_cw305_top.bit
.venv/bin/python check_setup.py -b vivado_ascon/ascon_cw305_top.bit

# Pre-collection gain calibration (auto-detects Husky vs CW-Lite)
python3 pick_gain.py -b vivado_ascon/ascon_cw305_top.bit

# Pre-collection gain calibration
python3 pilot_gain.py -b vivado_ascon/ascon_cw305_top.bit

# Collect dataset
python3 collect_dataset.py -n 1000 -o Dataset/run.h5

# Dataset overview (compare all .h5 files)
.venv/bin/python training/overview.py

# EDA report
.venv/bin/python training/eda.py Dataset/main2.h5

# Analyze
python3 view_dataset.py Dataset/demo.h5 --outdir results/

# Training pipeline
.venv/bin/python training/preprocess.py Dataset/main2.h5
.venv/bin/python training/train.py training/data/main2.npz --target kadd --column 3 --arch mlp
.venv/bin/python training/attack.py training/data/main2.npz --model training/models/... --target kadd --column 3

# ACPPA offline validation (no board)
.venv/bin/python training/adaptive.py --validate --npz training/data/main2.npz --model ... --column 1

# ACPPA against virtual board (no hardware)
.venv/bin/python training/adaptive.py --attack --sim --npz ... --model ... --column 0 --key <hex> --sim-amp 8.0

# Virtual board self-test (fit from capture, verify SNR match)
.venv/bin/python sim_board.py Dataset/main_unmasked_merged.h5 --column 0

# SNR threshold sweep (sim)
.venv/bin/python training/sim_sweep.py --amps 1 2 4 8 16 --ntrain 3000

# Live on-board fine-tuning
.venv/bin/python training/live_finetune.py --model ... --npz ... --key <hex> --column 0 --ntrain 300

# Full-key KADD beam-search ACPPA
.venv/bin/python training/kadd_acppa.py --model-dir training/models/kadd/ --npz ... --key <hex> --max-queries 300

# Bitstream rebuild (25-45 min, Vivado)
bash build_bitstream.sh
```

## Architecture

| Module | Role |
|--------|------|
| `ascon_ref.py` | NIST SP 800-232 ASCON-128 byte-exact reference oracle + `fpga_expected()` |
| `scope_config.py` | Scope/target auto-detect (CW-Husky vs CW-Lite/Pro) + clock setup; single source of truth for capture hardware |
| `check_setup.py` | One-shot bring-up check for new machines: library, scope, bitstream, register map, verified capture |
| `cw305_ascon_shim.py` | Maps CW305 FPGA register API → masked-core register layout (`wrap(target)` → `AsconMux`) |
| `sanity_check.py` | 5 KAT vectors, byte-exact FPGA vs oracle |
| `pilot_gain.py` | Pre-collection hardware calibration: gain sweep, ADC sync, clock verify |
| `collect_dataset.py` | Synchronized capture with per-trace oracle verification + clip/flat filters → HDF5 |
| `live_query.py` | `LiveQuery` class: one fixed-key, per-query capture (used by ACPPA loop) |
| `sim_board.py` | Virtual CW305: noise+leakage model fitted from real captures, same `query(nonce)` interface as `LiveQuery` |
| `view_dataset.py` | SNR/NICV/alignment/spectrum HTML EDA report |
| `verify_oracle.py` | Offline oracle self-test + batch perf |
| `training/train.py` | CNN/MLP profile training (cnn1/cnn2/mlp), 80/20 split, HW label |
| `training/attack.py` | Guessing-entropy / key-rank evaluation |
| `training/adaptive.py` | Closed-loop ACPPA engine (`--validate` offline, `--attack --sim` virtual, `--attack` real board) |
| `training/kadd_acppa.py` | Full-key beam-search ACPPA on KADD intermediate (8 per-byte profiles, 16-byte key search) |
| `training/live_finetune.py` | Live on-board profile fine-tuning at known key + random nonces (`--random-keys` spreads the true-HW class over the column's full support — a fixed key collapses onto a key-dependent subset like {3,4}, which is why the full-key attack locked hyp 1) |
| `training/sim_sweep.py` | SNR threshold sweep against virtual board |
| `training/snr_sweep.py` | Per-column SNR sweep on real captures |
| `training/overview.py` | Side-by-side health comparison of all `Dataset/*.h5` files |
| `training/eda.py` | Per-dataset EDA report (health, alignment, active region, leakage scans) |
| `training/labels.py` | Vectorized label generators (`round1_sbox_hw`, `kadd_words_hw`, `hypothesis_labels`), self-test against `ascon_ref.py` |
| `training/preprocess.py` | Align → z-score → crop → `training/data/*.npz` |
| `vivado_ascon/rtl/` | Masked ASCON core: `ascon_top.sv`, `datapath.sv`, `fsm.sv`, `ascon_sbox_d2.sv`, LFSR, shares |
| `vivado_ascon/fpga/` | CW305 wrapper: `cw305_top.v`, `cw305_reg_ascon.v`, `cw305_usb_reg_fe.v`, `clocks.v`, `cw305.xdc` |

## Conventions

- **Shebang**: `#!/usr/bin/env python3`
- **Docstrings**: `r"""…"""` raw strings at module top and on classes
- **CLI**: `argparse` throughout; `-b/--bitstream` defaults to `vivado_ascon/ascon_cw305_top.bit`
- **Entry guard**: `if __name__ == '__main__': main()`
- **Naming**: `snake_case` for functions/vars/files, `PascalCase` for classes (`LiveQuery`, `AsconMux`, `SimBoard`)
- **FPGA interface**: `target.fpga_write(addr, list_of_bytes)`, `target.fpga_read(addr, count)`
- **Shim pattern**: `t = wrap(target)` returns `AsconMux` with `loadEncryptionKey`/`loadInput`/`go`/`readOutput`
- **ASCON oracle**: `ascon_encrypt(key, nonce, ad, pt)` → `ct+tag` (20 bytes); `fpga_expected(key, nonce)` → register readback (16 bytes: tag[:12] + ct[:4])
- **Training**: Separate `.venv/` with CPU torch; `.npz` features in `training/data/` (gitignored); models in `training/models/` (gitignored)
- **Vivado**: `build_bitstream.sh` runs `vivado -mode batch -source build_ascon_cw305.tcl`; logs to `vivado_ascon/build_logs/`

## Two target types

| Target | Classes | Depends on | Used for |
|--------|---------|------------|----------|
| `sbox` (round-1 S-box output per column) | 6 (HW 0–5) | 2 unknown key bits per column | Key rank (4 hypotheses) |
| `kadd` (S[3] ⊕ key[0:8] after 12-round init, per byte) | 9 (HW 0–8) | Full 128-bit key | Intermediate recovery (not factorable) |

The S-box target is factorable per-column (2 bits → 4 hypotheses) but the masking suppresses it to chance. The KADD target leaks ~2× chance but cannot be factorized into per-byte key rank — it depends on all 16 key bytes via 12 rounds of diffusion.

## Training results & verdicts

**Masked core** (`main2.h5`, 9151 traces, gain −5 dB):
- S-box: at chance across all architectures. The masking (d=1, 2-share) works.
- KADD: ~2× chance (MLP with centered products, 21.6% vs 11.1%), all 8 bytes. Real, generalizing leakage on held-out random keys.
- ACPPA offline `--validate`: no exploitable per-trace S-box signal. Per-trace drift E[Δlogp] ≤ 0 (anti-correlated). 62% class collisions. Masked core defeats profiled S-box key recovery.

**Unmasked core** (`main_unmasked_merged.h5`, 6243 traces):
- S-box: 2.5–3× chance (28–35% top-1), real first-order leakage returns. But SNR still only −19 dB.
- ACPPA on real board (board-finetuned profile, posterior scoring, M=1): converges to the **correct** 2 key bits, posterior 0.999, 32 queries (key `0f1e…`, true hyp 3). The earlier "wrong convergence / class prior dominates" verdict was an arithmetic misread (key byte 1 vs byte 8).
- Sim (amp=1, real-board profile): correct in 8–16 queries, reliable across seeds. The sim_sweep "amp ≥ 8×" threshold applies to sim-trained profiles, not the real-board profile — the blocker was the profiling-domain gap, not analog SNR.
- M=64 nonce-repetition averaging (`adaptive.py --M 64`): q15 → q9 convergence, plus Phase 0 rank-1 0.25 → 0.94.

**Full-key KADD beam search** (`training/kadd_acppa.py`): true key scores +3.1 nats/trace above random keys, but beam search cannot find it. KADD not factorable per byte, no gradient (1-bit flip scores like random), 2^128 search space. Blocker is analog SNR, not algorithm.

**Key architectural insight**: on the masked core the deadlock holds (S-box untrainable, KADD unsearchable). On the unmasked core the S-box target IS attackable — the real blocker there was the profiling-domain gap (sim-trained profiles), not analog SNR: a board-finetuned profile recovers correct bits at amp=1.

## Hardware Notes

- **Husky**: the capture scope may be a CW-Husky (replaces CW-Lite). All scope
  scripts call `setup_scope_clock()` from `live_query.py`, which uses
  `clkgen_src='system'` + `adc_mul=1` on Husky (the legacy
  `adc_src='clkgen_x4'` maps to `adc_mul=4` = 160 MS/s, breaking timing).
  Husky gain range -15..+65 dB. Bring-up/runbook: `HUSKY_SETUP.md`.
  Pre-Husky backup: `backup_pre_husky/`.
- `training/active_loop.py`: unified closed loop — model picks each nonce
  (posterior-aware separating selection), online-trains on the trace
  (replay buffer), guesses the key; epoch ends on `--stable-n` repeats of the
  same guess at posterior > `--converge-p` OR `--max-traces`. Random key per
  epoch (oracle labels); `--attack-key` switches to real attack mode.
- CW305 register map: KEY=0x0a, TEXTIN=0x06, NONCEIN=0x0d, CIPHEROUT=0x09, TAGOUT=0x0c, TEXTIN_BUF=0x12, VALID_AD=0x10, VALID_MSG=0x11
- `REG_CLKSETTINGS=0x19` enables `tio_clkout` (needed for `extclk_x4` mode, set in `live_query.py`)

## SimBoard (`sim_board.py`)

Virtual board implementing the same `query(nonce) → (trace, ct)` interface as `LiveQuery`:

**Generation model**: `trace(t) = mu(t) + amp * alpha(t) * (HW − E[HW]) + sigma(t) * noise(t) + drift + jitter`

Parameters: fitted from a real `.h5` capture (mean mu, per-sample leakage template alpha, residual noise sigma, DC drift distribution, alignment jitter histogram, lag-5 noise color from residual ACF). `amp` knob scales leakage strength (1 = real SNR).

- `--self-test` verifies that amp=1 reproduces measured SNR within 2 dB
- Targets both `sbox` and `kadd` (multi-byte alpha profiles)
- **`target='sbox64'`** (added Aug 21): fits ALL 64 S-box columns, trace = Σ_c α_c·HW_c — the physically correct aggregate premise the parallel full-key attack relies on. The default `sbox` (single column) mode leaks only one column, which is unrealistically easy for per-column models (they read their column cleanly because the other 63 leak nothing). Single-column-sim success does NOT validate real-board behavior.
- Internally aligns traces before fitting (matching the preprocessing pipeline)
- Used by `adaptive.py --attack --sim` and `training/sim_sweep.py`

## Parallel full-key attack (`training/adaptive_parallel.py`)

Offline validation verdict (Aug 21): **the aggregate `sbox64` sim cannot validate full-key recovery with the per-column `cnn1` profiles.** Only the strongest model (col 0, 38.5% val acc) converges correctly; most columns converge to a confident WRONG hypothesis even in the sequential `adaptive.py --all-columns` path. The single-column sim is misleadingly easy. The documented real-board success (liveft board-finetuned profile, hyp 3, 32 queries) does not reproduce in sim — the sim's aggregate leakage template is not faithful enough at the per-column level, and the plain cnn1 profiles are too weak at this SNR (~14/64 columns leak below chance).

Two real bugs were found and fixed along the way:
1. `SimBoard(column=0)` leaked only column 0 — 63/64 columns scored pure noise in the parallel sim. Fixed with `target='sbox64'`.
2. `adaptive_parallel.py` `pack_nonce` overwrites ALL 128 nonce bits (64 cols × 2 bits), fully replacing the random base — with a deterministic tiebreak every query was the SAME all-zero nonce (zero information diversity). Fixed with a uniform tiebreak over equal-separation (n0,n1) choices.

The parallel attack is still unvalidated; the sim blocker is per-column model quality at this SNR, not the loop design.

## Gotchas

### Trigger race (every board interaction)
~50% of captures come back flat. `scope.capture()` return flag is **unreliable**. Must judge by `trace.std() < std_floor` (0.001 V on Husky) and retry. `collect_dataset.py` uses `_drain(target)` between retries — missing this causes consecutive flat captures. `live_query.LiveQuery.query()` returns `(None, None)` on flat/std-fail; caller must retry.

### Preprocessing order is locked and non-negotiable
`training/preprocess.py`: **align full trace → z-score full trace → crop to window**. Any deviation breaks feature distribution matching between profiling and live traces. `adaptive.py` and `live_finetune.py` must reproduce this exact order using the stored `ref` (alignment reference) and `mu`/`sigma` (z-score params) from the profiling `.npz`.

### Checkpoint format contract
All consumers (`Profile` in `train.py`, `attack.py`, `adaptive.py`, `live_finetune.py`) depend on this exact format:
```
{arch, column, window, n_classes, classes, hidden, state_dict, best_val_acc, seed}
```
Plus `target` field (`sbox` or `kadd`). Don't add/remove keys without updating all consumers.

### MLP architecture detection is fragile
`attack.py` detects MLP feature count via `model.net[0].in_features > window + 1` — assumes MLP has `model.net` Sequential. Will break if MLP architecture changes. The `> window + 1` check distinguishes raw MLP from centered-product MLP (which appends lags 1 and 4).

### Two parallel labeling systems
`training/labels.py` (numpy, vectorized) and `ascon_ref.py` (Python reference, byte-exact). They **must** be bit-identical. `training/labels.py` includes `_self_test()` verifying against `ascon_ref.py` (run with `python3 training/labels.py`). `training/eda.py` imports `kadd_labels` from `ascon_ref`, not from `labels.py`.

### clkgen_x4 vs extclk_x4
`pilot_gain.py` attempts `extclk_x4` (ADC clocked from crypto clock via ODDR/tio_clkout — drift-free sampling) but may not be stable at all sample counts. Actual datasets use `clkgen_x4` (ADC clocked from scope's internal PLL) with software cross-correlation alignment in `preprocess.py`. `extclk_x4` would eliminate alignment jitter if stable.

### HW class cardinality matters for loss weighting
S-box: classes 0–5 (6 classes). KADD: classes 0–8 (9 classes). Some classes may be empty depending on key/nonce distribution. Training must weight empty classes as 0 in the loss function, otherwise the model learns to predict impossible classes.

### `readOutput()` has 10 ms sleep
The FPGA core finishes in ~10 µs, but `AsconMux.readOutput()` has a hard 10 ms `time.sleep()` — this dominates adaptive query latency. 100 queries = 1 second minimum.

### Empty classes in training data
Not all HW classes appear equally across random keys/nonces. The loss function in `train.py` handles this by weighting empty classes to 0. Don't remove this handling.

### sim_board.py imports from training/ directory
`sim_board.py` adds `training/` to `sys.path` to import `labels`. This means it must be run from the repo root. Same pattern in `training/labels.py` for its self-test import of `ascon_ref`.

### Dataset quality gates
`collect_dataset.py` uses two filters: `--clip-threshold` (max absolute sample, default 0.49V — ADC rails at ±0.5V) and `--std-floor` (trace std, default 0.001 V). Recommended gain settings produce no clipping and no flat traces. `main2.h5` (gain −5 dB, 0% clip, 0% flat) is the reference quality.

### Verification is full-key only
A single column's 2 recovered key bits cannot be verified against ciphertext. All 64 columns must be assembled first, then `LiveQuery.verify_key(candidate_key)` re-encrypts a fresh query. This is the contract for `adaptive.py`: accumulate all 128 bits, then verify.

### Bitstream is checked in
Unlike typical Vivado projects, the built `.bit` file is tracked in git for reproducibility. `Dataset/` is not.

### RTL verified via verilator (Aug 12, board disconnect)
Full RTL audit + bitstream rebuild done while the board was disconnected:
- `tb_verify.sv` extended to all 5 NIST KAT vectors (same vectors as `sanity_check.py`); verilator sim **passes byte-exact** for both masked (d=1) and unmasked (`ASCON_UNMASKED`) builds: `ALL 5 VECTORS PASS`.
  Build: `cd vivado_ascon && verilator --binary --timing -Wno-fatal -Wno-width -Wno-lint -Wno-unoptflat --top-module tb_verify tb_verify.sv rtl/*.sv -o /tmp/tb_verify [ -DASCON_UNMASKED ]`
- Register map audited: `cw305_ascon_defines.v` matches `cw305_ascon_shim.py` exactly (KEY=0x0a, NONCEIN=0x0d, CIPHEROUT=0x09, TAGOUT=0x0c, VALID_AD=0x10, VALID_MSG=0x11, TEXTIN_BUF=0x12); write/read decode symmetric.
- Wrapper (cw305_top.v FSM + cdc_pulse + clocks.v) audited: `load_data` (O_start pulse) enters core INIT_LOAD, `start` (FSM LOAD_DATA) exits it — one cycle each, no race.
- Rebuilt `vivado_ascon/ascon_cw305_top.bit` (unmasked, `ASCON_UNMASKED=1 bash build_bitstream.sh`): 0 errors, 0 critical warnings, timing met (WNS=0.997, WHS=0.105), `sha256=b0fb6d6f…`.
- **Root cause of the Aug-12 post-replug freeze** (KEY round-tripped, NONCEIN read back 0, output frozen nonce-independent): the FPGA was running the **stock AES config** (from SPI flash after the replug), not our bitstream. Stock AES defines KEY at 0x0a (so KEY readback works) but has no NONCEIN register (map stops at 0x0b → default read 0). `IDENTIFY`=0x2e/`CRYPT_TYPE`=2 also match the stock template (values inherited from it), so IDENTIFY matching did not prove our bitstream was resident. No Verilog bug; reflash the board, then `python3 sanity_check.py` must pass 5/5 before attacking.
- Board-side gate after replug: `sanity_check.py` 5/5 → then `pilot_gain.py` for the current gain fingerprint → then continue the gain-20 full-key attack.

## Notes

- Paper draft: `paper.tex` (332 lines, 4 tables, 7 sections). Verified balanced LaTeX.
  Compile with: `pdflatex paper.tex && pdflatex paper.tex` (needs texlive-scheme-basic).
- The central finding ("structural deadlock") is fully documented and paper-ready.
- Scheme A (live on-board finetuning) is board-tested: 300 traces at gain 15
  → 90.7% train acc (72% majority prior), real first-order leakage learned. ACPPA
  with the board-finetuned model converges to the CORRECT key bits (hyp 3,
  posterior 0.999, 32 queries) — the unmasked core is crackable at amp=1.
- `adaptive.py` Phase 1+2: `--M` trace averaging (nonce repetition) plus optional
  `--cal` LR scoring. LR (logits/T − log prior) is opt-in: it dilutes the
  finetuned profile (T≈4, no convergence in 80 sim queries) and was motivated by
  the misread board verdict. M=64 averaging is the robust lever (q15 → q9).
- Phase 0 probe (`probe_averaging.py`): nonce-repetition averaging is the SNR
  lever. Same separating nonce captured M times and averaged: S-box true-hyp
  rank-1 0.25 (M=1, chance) → 0.94 (M=64), lr_margin −1.64 → 0.00 nats.
  The +18 dB the sim demanded is buyable at M=64. Naive cross-capture noise_std
  does NOT show 1/sqrt(M) (jitter+drift inflate raw variance) but the pipeline's
  align-then-z-score removes both — rank metrics are the ground truth.

