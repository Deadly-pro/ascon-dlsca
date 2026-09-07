#!/usr/bin/env bash
# scan_voltages.sh — Phase 1 of the Monday plan: voltage envelope + PA probe
# in one paste. For each voltage: set VCCINT + KAT-gate; if KAT passes,
# capture a 300-trace M=16 random-key probe set. Stops descending at the
# first KAT failure (that's the FI marginality frontier).
#
# Usage:  bash board_session/scan_voltages.sh
# Output: Dataset/vprobe_<v>.h5 for each KAT-passing voltage, plus
#         board_session/vscan.log (full console record for the paper)

set -u
cd "$(dirname "$0")/.."
mkdir -p board_session
LOG=board_session/vscan.log
: > "$LOG"

# Reset scope clock state left over from any prior glitch session.
# Friday's glitch run leaves hs2='glitch'; collect_dataset.py then gets
# no tio4 trigger because the crypto clock never reaches the FPGA.
echo "[+] Resetting scope/target clock state..." | tee -a "$LOG"
python3 - <<'PYEOF' 2>&1 | tee -a "$LOG"
import chipwhisperer as cw
import sys, time
try:
    scope = cw.scope()
    scope.io.hs2 = 'clkgen'
    scope.dis()
    print('[+] scope hs2 -> clkgen')
except Exception as e:
    print(f'[!] scope reset warn: {e}')
try:
    target = cw.target(None, cw.targets.CW305, force=True,
                       bsfile=None, fpga_id='100t', platform='cw305')
    target.fpga_write(0x00, [0x19])   # REG_CLKSETTINGS = PLL1 mode
    target.dis()
    print('[+] REG_CLKSETTINGS=0x19 written')
except Exception as e:
    print(f'[!] target reset warn: {e}')
PYEOF

for V in 1.00 0.97 0.95 0.92 0.90 0.88; do
  echo "===== VCCINT ${V} V =====" | tee -a "$LOG"
  TAG=$(echo "$V" | tr -d '.')

  # set + KAT gate; script exits 1 (and restores 1.0V) if core fails
  if ! python3 set_vccint.py --vcc "$V" --kat 2>&1 | tee -a "$LOG"; then
    echo "[!] KAT FAILED at ${V} V — envelope frontier found. Stopping descent." | tee -a "$LOG"
    python3 set_vccint.py --vcc 1.00
    break
  fi

  # 300-trace M=16 probe capture (random keys, bitstream resident)
  python3 collect_dataset.py -n 300 -M 16 --gain 35 --no-program \
      -o "Dataset/vprobe_${TAG}.h5" 2>&1 | tee -a "$LOG" || {
    echo "[!] capture failed at ${V} V — skipping" | tee -a "$LOG"
  }
done

# leave the board at the last good voltage (FI wants it) — do NOT restore 1.0
# here; the FI phase runs at the frontier. Restore happens at end of session.
echo "[i] scan done. Probe files:" | tee -a "$LOG"
ls -la Dataset/vprobe_*.h5 2>/dev/null | tee -a "$LOG"

# offline analysis (no board interaction) — per-voltage floor-gate verdict
for F in Dataset/vprobe_*.h5; do
  [ -e "$F" ] || continue
  echo "--- probe: $F ---" | tee -a "$LOG"
  .venv/bin/python training/preprocess.py "$F" 2>&1 | tail -3 | tee -a "$LOG"
  NPZ="training/data/$(basename "${F%.h5}").npz"
  .venv/bin/python training/probe_leakage.py "$NPZ" 2>&1 \
      | grep -E "col [0-9]+:|byte [0-9]+:|VERDICT|averaging" | tee -a "$LOG"
done

echo ""
echo "=== DECISION RULE ==="
echo "V_PA  = voltage with MOST 'LEAKS' lines above (max columns over floor)"
echo "V_FI  = LOWEST KAT-passing voltage from the scan (marginality frontier)"
echo "If all flat: V_PA = 1.00, V_FI = lowest scanned."
