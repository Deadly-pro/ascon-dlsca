# DOM masked core build — status

Sources vendored from `ascon-hardware-sca/hardware/ascon_lwc/src_rtl/v2/` + `LWC/`:
- `vivado_ascon/rtl_lwc_dom/CryptoCore_SCA.vhd` — 1st-order DOM (2 shares, 320-bit randomness/cycle)
- `vivado_ascon/rtl_lwc_dom/LWC_SCA.vhd` — top-level wrapper (pdi/sdi/rdi shared ports)
- Helper files: Round.vhd, design_pkg.vhd, LWC_config_32_2s.vhd, etc.

## Blockers

1. **Randomness source (rdi):** The DOM core needs 320 bits of fresh randomness every cycle
   (2 cycles/round for the masked S-box). The CW305 has no TRNG. Solution: add an
   LFSR-based PRNG in the adapter (`ascon_top_dom.sv`) to drive rdi automatically.
   This is standard for SCA eval boards.

2. **Adapter port mismatch:** The current `ascon_top.sv` uses the LWC crypto core
   interface (single-share bdi/bdo). The DOM core exposes LWC_SCA with shared ports:
   `pdi_data[2*W-1:0]`, `sdi_data[2*SW-1:0]`, `rdi_data[RW-1:0]`, `do_data[2*W-1:0]`.
   A new `ascon_top_dom.sv` is needed that:
   - Drives both shares of pdi (key, nonce, pt) from the register file
   - Drives both shares of sdi (key share)
   - Drives rdi from the LFSR PRNG
   - Reads do_data and combines shares (XOR for Boolean masking)
   - Maps the unified `done` signal back to the cw305_top.v protocol

3. **Build script:** `build_ascon_cw305.tcl` needs a new project target for the DOM
   core (different VHDL files, VHDL 2008, SCA wrapper).

## Minimum to build (~2-3 h work)

- Write `vivado_ascon/rtl/ascon_top_dom.sv` with LFSR PRNG + share adapter
- Add a `build_ascon_cw305_dom.tcl` or modify the existing one
- Build: `bash build_bitstream.sh` (25-45 min)
- Sanity check: `sanity_check.py` 5/5

## Fallback for the paper

If the DOM build doesn't complete in time: the paper can present the *simulated*
DOM collapse (2-share model in software with injected faults) as a secondary
result, alongside the real unmasked glitch attack. This is weaker but still
publishable as "study on the NIST reference."