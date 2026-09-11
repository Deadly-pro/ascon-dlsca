#!/usr/bin/env bash
# capture_sprint.sh — board-time sprint (deadline 4 PM). Captures EVERYTHING
# the weekend analysis needs, in priority order, then stops.
#
# Rationale: all captures are FIXED-KEY. With a known key there is no
# hypothesis search, so CPA can correlate against the true intermediate
# directly (maximum sensitivity), and the Sep-7 key-write bus artifact
# (|r|~0.4-0.6 on random-key captures) becomes a CONSTANT that cancels.
#
# Detection floor for known-key CPA:  rho_min = 3.4 / sqrt(N*M)
#   today (N=5000, M=1)        -> 0.048   (calibrated: measured 0.045)
#   Run A (N=2048, M=64)       -> 0.0094  (~5x deeper, ~14 dB)
#
# Priority order — if time runs out, whatever completed is still useful:
#   A  main decisive scan        131k captures  ~46 min
#   B  second key (replication)   33k captures  ~12 min
#   C  5 MHz crypto (8 samp/cyc)  16k captures   ~6 min
#   D  extclk phase-coherent      16k captures   ~6 min
#   E  200 MS/s (20 samp/cyc)      8k captures   ~3 min
set -u
cd "$(dirname "$0")/.." || exit 1
OUT=board_session/sprint
PY=.venv/bin/python
LOG=$OUT/sprint.log
mkdir -p "$OUT"
K1=0123456789abcdef0123456789abcdef
K2=a45f8bcdab3d569e1ee091e0d29f2ab7

say() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

run() {   # run <name> <extra args...>
  local name=$1; shift
  say "START $name : $*"
  if $PY collect_dataset.py --offset 700 --gain 50 -s 2000 \
        -o "$OUT/$name.h5" "$@" >>"$LOG" 2>&1; then
    local n
    n=$($PY -c "import h5py;print(h5py.File('$OUT/$name.h5','r')['traces'].shape[0])" 2>/dev/null || echo 0)
    say "DONE  $name : $n traces"
    [ "$n" -gt 0 ] || say "WARN  $name saved 0 traces — check clip/flat in log"
  else
    say "FAIL  $name (nonzero exit) — continuing"
  fi
}

# ---- gate: board must still be KAT-clean (replug => stock AES risk) --------
say "gate: sanity_check"
if ! $PY sanity_check.py -b vivado_ascon/ascon_cw305_top.bit >>"$LOG" 2>&1; then
  say "ABORT: sanity_check failed (reflash / replug, then rerun)"
  exit 1
fi
say "gate: sanity_check PASSED"

# ---- preflight: 8 traces, confirm no clipping at offset 700 ----------------
say "preflight 8 traces"
$PY collect_dataset.py --key $K1 -n 8 -M 4 --offset 700 --gain 50 -s 2000 \
    -o "$OUT/preflight.h5" >>"$LOG" 2>&1 || true
PRE=$($PY -c "
import h5py
try:
    with h5py.File('$OUT/preflight.h5','r') as d:
        print(d['traces'].shape[0], int(d.attrs.get('clipped_rejected',0)),
              int(d.attrs.get('flat_rejected',0)))
except Exception:
    print('0 999 999')
" 2>/dev/null || echo "0 999 999")
set -- $PRE
say "preflight: saved=$1 clip=$2 flat=$3"
if [ "$1" -lt 4 ]; then
  say "ABORT: preflight saved <4 traces (clip=$2 flat=$3). Offset/gain wrong —"
  say "       try: --gain 45 (and confirm you are NOT on stock AES config)."
  exit 1
fi

# ---- A: main decisive scan ------------------------------------------------
run A_fixedkey_K1_N2048_M64 --key $K1 -n 2048 -M 64

# ---- B: second key (cross-key replication) --------------------------------
run B_fixedkey_K2_N512_M64  --key $K2 -n 512  -M 64

# ---- C: slower crypto, 8 samples/cycle at 40 MS/s -------------------------
run C_K1_5mhz_N512_M32 --key $K1 --crypto-mhz 5 -n 512 -M 32 -s 4000

# ---- D: phase-coherent ADC (extclk) ---------------------------------------
run D_K1_extclk_N512_M32 --key $K1 --extclk -n 512 -M 32

# ---- E: high sample rate, 20 samples/cycle --------------------------------
run E_K1_200msps_N512_M16 --key $K1 --fs 200 -n 512 -M 16

# ---- summary ---------------------------------------------------------------
say "==== SPRINT SUMMARY ===="
$PY - <<'PYEOF' 2>&1 | tee -a "$LOG"
import glob, h5py, os
for f in sorted(glob.glob('board_session/sprint/*.h5')):
    try:
        with h5py.File(f,'r') as d:
            a=dict(d.attrs); sh=d['traces'].shape
        print(f'  {os.path.basename(f):34s} n={sh[0]:5d} T={sh[1]:5d} '
              f'fs={a.get("fs_hz",0)/1e6:.0f}MHz crypto={a.get("crypto_clk_hz",0)/1e6:.1f}MHz '
              f'M={a.get("avg_m",1)} key={a.get("key_mode")} '
              f'clip={a.get("clipped_rejected")} flat={a.get("flat_rejected")}')
    except Exception as e:
        print(f'  {os.path.basename(f)}: ERR {e}')
PYEOF
say "sprint complete — safe to disconnect the board"
