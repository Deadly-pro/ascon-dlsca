# Ascon-CW305 Vivado project (self-contained)

Builds Ascon bitstream for ChipWhisperer CW305 (xc7a100tftg256-2).

## Build (no board needed, ~30-45 min)
    cd vivado_ascon
    /tools/2026.1/Vivado/bin/vivado -mode batch -source build_ascon_cw305.tcl
    # or: VIVADO_PATH=/path/to/vivado bash ../regen_and_run.sh
Output: vivado_ascon/ascon_cw305_top.bit

## Program + capture (board needed)
    cd ..
    python3 capture_cw305_traces.py -b vivado_ascon/ascon_cw305_top.bit -n 1000 -o ascon_traces.h5

## Register mapping
- TEXTIN (0x06) <- nonce (16B)
- KEY    (0x0a) <- key (16B)
- GO     (0x05) <- start
- TEXTOUT/CIPHEROUT -> ciphertext(4B)+tag(16B) via data_o[127:0]
