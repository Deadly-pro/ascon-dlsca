# ascon-dlsca

Side-channel analysis (power) of the **ASCON** lightweight cipher on a
ChipWhisperer **CW305** (Artix-7 XC7A100T) — RTL implementation, trace capture,
CPA/DPA and deep-learning (DL-SCA) key recovery.

## Layout

```
capture_cw305_traces.py   # power-trace capture (CW305 + CW-Lite, register API)
program_cw305.py          # program bitstream into SPI flash (CW305's own USB)
program_ascon_fpga.py     # load bitstream into FPGA fabric over USB (volatile)
check_board.py            # CW305/CW-Lite connectivity check
check_spi_bridge.py       # SPI-bridge sanity check
regen_and_run.sh          # rebuild bitstream / re-run sim (clears stale xsim cache)
vivado_ascon/             # self-contained Vivado in-memory flow (no GUI project)
  build_ascon_cw305.tcl   #   synth/place/route -> ascon_cw305_top.bit (~30-45 min)
  src/                    #   cw305_top_ascon + cw305 register interface
  src/ascon/              #   ASCON cores (vendored from ascon-hw-public)
  constrs/cw305.xdc       #   pin constraints
  sim_sanity.tcl          #   xsim sanity check
Dataset/ascon_dataset.h5  # 1000 x 20000 power traces + key/nonce/ct
ascon_sca_notebook.ipynb  # DL-SCA analysis (preprocessing -> S-box labels -> 1D CNN)
```

## Setup on WSL / fresh Linux (no hardware needed)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

That's everything for the **analysis** side. You can run the notebook end-to-end
on the committed dataset (`Dataset/ascon_dataset.h5`) with no board:

```bash
jupyter notebook ascon_sca_notebook.ipynb
```

## Rebuild the bitstream (Vivado required, ~30-45 min)

Install Vivado 2026.1, then:

```bash
VIVADO_PATH=/path/to/Vivado/bin/vivado bash regen_and_run.sh
# or: cd vivado_ascon && /path/to/Vivado/bin/vivado -mode batch -source build_ascon_cw305.tcl
```

## Capture (hardware: CW305 + CW-Lite)

1. Program the FPGA over USB (mode switches M0=1 M1=1 M2=1):
   `python3 program_ascon_fpga.py`
2. Capture (ADC = extclk_x4 of the 10 MHz crypto clock = 40 MS/s):
   `python3 capture_cw305_traces.py -n 1000 -s 25000`
3. For SPI-flash boot (M0=1 M1=0 M2=0 + power-cycle): `python3 program_cw305.py`

Capture loop sync: inputs are loaded **before** `scope.arm()`, and a trigger
timeout drains the FPGA op before the next `arm()` so `tio_trigger` (high for the
whole bit-serial op) never lingers into the next trace.

## Notes

- `chipwhisperer/` and `ascon-hw-public/` are upstream git repos (gitignored);
  scripts use the pip-installed `chipwhisperer` 6.0.0 and the cores vendored in
  `vivado_ascon/src/ascon/`.
