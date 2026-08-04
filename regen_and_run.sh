#!/usr/bin/env bash
# regen_and_build.sh — one-shot fix for the CW305 Ascon Vivado project.
#
# Why: the xsim simulation was elaborated against a STALE cdc_pulse.v
# (the netlist version with FDRE/LUT + no dst_pulse port). cdc_pulse.v on
# disk is now the correct behavioral RTL; this script clears the stale
# simulation cache and rebuilds everything clean so Vivado re-elaborates.
#
# Usage:
#   bash regen_and_build.sh        # clean sim cache + synth the .bit
#   bash regen_and_build.sh sim    # only re-run simulation sanity
set -e
cd "$(dirname "$0")"
VIV="${VIVADO_PATH:-/tools/2026.1/Vivado/bin/vivado}"
PROJ=vivado_ascon

echo "==> Clearing stale simulation artifacts"
rm -rf "$PROJ/vivado_ascon.sim"
rm -f  "$PROJ/vivado_ascon.cache/"*.clean 2>/dev/null || true

if [ "${1:-}" = "sim" ]; then
    echo "==> Running simulation sanity on cw305_top_ascon"
    $VIV -mode batch -source sim_sanity.tcl
    echo "==> DONE. Check the tcl console for elaboration result."
    exit 0
fi

echo "==> Building Ascon bitstream (30-45 min)"
$VIV -mode batch -source build_ascon_cw305.tcl
echo "==> Output: $PROJ/ascon_cw305_top.bit"