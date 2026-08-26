#!/usr/bin/env bash
# run_session.sh — 1-hour conclusive board session for the new unmasked rprimas core.
# Phases with time budget, decision tree, and logging.
# Run from repo root:  bash board_session/run_session.sh
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TS=$(date +%Y%m%d_%H%M%S)
OUT="$ROOT/board_session/run_$TS"
mkdir -p "$OUT"
LOG="$OUT/session.log"
exec > >(tee -a "$LOG") 2>&1
START=$(date +%s)
BIT="$ROOT/vivado_ascon/ascon_cw305_top.bit"
VENV="$ROOT/.venv/bin/python"
PGM="--no-program"           # set after first program; cleared for clock-change rows

step() { echo; echo "=== $1 ==="; date +%H:%M:%S; }
elapsed() { echo "[elapsed $(( ($(date +%s)-START)/60 )) min]"; }
fatalf() { echo "!! FATAL: $1"; echo "VERDICT fail $1" > "$OUT/verdict.txt"; exit 1; }

# ---- Phase 0: gate (2 min) ----
step "PHASE 0: verify_state — observability gate (5/5 required)"
VOUT=$($VENV "$ROOT/verify_state.py" -b "$BIT" -n 5 2>&1); echo "$VOUT"
echo "$VOUT" | grep -q "5/5 state readbacks match oracle exactly" \
  || fatalf "verify_state gate failed — reflash and retry once"
echo "  bitstream $BIT"
elapsed

# ---- Phase 1: gain sweep — template edge at M=1 (10 min) ----
step "PHASE 1: gain sweep (gain 30 35 40 45 50, 300 traces each, template edge)"
BEST_GAIN=35; BEST_EDGE=-1.0
for g in 30 35 40 45 50; do
    step "  gain $g — collect 300, fit template, measure edge"
    $VENV "$ROOT/collect_dataset.py" -b "$BIT" $PGM -n 300 --samples 1200 \
        -o "$OUT/gain_${g}.h5" --gain $g --max-retry 10
    EOUT=$($VENV "$ROOT/training/template_edge.py" --h5 "$OUT/gain_${g}.h5" \
        --n 300 --fit-k 200 2>&1)
    echo "$EOUT"
    E=$(echo "$EOUT" | grep -oP 'mean [+-]?\d+\.\d+ nats' | head -1 | grep -oP '[+-]?\d+\.\d+')
    echo "  => gain $g edge = $E nats"
    if (( $(echo "$E > $BEST_EDGE" | bc -l 2>/dev/null) )); then
        BEST_EDGE=$E; BEST_GAIN=$g
    fi
    elapsed
done
echo "[[ BEST: gain=$BEST_GAIN at edge=$BEST_EDGE nats ]]"

# ---- Decision branch — does the core leak? ----
if (( $(echo "$BEST_EDGE < 0.02" | bc -l) )); then
    echo "[[ Edge < 0.02 at all 10 MHz gains — trying 5 MHz crypto ]]"
    step "PHASE 1b: 5 MHz contingency — collect 300 at gain $BEST_GAIN, 5 MHz"
    PGM=""  # need to program with new PLL freq
    $VENV "$ROOT/collect_dataset.py" -b "$BIT" -n 300 --samples 1200 \
        --crypto-mhz 5 -o "$OUT/gain_${BEST_GAIN}_5mhz.h5" --gain $BEST_GAIN --max-retry 10
    EOUT5=$($VENV "$ROOT/training/template_edge.py" --h5 "$OUT/gain_${BEST_GAIN}_5mhz.h5" \
        --n 300 --fit-k 200 2>&1)
    echo "$EOUT5"
    E5=$(echo "$EOUT5" | grep -oP 'mean [+-]?\d+\.\d+ nats' | head -1 | grep -oP '[+-]?\d+\.\d+')
    if (( $(echo "$E5 < 0.02" | bc -l) )); then
        echo "VERDICT no_leak: edge M=1 < 0.02 nats at ALL gains AND both clocks."
        echo "  The bitstream is not leaking first-order S-box signal."
        echo "  Causes: RTL synthesis collapsed masking, wrong bitstream,"
        echo "  trigger timing misses the encryption burst, or ADC saturating."
        echo "no_leak gain=$BEST_GAIN edge_10mhz=$BEST_EDGE edge_5mhz=$E5" > "$OUT/verdict.txt"
        echo "  Check: verify_state, capture variance profile, rebuild."
        fatalf "no leakage detected — session conclusive but negative"
    fi
    BEST_EDGE=$E5
    CRYPTO_MHZ=5
    PROF_H5="$OUT/gain_${BEST_GAIN}_5mhz.h5"
    echo "[[ 5 MHz: edge=$BEST_EDGE — proceeding with 5 MHz ]]"
else
    CRYPTO_MHZ=10
    PROF_H5="$OUT/gain_${BEST_GAIN}.h5"
fi
elapsed

# ---- Phase 2: edge vs M-averaging (10 min) ----
step "PHASE 2: edge vs M-averaging at gain $BEST_GAIN, ${CRYPTO_MHZ} MHz"
$VENV "$ROOT/training/edge_vs_m.py" \
    --profile-h5 "$PROF_H5" \
    --gain $BEST_GAIN --samples 1200 --M-max 64 --nonces 30 \
    --crypto-mhz $CRYPTO_MHZ --out "$OUT/edge_vs_m.h5"
elapsed

# ---- Phase 3: profiling set (3 min) ----
step "PHASE 3: profiling set (5000 traces at gain $BEST_GAIN, ${CRYPTO_MHZ} MHz)"
$VENV "$ROOT/collect_dataset.py" -b "$BIT" $PGM -n 5000 --samples 1200 \
    --crypto-mhz $CRYPTO_MHZ -o "$OUT/profiling.h5" --gain $BEST_GAIN --max-retry 10
elapsed

# ---- Phase 4: template attack (10 min) ----
step "PHASE 4: template attack (M=64, 120 queries, 2 episodes, ${CRYPTO_MHZ} MHz)"
$VENV "$ROOT/training/live_loop_transformer.py" \
    --evidence template --profile-h5 "$OUT/profiling.h5" \
    --integrator naive --M 64 --retries 128 \
    --gain $BEST_GAIN --episodes 2 --max-queries 120 \
    --crypto-mhz $CRYPTO_MHZ \
    --save-h5 "$OUT/attack_session.h5"
elapsed

# ---- Summary ----
step "SESSION SUMMARY"
echo "  best gain:   $BEST_GAIN"
echo "  crypto:      ${CRYPTO_MHZ} MHz"
echo "  edge M=1:    $BEST_EDGE nats"
echo "  full log:    $LOG"
echo "  outputs:     $OUT/"
echo "VERDICT complete gain=$BEST_GAIN crypto=${CRYPTO_MHZ}MHz edge=$BEST_EDGE" \
    > "$OUT/verdict.txt"
echo "  Runbook:     board_session/README.md"
echo "DONE $(date)"