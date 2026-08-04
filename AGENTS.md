# AGENTS.md

Project context for opencode. (Created from Claude Code session history + project files; no prior CLAUDE.md existed.)

## Project

Hardware security research: **side-channel analysis (power/EM) of the ASCON lightweight cipher** on a ChipWhisperer **CW305** (Artix-7 XC7A100T, part `xc7a100tftg256-2`). Faculty-led VLSI research paper with a PES professor + a group of friends. Goal: implement the ASCON permutation in RTL, capture power traces, recover the key via CPA/DPA, and evaluate countermeasures.

## Layout

- `vivado_ascon/` — self-contained Vivado 2026.1 in-memory flow (no GUI project). Top module `cw305_top_ascon`; sources in `src/` + `src/ascon/`; constraints `constrs/cw305.xdc`; `build_ascon_cw305.tcl` → `ascon_cw305_top.bit`; `tb_ascon_cw305.v` + `sim_sanity.tcl` for simulation.
- `ascon-hw-public/` — upstream reference ASCON hardware repo (gitignored; cores are vendored into `vivado_ascon/src/ascon/`).
- `chipwhisperer/` — local ChipWhisperer source tree (gitignored; capture scripts use the pip-installed `chipwhisperer` 6.0.0).
- `Dataset/` — captured traces (`ascon_dataset.h5`: 1000 × 20000 power traces + key/nonce/ct).
- Root scripts: `capture_cw305_traces.py`, `program_cw305.py`, `program_ascon_fpga.py`, `check_board.py`, `check_spi_bridge.py`, `regen_and_run.sh`.

## Build (bitstream, no board needed, ~30–45 min)

```bash
cd /home/deadly-pro/ascon/vivado_ascon
/tools/2026.1/Vivado/bin/vivado -mode batch -source build_ascon_cw305.tcl
# output: vivado_ascon/ascon_cw305_top.bit
```

`regen_and_run.sh` clears a stale xsim cache (cdc_pulse.v was once elaborated from its stale netlist version with no `dst_pulse` port — always clear `vivado_ascon.sim` before re-elaborating) and rebuilds. `regen_and_run.sh sim` runs only the simulation sanity check.

## Program + capture (board needed)

```bash
python3 program_cw305.py vivado_ascon/ascon_cw305_top.bit    # SPI flash via CW305's own USB (2b3e:c305), no CW-Lite
python3 capture_cw305_traces.py -b vivado_ascon/ascon_cw305_top.bit -n 1000 -o ascon_traces.h5
```

Mode switches: USB boot M0=1 M1=1 M2=1; SPI boot M0=1 M1=0 M2=0 (+ power-cycle to boot from flash).

## Register API (CW305 register interface — no SimpleSerial)

- TEXTIN (0x06) <- nonce (16B)
- KEY    (0x0a) <- key (16B)
- GO     (0x05) <- start
- TEXTOUT/CIPHEROUT -> ciphertext (4B) + tag (16B) via `data_o[127:0]`
- `tio_trigger` is high during the cipher operation

## Toolchain

Vivado 2026.1 at `/tools/2026.1/Vivado/bin/vivado`; Python `chipwhisperer` package; iverilog + gtkwave for reference-hardware simulation.
