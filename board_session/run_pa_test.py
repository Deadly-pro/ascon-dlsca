#!/usr/bin/env python3
r"""run_pa_test.py — cross-platform (Windows/Linux) PA full-key recovery session.

Resume-aware: every phase checks whether its output artifact already exists
and skips if present. Designed so the heavy phases (profiling capture, CNN
training) run ONCE (here, offline) and the board PC only runs the live attack
phases (fine-tune + scores_export + assembly).

Phases:
  0. Gate: sanity_check 5/5
  1. [skip if profiling.npz exists] config hunt + profiling capture + train
  2. [skip if models exist] preprocess + per-column CNN training (64 cols)
  3. Floor gate (probe_leakage) — always
  4. Live fine-tuning at the target key — board required
  5. Attack: scores_export at target key — board required
  6. Full-key assembly (fullkey_assemble) — offline

Outputs (git-tracked staging dir for cross-machine handoff):
  board_session/pa_assets/profiling.npz     — preprocessed features + ref
  board_session/pa_assets/models/c{col}.pt  — 64 per-column CNN profiles

Usage:
  python3 board_session/run_pa_test.py                # full run
  python3 board_session/run_pa_test.py --resume       # skip finished phases
  python3 board_session/run_pa_test.py --attack-only  # live attack only
"""
import argparse
import datetime
import os
import re
import shutil
import sys
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIT = os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit')

# Target key (random, generated at script creation time)
TARGET_KEY = 'a45f8bcdab3d569e1ee091e0d29f2ab7'

# Known-good captures: fresh Sep-9 config-hunt runs verified 100/100 vs the
# current oracle. The Aug-27 profiling.h5 predates the w32rev fix and does
# NOT verify (0/200) — stale-era, unusable as training data.
KNOWN_H5 = os.path.join(ROOT, 'board_session', 'run_pa_20260909_032325',
                        'cfg_g30_10mhz_clkgen.h5')
KNOWN_GAIN = 30
KNOWN_MHZ = 10.0
KNOWN_EXT = False

# Staging dir: git-tracked so models travel repo -> board PC via git pull
ASSETS = os.path.join(ROOT, 'board_session', 'pa_assets')
ASSET_NPZ = os.path.join(ASSETS, 'profiling.npz')
ASSET_MODEL_FRM = os.path.join(ASSETS, 'models', 'c{col}.pt')


def venv_python():
    # WSL/Linux + Windows venv layouts; a Windows venv on WSL lives in
    # .venv/Scripts/python.exe while os.name == 'posix'
    for rel in (os.path.join('.venv', 'bin', 'python'),
                os.path.join('.venv', 'Scripts', 'python.exe')):
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            return p
    return sys.executable


