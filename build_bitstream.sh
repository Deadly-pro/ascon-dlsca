#!/bin/bash
# Build the compact-yet-fast-ascon bitstream for CW305-100t
# Usage: bash build_bitstream.sh
set -e
cd "$(dirname "$0")"

VIVADO=/tools/2026.1/Vivado/bin/vivado
TCL=build_ascon_cw305.tcl
OUTDIR=vivado_ascon/build_logs

if [ -n "$ASCON_UNMASKED" ]; then
    LABEL="unmasked d=0 ASCON-128"
    LOG=rebuild_unmasked
else
    LABEL="masked ASCON-128"
    LOG=rebuild4
fi

mkdir -p "$OUTDIR"

echo "[+] Starting Vivado synthesis (CW305 100t, $LABEL)..."
echo "    Log: $OUTDIR/$LOG.log"
echo "    This takes 25-45 minutes. Watch with:  tail -f $OUTDIR/$LOG.stdout"
echo ""

rm -f vivado.log vivado.jou

$VIVADO -mode batch -source "$TCL" \
    -log "$OUTDIR/$LOG.log" \
    -journal "$OUTDIR/$LOG.jou" \
    > "$OUTDIR/$LOG.stdout" 2>&1

RC=$?
if [ $RC -eq 0 ] && [ -f vivado_ascon/ascon_cw305_top.bit ]; then
    SIZE=$(stat -c%s vivado_ascon/ascon_cw305_top.bit 2>/dev/null || stat -f%z vivado_ascon/ascon_cw305_top.bit 2>/dev/null)
    echo "[+] BUILD OK — bitstream: vivado_ascon/ascon_cw305_top.bit ($SIZE bytes)"
    echo "[+] Run:  python3 sanity_check.py"
else
    echo "[!] BUILD FAILED (exit=$RC) — check $OUTDIR/rebuild4.stdout"
    exit 1
fi
