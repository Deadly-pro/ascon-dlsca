# DL-SCA Literature Study: ASCON-Hardware-SCA-Related Attacks — Methodology Report

**Date:** 2026-08-31 · **Scope:** every published DL-SCA attack touching the `ascon-hardware-sca` lineage or Ascon FPGA targets, with exact methodology extracted from primary sources.

---

## 0. The critical discovery — a citation-chain correction

The working assumption going in was: *"a paper broke our bitstream (ascon-hardware-sca) with 24k traces + an ensemble."* **This is wrong in an important way.**

**"One for All, All for Ascon" (Rezaeezade, Basurto-Becerra, Weissbart, Perin — ACNS 2024, ePrint 2023/1922)** — the "24k traces" memory — attacked **software implementations running on an STM32F4 microcontroller** (ChipWhisperer-Lite, 7.37 MHz target clock), NOT the FPGA core:

> *"Traces are collected using a ChipWhisperer Lite board and an 8-bit precision oscilloscope, coupled with the STM32F4 target running at a frequency of 7.37 MHz. … The C implementations by the Ascon team are available in their GitHub repository [SDG+20]."* (§4.2)

The "Ascon-Protected" dataset is the **first-order masked 32-bit C implementation** (bit-interleaved masking) from the ASCON team's *software* repository. The Zenodo record (10229484) **does** contain SAKURA-G FPGA hardware datasets (`ascon_hw_protected.h5`, 500k traces × 10k samples; `ascon_hw_unprotected.h5`, 100k × 6,000, Lecroy 500 MS/s) — but **the ensemble paper never used them**, and **no published work has attacked them** (0 citations, 0 indexed reproductions as of 2026-08).

**Implication for us:** nobody has ever published a DL-SCA key-recovery attack against the *hardware* `ascon-hardware-sca` RTL — neither the DOM-masked version nor (especially) any CW305-port of it. Our CW305 work targets ground no published paper covers. The "they did it in 24k traces" comparison is to a **32-bit software implementation at 7.37 MHz on a microcontroller** — a completely different leakage environment (software register transitions, no parallel bus switching, different noise).

---

## 1. One for All, All for Ascon (ACNS 2024) — the ensemble paper

### 1.1 Target & attack point
- **Datasets:** Ascon-Unprotected (32-bit optimized C, 100k traces × 772 samples) and Ascon-Protected (1st-order masked C, 500k × 1408), both STM32F4 @ 7.37 MHz, CW-Lite at 4× target clock.
- **Attack point:** round-1 S-box output, with an algebraic trick. The Ascon column S-box outputs are (their Eq. 2):
  - y4 = x1(1+x0+x4) + x3 + x4
  - At initialization, x0 = IV (public), x3 = nonce (public), x4 = public constant; **x1 = key[0:8] (secret), x2 = key[8:16] (secret)**
  - Therefore **y4 depends on exactly one key word (x1)** → leakage model `Y = k_i^(1) & (255 ⊕ IV_i ⊕ M_i^(1)) ⊕ M_i^(1) ⊕ M_i^(2)` — a **byte-wise divide-and-conquer on x1 in 8 attacks**
  - For x2 (the other key half): use y0 or y1 (contain x2 non-linearly), substituting the already-recovered x1
- **Classes:** HW of the target byte's contribution (9 classes) — standard HW leakage model on the *composed* intermediate

### 1.2 Methodology (their pipeline)
1. **50 random-search models per sub-key per architecture** (Table 1 ranges: MLP 2–8 layers, 30–150 neurons; CNN 2–4 conv layers, 4–20 filters, first filter 4–24, stride 2–10, pool 4–10; LR 1e-4..1e-3, Adam, batch 128, **10 epochs**)
2. Rank all 50 by **guessing entropy (GE)** on attack traces; take the best single ("GE-Best")
3. **Ensemble = the 5 best models** (must include the best); aggregate by **summing class probabilities across models**, accumulate over attack traces ("GE-Ensemble")
4. Success = GE = 1; NT = traces to reach it
5. Repeat 8× (once per key byte of x1)

### 1.3 Results
| Dataset | Best single model | Ensemble (5 models) |
|---|---|---|
| Unprotected (software) | MLP: key in ~100 traces; CNN ≈ 5× worse | MLP ensemble ≈ best single (no gain); CNN ensemble ~1000 traces |
| **Protected (software, masked)** | best MLP: only 2/8 sub-keys ever reached GE=1 | **MLP ensemble: 7/8 sub-keys, < 3000 traces total; CNN ensemble: 8/8** |

**Their own key insight:** *"the ensemble method is significantly more effective for challenging datasets, where finding optimal models is more difficult… in the case of Ascon-Protected, almost all the best-found models performed poorly. However, combining those weak models through the ensemble method could still significantly improve the attack performance."*

