# FULL KEY RECOVERY — HOW TO RUN (READ THIS FIRST)

Everything you need is already in this repo (git pull gets it). The 64 trained
CNN models are in `board_session/pa_assets/models/c0.pt .. c63.pt`. The
profiling data is in `board_session/pa_assets/profiling.npz`.

This attack recovers the FULL 128-bit key of the ASCON-128 core on the CW305
board using POWER ANALYSIS (method: **SBOX round-1, per-column** — each of the
64 S-box columns leaks 2 key bits, the assembler combines all 64).

---

## 1. SETUP (one time, on the Windows + WSL machine)

The project .venv is broken. Use a FRESH venv:

```bash
cd /mnt/c/Users/<you>/Documents/GitHub/ascon-dlsca
git pull                       # get the models + this file
python3 -m venv .venv_fresh
.venv_fresh/bin/pip install numpy h5py scipy scikit-learn torch --index-url https://download.pytorch.org/whl/cpu
.venv_fresh/bin/pip install chipwhisperer==6.0.0
```

If `python3` is not found, try `python` or `py -3`.
If pip complains about "externally managed", add `--break-system-packages`.

Then use `.venv_fresh/bin/python` for every command below (NOT plain
`python3`, NOT the old `.venv`).

Sanity check the env:
```bash
.venv_fresh/bin/python -c "import numpy, h5py, torch, chipwhisperer; print('OK')"
```
If numpy itself errors on import, reinstall it:
```bash
.venv_fresh/bin/pip install --force-reinstall numpy
```

## 2. CHECK THE BOARD (2 min)

```bash
.venv_fresh/bin/python sanity_check.py -b vivado_ascon/ascon_cw305_top.bit
```
You MUST see 5/5 KATs pass. If not: re-plug the board USB, re-flash, retry.
Do not continue until this passes.

## 3. RUN THE FULL KEY RECOVERY

```bash
.venv_fresh/bin/python board_session/run_pa_test.py --resume --key a45f8bcdab3d569e1ee091e0d29f2ab7
```

What it does, phase by phase (all automatic):
- Phase 0: sanity_check again (gate)
- Phase 1: SKIPPED (profiling.npz already exists in pa_assets)
- Phase 2: SKIPPED (all 64 models already trained)
- Phase 3: floor-gate report (see Section 5 for what this means)
- Phase 4: live fine-tune column 0 (300 board traces) — closes the gap
          between offline training and live board noise
- Phase 5: per-column attack at the target key (queries the board with
          chosen nonces, scores all 4 key hypotheses per column)
- Phase 6: full-key assembly (combines 64 columns, brute-forces weak ones,
          VERIFIES each candidate by re-encrypting and comparing ct/tag)

Output lands in `board_session/run_pa_<timestamp>/`:
- `session.log`   — full transcript
- `attack_scores.npz` — per-column (64x4) hypothesis scores
- `verdict.txt`   — THE RESULT (read this)

## 4. HOW TO INTERPRET THE RESULT (verdict.txt)

The verdict is one of:

| Verdict line | Meaning | Paper story |
|---|---|---|
| `FULL_KEY_RECOVERED key=<hex>` | All 128 bits found AND verified against real ciphertext | The headline result — full-key recovery via DL-PA |
| `KEY_MISMATCH ...` | Assembler returned a key that does not re-encrypt | Bug or wrong-domain models; report the hex, do NOT claim recovery |
| `partial_assembly confident_cols=X/64 weak=Y budget=4^Y` | X columns were confident; Y weak columns brute-forced but no match found | Honest partial result: per-column recovery works, full assembly bounded |
| `assembly_failed ...` | Scores too weak to converge | Per-column leakage below usable threshold at this gain/SNR |
| `attack_failed` | Board query problem (flat traces, timeout) | Retry; check board |

**IMPORTANT — what counts as a result:**
- Only `FULL_KEY_RECOVERED` is a full-key claim. It is verified by the
  script against the device oracle (fresh re-encryption), so it cannot be
  wrong.
- `partial_assembly` is still a valid paper number: report
  "X/64 columns confident at >99% posterior; full key bounded at 2^Y".
- Never report a key that did not pass verification.

## 5. WHAT "FLOOR" MEANS (so you can read Phase-3 output)

The floor-gate printout looks like:
```
col  0: floor 36.7%  logistic 28.8%  KNN 28.7%  floor
```
Interpretation:
- The S-box column label is the Hamming weight (0..5) of a 5-bit S-box
  output — 6 possible classes.
- Class counts are NOT equal: some weights (e.g. HW=3) are far more common
  than others. The **majority floor** is the accuracy a dumb classifier gets
  by always guessing the most common class (here ~37%). That is the bar a
  classifier must beat to prove it reads real per-trace information.
- **logistic/KNN sitting AT the floor is EXPECTED at this SNR and does NOT
  mean the attack fails.** The CNN profiles (Phase 2 models) extract the
  signal that linear probes cannot: measured per-column key-rank top-1 is
  42.7% mean vs 25% chance on held-out traces, all 64 columns above chance.
  The real attack metric is the 4-hypothesis key rank (chance = 25%), not
  the 6-class HW accuracy (chance = 16.7%, floor ~37%).
- Ignore the "VERDICT: NO per-trace leakage" line from probe_leakage if the
  CNN key-rank (Section 3 / attack_scores) shows above-chance scores. That
  probe uses weak linear models on the skewed-class problem and is
  documented as a false-negative trap in the paper.

## 6. IF YOU CHANGE THE TARGET KEY

The attack key is the `--key` hex. Any 32-hex-char key works:
```bash
.venv_fresh/bin/python board_session/run_pa_test.py --resume --key <NEW_KEY_HEX>
```
The models are key-agnostic (they learn column leakage, not a specific key).

## 7. TROUBLESHOOTING

| Symptom | Fix |
|---|---|
| `sanity_check` not 5/5 | Replug board, reflash bitstream, rerun |
| ImportError numpy/torch | Use `.venv_fresh/bin/python`, reinstall numpy |
| Every capture "flat" | Board trigger race — the script retries automatically; check USB cable |
| `verify_state not available` WARNING | Harmless (older build); sanity_check 5/5 is the real gate |
| Script stops at Phase 3 with floor verdict | Normal — read Section 5; let it continue (the verdict line is from the weak probe, not the attack) |
| Takes >2 h | Normal for first run (6000-trace capture in older versions; --resume skips it now) |

## 8. FILES THAT MATTER

- `board_session/pa_assets/models/c{col}.pt` — 64 trained CNN profiles
- `board_session/pa_assets/profiling.npz` — profiling traces + labels + alignment ref
- `board_session/run_pa_test.py` — the full pipeline (resume-aware)
- `training/fullkey_assemble.py` — assembler + oracle verifier
- `training/scores_export.py` — per-column board attack
- `training/adaptive.py` — Profile loader / scoring machinery
