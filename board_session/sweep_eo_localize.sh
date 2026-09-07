#!/usr/bin/env bash
# sweep_eo_localize.sh — single-glitch eo sweep, gated on LOCALIZATION rate
# (not tag bit-diff). Keep configs where the known-key localizer matches.
set -u
KEY=8826d916cdfb21c6c1ff91a761565a70
NONCE=22389617c344f98dafbf4ce3e3535610
for eo in 28 30 32 34 36 38 40 42 44 46 48 50; do
  echo "===== eo=$eo ====="
  python3 glitch_collect.py --key "$KEY" --nonce "$NONCE" \
    --ext-offset "$eo" --offset 0 --width 67 \
    --count 150 --num-glitches 1 --out "fi_eo${eo}.npz" 2>&1 \
    | grep -E "Collecting|Localized|DFA recovered|recovered"
done
echo "===== DONE — pick the eo with the highest Localized count ====="
