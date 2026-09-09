#!/usr/bin/env bash
# train64_natural.sh — train all 64 sbox columns on profiling.npz (NATURAL
# labels, fixed labels.py = board-verified oracle domain) and stage to
# board_session/pa_assets/models/c{col}.pt for git pull on the board PC.
set -u
NPZ="training/data/profiling.npz"
DST="board_session/pa_assets/models"
VENV=".venv/bin/python"
[ -x "$VENV" ] || VENV="python3"
mkdir -p "$DST" training/models
rm -f training/models/profiling_c*_sbox_cnn1.pt
ok=0; fail=0
for c in $(seq 0 63); do
  out=$("$VENV" training/train.py "$NPZ" --target sbox --column "$c" --arch cnn1 --epochs 40 2>&1)
  rc=$?
  acc=$(echo "$out" | grep -oE 'BEST val [0-9.]+ %' | tail -1)
  echo "col $c: rc=$rc $acc"
  if [ $rc -eq 0 ]; then ok=$((ok+1)); else fail=$((fail+1)); fi
done
echo "TRAINED=$ok FAILED=$fail"
for c in $(seq 0 63); do
  cp "training/models/profiling_c${c}_sbox_cnn1.pt" "$DST/c${c}.pt" 2>/dev/null
done
echo "STAGED: $(ls "$DST" 2>/dev/null | wc -l)/64 in $DST"
