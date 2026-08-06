# ASCON-128 Side-Channel Analysis on NewAE CW305 + ChipWhisperer-Lite

Power side-channel analysis (SCA) of a **masked ASCON-128** hardware
implementation — the NIST SP 800-232 lightweight authenticated cipher — running
on a **NewAE Technology CW305** (Artix-7 XC7A100T FPGA target) and captured with
a **ChipWhisperer-Lite** (CW-Lite) 40 MS/s scope front-end.

This repository is a complete, board-tested research pipeline:

- **RTL** — threshold-implemented (d=1, 2-share) masked ASCON-128 AEAD core,
  vendorized from `compact-yet-fast-ascon`, wrapped for the CW305 register
  interface.
- **Oracle** — a byte-exact ASCON-128 reference (NIST SP 800-232) that predicts
  the FPGA's register readback, validated 5/5 known-answer vectors on hardware.
- **Capture** — synchronized power-trace collection where every trace is
  verified against the oracle before storage (no dead/clipped traces stored).
- **Analysis** — SNR / NICV / alignment / spectrum EDA in a self-contained HTML
  report, plus a demo dataset included for offline reproduction.

---

## Hardware Setup

| Item | Role | Notes |
|------|------|-------|
| **NewAE CW305** (Artix-7 XC7A100T-FTG256) | DUT — runs the masked ASCON core | xc7a100tftg256, bitstream built with Vivado 2026.1 |
| **ChipWhisperer-Lite (CW-Lite)** | Scope — 40 MS/s power capture + trigger | `adc_src = clkgen_x4`, trigger on `tio4` |
| VCCINT / PLL | Power rail + crypto clock | 1.0 V core; 10.0 MHz crypto clock on PLL1 (verified via `pll_outfreq_get`) |

The CW-Lite samples the target's power trace at **40 MS/s** while the CW305
executes the ASCON-128 operation (AD=4 B, PT=4 B, 16-byte key, 16-byte nonce).
The `tio_trigger` signal on the CW305 holds for the full active crypto window so
each capture window is aligned to the operation.

Tested bitstream: `vivado_ascon/ascon_cw305_top.bit` (programmed over USB).

## Repository Layout

```
ascon_ref.py              # NIST SP 800-232 ASCON-128 reference oracle + leakage labels
cw305_ascon_shim.py       # maps the CW305 register API to the masked-core register map
sanity_check.py           # 5 known-answer vectors, byte-exact vs FPGA  (ALL PASS)
collect_dataset.py        # synchronized collection, per-trace oracle verification
view_dataset.py           # SNR / NICV / alignment / spectrum HTML report
pilot_gain.py             # pre-collection calibration pilot (gain / ADC sync / clock)
verify_oracle.py          # offline oracle selftest + round-trip + batch perf
build_bitstream.sh        # one-shot Vivado batch build -> ascon_cw305_top.bit
build_ascon_cw305.tcl     # synth/place/route script (xc7a100tftg256)
vivado_ascon/
  fpga/                   # CW305 wrapper (top, register file, USB FE, clocks, XDC)
  rtl/                    # masked ASCON-128 core (compact-yet-fast-ascon, d=1)
  ascon_cw305_top.bit     # built bitstream
  tb_verify.sv            # optional RTL testbench vs oracle expected file
results/
  demo.h5                 # 100 verified traces (subset of a 1000-trace run)
  report.html             # generated EDA report on demo.h5 (open in a browser)
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Requires Vivado 2026.1 for bitstream rebuilds (optional; the committed
`ascon_cw305_top.bit` is ready to program).

## Usage

### 1. Verify the oracle (no hardware)

```bash
python3 verify_oracle.py
```

### 2. Program the FPGA + run the known-answer sanity check

```bash
python3 sanity_check.py -b vivado_ascon/ascon_cw305_top.bit
# expect: ALL 5/5 PASSED (ciphertext, tag, and combined readback byte-exact)
```

### 3. Collect a dataset

```bash
python3 collect_dataset.py -n 1000 -o Dataset/run.h5        # random keys
python3 collect_dataset.py -n 500 --key 000102...0f -o Dataset/fixed.h5
```

Every stored trace's ciphertext is verified against the oracle; traces that
clip (`|peak| > 0.49`) or come back flat (`std < 0.01`) are rejected and
counted.

### 4. Analyze

```bash
python3 view_dataset.py Dataset/run.h5 --outdir Dataset/analysis
# writes Dataset/analysis/report.html
```

### 5. Rebuild the bitstream (Vivado)

```bash
bash build_bitstream.sh        # ~25-45 min, log in vivado_ascon/build_logs/
```

## Verified Results

- **5/5** known-answer vectors match the NIST SP 800-232 oracle **byte-for-byte**
  on the FPGA (ciphertext + tag + combined register readback).
- Captured datasets (e.g. 1000 traces @ 24000 samples) with **100 % readback
  verification** and clean trace quality (dual-threshold clip/flat filter).
- The included `results/report.html` shows the full EDA on 100 verified traces:
  alignment histogram, spectrum (10 MHz clock harmonics), and leakage scans.

## Reference Implementation

The `rtl/` core is the [compact-yet-fast-ascon](https://github.com/edge-group-polito/compact-yet-fast-ascon)
masked ASCON implementation (d=1, 2-share) by the Politecnico di Torino
edge-group, wrapped for the CW305 register interface. The Python oracle is the
NIST SP 800-232 ASCON-128 reference. Hardware and capture tooling are from
NewAE Technology (CW305 + ChipWhisperer-Lite).

## License

See the per-file headers in `vivado_ascon/fpga/` (NewAE) and the upstream
`compact-yet-fast-ascon` terms for the RTL. Project-specific scripts are
provided for research/education use.