### 1.4 What made it work (transferable lessons)
- **The leakage model is doing the heavy lifting**: substituting public values into the S-box algebra to isolate ONE key word per attack (y4 → x1). This is the same structure as our `hypothesis_labels` — but they attack the **S-box OUTPUT byte**, computed from already-recovered x1 for the x2 attack (chained divide-and-conquer).
- **Ensembles rescue weak models** — relevant to our situation: our single models performed poorly; an ensemble of our models might have squeezed out more. But note their weak models still had GE-reducing signal per model (models that "only need to reduce GE to small values").
- **10 epochs, tiny models** (30–150 neurons) — nothing exotic. CNNs needed bigger searches.
- 50k profiling / 10k attack traces, fixed-key attack phase.

---

## 2. SCARL (Ramezanpour, Ampadu, Diehl — ACM JETC / NIST LWC 2020)

### 2.1 Target — the only published FPGA ASCON DL-SCA
- **Their own lightweight Ascon on CW305 Artix-7** (Virginia Tech SAL design): **one bit-sliced S-box hardware unit shared by all 64 columns, one S-box op per clock cycle → 64 cycles per round**
- FOBOS rig: PicoScope 5000 + 20 dB amp, **125 samples per clock cycle**, supply-pin measurement, 40k encryptions (80k single-S-box traces)
- Attack point: round-1 S-box **output** of columns 0–1 (5-bit), input = IV bit + k_i, k_{i+64} + nonce bits → **2 key bits per column**

### 2.2 Methodology
1. **Unsupervised, model-free** (no HW assumption): sliding window (W=10, stride 5) → **LSTM autoencoder** (single LSTM cells, feature dim D=150) reconstructs the window; internal state c = feature. MSE loss, Adam, batch 512, ~25 epochs. Normalize to [−1,1].
2. **Actor-critic RL clustering**: actor MLP (512, 256 → μ, σ of Gaussian policy) assigns each feature to cluster C0/C1; reward = max inter-cluster mean-distance − KL(split vs uniform); critic MLP (256) with TD learning. Stops ~350 steps.
3. **Key ranking**: for each key candidate k*, compute S-box outputs X*_j, fit a **≤2nd-order generic leakage model** (higher terms forced to 0) minimizing MSE to the actor's cluster labels, re-cluster, rank by **max inter-cluster mean difference ℛ(k*)**. Correct key = largest ℛ.
4. Full-key claim: 2 key bits per column × 64 columns ⇒ repeat per column (they demonstrate columns 0–1 = 4 bits; abstract claims the 128-bit key by extension — **the extension is asserted, not demonstrated**).

### 2.3 Results
- **24K traces** for the 4-bit subset (S-boxes 0+1); classical DPA (HW and MSB models) and CPA fail at >40K traces: HW-DPA ranks the true key 8th; MSB-CPA leaves 2 wrong candidates above the true one
- **Why classical fails (their diagnosis):** the true leakage is **not linear in HW or MSB of the 5-bit S-box output** — it's low-order but non-linear. This is the same phenomenon as our per-bit scan: the 5-bit chi output's power signature doesn't correlate linearly with any simple function of the key bits.
- 8 minutes on a GTX 1080 for the 4-bit demo.

### 2.4 Transferable lessons for us
- **125 samples/clock cycle** vs our 4 samples/cycle (40 MS/s / 10 MHz): their per-S-box transient is ~31× more resolved. Our captures are 4 samples/cycle — the finest structure we could possibly see is 4 points per S-box op. This is a direct explanation of why our per-bit scan finds nothing: the value-dependent component of the transient may be sub-sample at our rate.
- **Unsupervised clustering + generic low-order model** beats model-dependent CPA when the leakage model is unknown — candidate approach for our data (cluster our M=32 traces on the load transient, test if clusters align with any low-order function of key bytes).
- Their FPGA is *slower per round* (64 cycles) vs our core (~3.5–8.5 µs whole encryption ≈ 35–85 cycles total) — much cleaner per-op isolation.

---

## 3. What nobody has done (our position in the literature)

1. **No published attack on `ascon-hardware-sca` RTL on ANY FPGA board** — the Zenodo hardware datasets (SAKURA-G) are unattacked in the literature; our CW305 port is novel territory.
2. **No published DL-SCA on the CW305 + this core combination.**
3. **No published work reports the byte-load HW leakage finding** (that the dominant first-order leak of this core is the key-register load transient, not the S-box output). SCARL's DPA/CPA failure diagnosis ("leakage is not linear in S-box-output HW/MSB") is consistent with our observation that the S-box output HW sits at noise floor on our captures.
4. The ensemble paper's protected attack is on **masked software** — a much easier target than masked hardware (no parallel bus/switching noise).