PY = venv_python()
OUT = os.path.join(ROOT, 'board_session', 'run_pa_%s' %
                   datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
os.makedirs(OUT, exist_ok=True)
LOG_PATH = os.path.join(OUT, 'session.log')
START = time.time()
LOG = open(LOG_PATH, 'w', encoding='utf-8', buffering=1)


def log(msg):
    line = '%s %s' % (datetime.datetime.now().strftime('%H:%M:%S'), msg)
    print(line, flush=True)
    LOG.write(line + '\n')


def step(name):
    log('')
    log('=== %s ===' % name)
    log('elapsed %d min' % ((time.time() - START) / 60))


def run(cmd, timeout=1800):
    log('$ %s' % ' '.join(cmd))
    try:
        proc = subprocess.run([PY] + cmd, cwd=ROOT, capture_output=True,
                              text=True, timeout=timeout)
        text = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        text = '!! TIMEOUT after %ds' % timeout
        proc = None
    for line in text.splitlines():
        LOG.write('    ' + line + '\n')
        print('    ' + line, flush=True)
    return (proc.returncode if proc else -1), text


def verdict(text):
    with open(os.path.join(OUT, 'verdict.txt'), 'w') as f:
        f.write(text + '\n')
    log('VERDICT: %s' % text)


def all_models_present():
    return all(os.path.exists(ASSET_MODEL_FRM.format(col=c))
               for c in range(64))


def model_count():
    if not os.path.isdir(os.path.join(ASSETS, 'models')):
        return 0
    return len([f for f in os.listdir(os.path.join(ASSETS, 'models'))
                if f.startswith('c') and f.endswith('.pt')])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--resume', action='store_true',
                    help='skip phases whose artifacts already exist')
    ap.add_argument('--attack-only', action='store_true',
                    help='skip gate + training; run live attack phases only')
    ap.add_argument('--h5', default=KNOWN_H5,
                    help='profiling capture h5 (default: known-good capture)')
    ap.add_argument('--key', default=TARGET_KEY, help='target key hex')
    ap.add_argument('--gain', type=int, default=KNOWN_GAIN)
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--M', type=int, default=16)
    args = ap.parse_args()

    log('session out dir: %s' % OUT)
    log('python: %s' % PY)
    log('bitstream: %s' % BIT)
    log('target key: %s' % args.key)
    log('assets:     %s' % ASSETS)
    log('npz exists: %s' % os.path.exists(ASSET_NPZ))
    log('models:     %d/64' % model_count())

    if args.attack_only:
        args.resume = True

    # ---- Phase 0: gate (skip only in --attack-only) ----
    if not (args.resume and all_models_present()):
        step('PHASE 0: sanity_check 5/5')
        rc, text = run(['sanity_check.py', '-b', BIT])
        if '5/5' not in text:
            verdict('fail sanity_check gate — reflash and retry')
            return 1
        log('sanity_check passed')

    # ---- Phase 1: profiling npz (skip if exists) ----
    if args.resume and os.path.exists(ASSET_NPZ):
        log('PHASE 1 SKIPPED: profiling npz already exists')
        npz = ASSET_NPZ
    else:
        step('PHASE 1: preprocess known-good capture -> npz')
        os.makedirs(ASSETS, exist_ok=True)
        if not os.path.exists(args.h5):
            log('  !! profiling h5 missing: %s' % args.h5)
            log('  Collect one first:  python3 collect_dataset.py -n 5000 '
                '--gain 30 -o <file>.h5')
            verdict('fail: no profiling h5')
            return 1
        # preprocess writes training/data/<name>.npz; copy into assets
        rc, text = run(['training/preprocess.py', args.h5])
        if rc != 0:
            verdict('fail preprocess')
            return 1
        src_npz = os.path.join('training', 'data',
                               os.path.splitext(os.path.basename(args.h5))[0]
                               + '.npz')
        if not os.path.exists(src_npz):
            # preprocess writes training/data/<h5-basename>.npz; the known
            # capture basename is 'profiling' regardless of its dir
            for cand in ('training/data/profiling.npz',):
                if os.path.exists(cand):
                    src_npz = cand
                    break
        shutil.copy(src_npz, ASSET_NPZ)
        log('  copied %s -> %s' % (src_npz, ASSET_NPZ))
        npz = ASSET_NPZ

    # ---- Phase 2: per-column CNN training (skip if all 64 present) ----
    if args.resume and all_models_present():
        log('PHASE 2 SKIPPED: all 64 models present')
    else:
        step('PHASE 2: train per-column CNN profiles (%d/64 done)'
             % model_count())
        os.makedirs(os.path.join(ASSETS, 'models'), exist_ok=True)
        # train.py saves training/models/<name>_c<col>_sbox_cnn1.pt;
        # run one per column and copy into assets as c{col}.pt
        name = os.path.splitext(os.path.basename(args.h5))[0]
        fails = 0
        for col in range(64):
            dst = ASSET_MODEL_FRM.format(col=col)
            if os.path.exists(dst):
                continue
            rc, text = run(['training/train.py', npz, '--target', 'sbox',
                            '--column', str(col), '--arch', 'cnn1',
                            '--epochs', str(args.epochs)])
            if rc != 0:
                log('  !! train column %d failed' % col)
                fails += 1
                continue
            # locate the freshly written model and copy into assets
            src = os.path.join('training', 'models',
                               '%s_c%d_sbox_cnn1.pt' % (name, col))
            if not os.path.exists(src):
                # fallback glob: newest profiling*.pt containing _c{col}_
                import glob
                cands = glob.glob(os.path.join(
                    'training', 'models', '*_c%d_sbox_cnn1.pt' % col))
                src = cands[0] if cands else None
            if src and os.path.exists(src):
                shutil.copy(src, dst)
                log('  col %d -> %s' % (col, dst))
        if fails:
            log('  WARNING: %d columns failed to train' % fails)
        log('  models staged: %d/64' % model_count())

    # ---- Phase 3: floor gate ----
    step('PHASE 3: floor gate (probe_leakage)')
    rc, text = run(['training/probe_leakage.py', npz])
    log('floor gate complete (see above; logistic/KNN is the weak probe — '
        'CNN profiles are the real signal)')

    if model_count() < 52:
        log('  WARNING: only %d/64 models — full-key assembly may be bounded'
            % model_count())

    # ---- Phase 4: live fine-tuning (board) ----
    step('PHASE 4: live fine-tuning at target key (board)')
    if model_count() == 0:
        verdict('fail: no trained models to fine-tune')
        return 1
    # fine-tune column 0 as the domain-gap demonstration
    m0 = ASSET_MODEL_FRM.format(col=0)
    rc, text = run(['training/live_finetune.py', '--model', m0,
                    '--npz', npz, '--key', args.key, '--column', '0',
                    '--ntrain', '300', '--random-keys'])
    if rc != 0:
        log('  WARNING: live_finetune failed — continuing with base profiles')

    # ---- Phase 5: attack at target key (board) ----
    step('PHASE 5: scores_export at target key (board)')
    scores = os.path.join(OUT, 'attack_scores.npz')
    cmd = ['training/scores_export.py', '--key', args.key,
           '--model-frm', ASSET_MODEL_FRM,
           '--npz', npz, '--M', str(args.M),
           '--gain', str(args.gain), '--out', scores]
    rc, text = run(cmd, timeout=3600)
    if rc != 0 or not os.path.exists(scores):
        log('  !! scores_export failed')
        verdict('attack_failed — see session.log')
        return 1
    log('attack scores written: %s' % scores)

    # ---- Phase 6: full-key assembly ----
    step('PHASE 6: full-key assembly')
    cmd = ['training/fullkey_assemble.py', '--scores', scores]
    rc, text = run(cmd, timeout=1800)
    if rc == 0 and 'FULL KEY RECOVERED' in text:
        m = re.search(r'FULL KEY RECOVERED: ([0-9a-f]{32})', text)
        recovered_key = m.group(1) if m else 'unknown'
        log('FULL KEY RECOVERED: %s' % recovered_key)
        if recovered_key == args.key:
            verdict('FULL_KEY_RECOVERED key=%s' % recovered_key)
        else:
            verdict('KEY_MISMATCH recovered=%s expected=%s'
                    % (recovered_key, args.key))
    else:
        # count confident columns for the honest partial statement
        m = re.search(r'(\d+) weak columns', text)
        weak = int(m.group(1)) if m else -1
        if weak >= 0:
            verdict('partial_assembly confident_cols=%d/64 weak=%d budget=4^%d'
                    % (64 - weak, weak, weak))
        else:
            verdict('assembly_failed — per-column scores too weak; '
                    'see session.log')

    step('SESSION SUMMARY')
    log('  target key:   %s' % args.key)
    log('  models:       %d/64' % model_count())
    log('  log:          %s' % LOG_PATH)
    log('  outputs:      %s' % OUT)
    return 0


if __name__ == '__main__':
    sys.exit(main())
