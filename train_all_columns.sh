#!/usr/bin/env bash
# train_all_columns.sh — train cnn1 profile for all 64 S-box columns from an
# existing npz. Skips columns whose model file already exists (resume-safe).
# Usage: bash train_all_columns.sh [npz] [epochs]
set -u
NPZ="${1:-training/data/profiling.npz}"
EPOCHS="${2:-40}"
VENV=".venv/bin/python"
[ -x "$VENV" ] || VENV="python3"
mkdir -p training/models training/results
ok=0; skip=0; fail=0
for c in $(seq 0 63); do
  model="training/models/profiling_c${c}_sbox_cnn1.pt"
  if [ -f "$model" ]; then
    echo "col $c: model exists — skip"
    skip=$((skip+1)); continue
  fi
  out=$("$VENV" training/train.py "$NPZ" --target sbox --column "$c" --arch cnn1 --epochs "$EPOCHS" 2>&1)
  rc=$?
  acc=$(echo "$out" | grep -oE 'BEST val [0-9.]+ %' | tail -1)
  echo "col $c: rc=$rc $acc"
  if [ $rc -eq 0 ]; then ok=$((ok+1)); else fail=$((fail+1)); fi
done
echo "DONE: trained=$ok skipped=$skip failed=$fail"
