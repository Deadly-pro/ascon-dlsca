#!/usr/bin/env bash
# hunt_single_localize.sh — SINGLE-glitch nonce hunt, then offline-localize
# every saved band-hit tag with the known key. This is the one untested cell:
# burst was multi-fault, the eo sweep used one nonce. Data-dependent faults
# mean different nonces fault at different cycles -> some may be clean
# round-11 single-bit faults the DFA can eat.
set -u
KEY=8826d916cdfb21c6c1ff91a761565a70
OUT=band_single.npz

echo "===== [1/2] single-glitch nonce hunt (eo 38-47, 20 nonces) ====="
python3 glitch_cal.py --key "$KEY" \
  --nonce-hunt 20 --seed 7 --num-glitches 1 \
  --eo-min 38 --eo-max 47 --width 67 --settle-s 0.02 \
  --output clock_xor --out "$OUT"

echo
echo "===== [2/2] offline localization of every saved hit ====="
timeout 500 .venv/bin/python - <<'PY'
import sys, numpy as np
sys.path.insert(0, 'training'); sys.path.insert(0, '.')
import dfa_bitflip as df

try:
    d = np.load('band_single.npz', allow_pickle=True)
except FileNotFoundError:
    print('[!] band_single.npz not found (no band hits saved?)'); sys.exit(0)
bh = d['band_hits']
if bh.size == 0:
    print('[!] no band hits'); sys.exit(0)
key = d['key'].tobytes()
AD = b'\x00'*4; PT = b'\x00'*4
KEYH = key.hex()

print(f'[+] {len(bh)} band hits, localizing each with known key...')
ok = []
seen = set()
for b in bh:
    nonce_hex, eo, off, w, bd, tag_hex = b[0], int(b[1]), int(b[2]), int(b[3]), int(b[4]), b[5]
    if nonce_hex == KEYH:      # skip the key-as-nonce artifact
        continue
    if tag_hex in seen:        # dedupe identical tags
        continue
    seen.add(tag_hex)
    nonce = bytes.fromhex(nonce_hex)
    loc = df.localize_fault(key, nonce, AD, PT, bytes.fromhex(tag_hex))
    if loc is not None:
        ok.append((nonce_hex, eo, off, w, bd, loc))
        print(f'  LOCALIZED nonce={nonce_hex[:16]}... eo={eo} off={off} '
              f'bitdiff={bd} -> col={loc[0]} bit={loc[1]}')
print(f'[+] {len(ok)} clean single-bit faults from {len(seen)} distinct tags')
if ok:
    print(f'[+] CONFIG TO COLLECT: nonce={ok[0][0]} eo={ok[0][1]} off={ok[0][2]} w=67 num-glitches=1')
else:
    print('[!] No clean single-bit faults at any nonce/eo -> single-bit DFA is dead on this core')
PY