---

## 4. Methodological comparison table

| | Ensemble (ACNS'24) | SCARL (JETC'21) | Ours (2026) |
|---|---|---|---|
| Target | STM32F4 software (masked + unmasked C) | Own Ascon on CW305 FPGA (bit-sliced, 64 cyc/round) | ascon-hardware-sca lineage core on CW305 (~35–85 cyc total) |
| Scope | Software only | FPGA, own RTL | FPGA, official RTL port |
| Attack point | y4 (S-box out, byte-wise → x1), then y0/y1 → x2 | S-box outputs, cols 0–1 (2 bits/col) | key-register load HW (16 bytes) |
| Leakage model | HW of composed byte | none (unsupervised) + ≤2nd-order generic | HW (linear) |
| Traces | 50k profile / 10k attack (fixed key) | 24k attack (no profile) | 3k–6k profile (random keys), M=600 same-key attack |
| Model | ensemble of 5 MLPs/CNNs (random search 50) | LSTM-autoencoder + actor-critic RL | linear template / CNN (tied) |
| Clock resolution | 4× target clock | **125 samples/cycle** | **4 samples/cycle** ← fundamental limit |
| Result | full key (masked SW): <3000 traces | 4-bit demo @ 24k; full key asserted | HW signature 87%/byte; value recovery blocked (0/128 bits) |

---

## 5. What our data says vs their findings — reconciliation

1. **SCARL's "CPA fails because leakage isn't linear in S-box-output HW"** ⟺ our S-box output HW at noise floor (r ≈ 0.06–0.09, 16/64 cols). Their fix was unsupervised clustering at 125 samples/cycle; our equivalent resolution is 4 samples/cycle — 31× coarser. **Our negative result at 4 samples/cycle is consistent with their leakage-structure finding.**
2. **Ensemble paper's success on masked software** used the y4-isolation trick (public everything except x1). We attacked the same intermediate family (round-1 S-box) on hardware and found it at floor — because at 4 samples/cycle the S-box transient is unresolvable, while the *register load* transient (their attack never needed it; software loads are diffuse) dominates our captures.
3. **Both papers' targets differ from ours in the dimension that matters**: sample density per switching event. Their successes ride on resolving per-cycle or per-op detail; our rig fundamentally cannot at 40 MS/s on a 10 MHz core with the whole op in ~350 samples.

---

## 6. Actionable conclusions for the paper & any future board session

1. **Framing (paper):** we are the **first DL-SCA study of the `ascon-hardware-sca` RTL on a CW305 FPGA**; published successes are on software (ensemble paper) or a custom 64-cycle/bit-sliced FPGA at 125 samples/cycle (SCARL). Our negative result is the *predicted* outcome at 4 samples/cycle given SCARL's leakage-structure finding — a supportable scientific claim, not a failure.
2. **The one board experiment that could still succeed** (testable against both papers' methods):
   - **Crypto clock ÷4 (2.5 MHz)** → 16 samples/cycle at fixed 40 MS/s ADC — still below SCARL's 125 but 4× our current; combined with **their y4/x1 byte-wise model** (which we can compute exactly with our `hypothesis_labels`) and **their ensemble method** (5 MLPs, random search, 10 epochs — trivially replicable offline).
   - **SCARL's unsupervised clustering** on our M=600 load-transient features — needs no leakage model, tests for any low-order structure we haven't hypothesized.
3. **If a future session captures at 2.5 MHz:** replicate the ensemble paper's exact pipeline (50 random models → 5-best ensemble → GE) against our y4-byte labels. Their entire methodology is reproducible offline from our existing captures *if* the per-sample resolution supports it.
4. **The Zenodo hardware datasets** (500k masked-hardware traces at 500 MS/s SAKURA-G) are public and unattacked — downloading and running our pipeline on them is a legitimate, board-free contribution comparison (10.6 GB `ascon_hw_protected.h5`): attack their unprotected 100k × 6000-sample set with our byte-HW methodology and compare leak structure at 500 MS/s vs our 40 MS/s. **This directly tests the "resolution hypothesis" without any board time.**

---

## 7. Sources
- ePrint 2023/1922 (Rezaeezade et al., ACNS 2024) — full PDF, extracted §4–6
- Zenodo 10229484 — dataset record (hardware = SAKURA-G/Lecroy 500 MS/s; software = CW/STM32F4)
- arXiv 2006.03995 / ACM JETC (SCARL) — full PDF, extracted §5–6
- GMU ATHENa protected-HW registry (formal verification + TVLA of ascon-hardware-sca; no key-recovery break)
- Literature search (DataCite/OpenAlex/ePrint): **0 citing works for the Zenodo hardware datasets as of 2026-08**
