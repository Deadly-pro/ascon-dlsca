#!/usr/bin/env bash
# rerun_failed.sh — re-capture the two sprint runs that failed.
#
#   D: extclk  — failed because chipwhisperer 6.0.0 has no
#      scope.clock.target_freq setter; the ADC fell back to the system clock
#      (silently not phase-coherent).  scope_config.setup_scope_clock fixed.
#   E: 200 MS/s — all 512 traces clipped at the rail.  The ADC front-end
#      settles differently at 200 MS/s, so gain 50 / offset 700 is wrong for
#      it.  We probe gains to find a non-clipping setting first.
set -u
cd "$(dirname "$0")/.." || exit 1
OUT=board_session/sprint
PY=.venv/bin/python
LOG=$OUT/rerun.log
K1=0123456789abcdef0123456789abcdef
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

probe() {   # probe <label> <args...> -> prints "saved clip flat"
  local label=$1; shift
  $PY collect_dataset.py --key $K1 -n 8 --offset 700 -s 2000 \
      -o "$OUT/probe.h5" "$@" >>"$LOG" 2>&1 || true
  $PY -c "
import h5py
try:
    with h5py.File('$OUT/probe.h5','r') as d:
        a=dict(d.attrs); print(d['traces'].shape[0], int(a.get('clipped_rejected',0)), int(a.get('flat_rejected',0)))
except Exception:
    print('0 999 999')
" 2>/dev/null || echo "0 999 999"
}

# ---------------------------------------------------------------- D: extclk
say "=== D: extclk probe (8 traces, M=2) ==="
read -r SV CL FL <<<"$(probe extclk --extclk -M 2)"
say "extclk probe: saved=$SV clip=$CL flat=$FL"
$PY - <<'PYEOF' >>"$LOG" 2>&1
# report what clock the scope actually landed on
import chipwhisperer as cw
from scope_config import configure_scope, is_husky
s = configure_scope(gain=50, samples=2000, offset=700, sample_rate=40e6,
                    extclk=True, crypto_hz=10e6)
print(f'  clkgen_src={s.clock.clkgen_src}  adc_freq={s.clock.adc_freq/1e6:.2f}MHz  '
      f'adc_mul={s.clock.adc_mul}  clkgen_freq={s.clock.clkgen_freq/1e6:.2f}MHz')
s.dis()
PYEOF
tail -2 "$LOG" | sed 's/^/    /'

if [ "$SV" -ge 4 ]; then
  say "START D2_extclk_N512_M32 (full)"
  if $PY collect_dataset.py --key $K1 --extclk -n 512 -M 32 --offset 700 \
        --gain 50 -s 2000 -o "$OUT/D2_extclk_N512_M32.h5" >>"$LOG" 2>&1; then
    say "DONE D2_extclk_N512_M32"
  else
    say "FAIL D2_extclk_N512_M32"
  fi
else
  say "SKIP D2: extclk probe unusable (clip=$CL) — needs clock debugging"
fi

# ---------------------------------------------------------------- E: 200 MS/s
say "=== E: 200 MS/s gain probe ==="
E_GAIN=""
for g in 40 30 20 10; do
  read -r SV CL FL <<<"$(probe "200msps_g$g" --fs 200 -M 2 --gain $g)"
  say "  200MS/s gain=$g -> saved=$SV clip=$CL flat=$FL"
  if [ "$SV" -ge 6 ] && [ "$CL" -le 1 ]; then E_GAIN=$g; break; fi
done

if [ -n "$E_GAIN" ]; then
  say "START E2_200msps_N512_M16 (gain=$E_GAIN)"
  if $PY collect_dataset.py --key $K1 --fs 200 -n 512 -M 16 --offset 700 \
        --gain "$E_GAIN" -s 2000 -o "$OUT/E2_200msps_N512_M16.h5" >>"$LOG" 2>&1; then
    say "DONE E2_200msps_N512_M16"
  else
    say "FAIL E2_200msps_N512_M16"
  fi
else
  say "SKIP E2: no 200 MS/s gain produced clean traces"
fi

say "=== rerun summary ==="
$PY - <<'PYEOF' 2>&1 | tee -a "$LOG"
import glob, h5py, os
for f in sorted(glob.glob('board_session/sprint/D2*.h5') +
                glob.glob('board_session/sprint/E2*.h5')):
    with h5py.File(f,'r') as d:
        a=dict(d.attrs); sh=d['traces'].shape
    print(f'  {os.path.basename(f):32s} n={sh[0]:4d} T={sh[1]:5d} '
          f'fs={a.get("fs_hz",0)/1e6:.0f}MHz M={a.get("avg_m")} '
          f'clip={a.get("clipped_rejected")} flat={a.get("flat_rejected")}')
PYEOF
say "rerun complete"
