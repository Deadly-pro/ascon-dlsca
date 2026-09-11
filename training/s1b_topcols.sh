#!/usr/bin/env bash
# S1b — multi-key validation on the top-3 fine-tuned columns
# (c42: 79%, c38: 67%, c59: 64% train-acc) to see if ANY column tracks the key.
cd /home/deadly-pro/ascon-dlsca
for c in 42 38 59; do
  echo "=================== column $c ==================="
  .venv/bin/python training/s1_multikey_validate.py \
      --model "board_session/pa_assets/models/c${c}_liveft.pt" \
      --column "$c" --queries 20 2>&1 | grep -v WARNING
done
