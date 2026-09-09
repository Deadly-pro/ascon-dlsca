#!/usr/bin/env bash
# train64.sh — train all 64 sbox columns from profiling_relabel.npz into
# board_session/pa_assets/models/c{col}.pt (git-tracked for board-PC pull).
set -u
NPZ="training/data/profiling_relabel.npz"
DST="board_session/pa_assets/models"
VENV=".venv/bin/python"
[ -x "$VENV" ] || VENV="python3"
mkdir -p "$DST" training/models
ok=0; skip=0; fail=0
for c in $(seq 0 63); do
  model="training/models/profiling_c${c}_sbox_cnn1.pt"
  if [ -f "$model" ]; then
    echo "col $c: model exists — skip"; skip=$((skip+1)); continue
  fi
  out=$("$VENV" training/train.py "$NPZ" --target sbox --column "$c" --arch cnn1 --epochs 40 2>&1)
  rc=$?
  acc=$(echo "$out" | grep -oE 'BEST val [0-9.]+ %' | tail -1)
  echo "col $c: rc=$rc $acc"
  if [ $rc -eq 0 ]; then ok=$((ok+1)); else fail=$((fail+1)); fi
done
echo "DONE: trained=$ok skipped=$skip failed=$fail"
# stage into git-tracked assets dir as c{col}.pt (scores_export model-frm format)
for c in $(seq 0 63); do
  cp "training/models/profiling_c${c}_sbox_cnn1.pt" "$DST/c${c}.pt" 2>/dev/null
done
echo "staged: $(ls $DST | wc -l)/64 models in $DST"
