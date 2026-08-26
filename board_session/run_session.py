#!/usr/bin/env python3
r"""run_session.py — cross-platform (Windows/Linux) 1-hour board session.

The single source of truth for the conclusive session on the new unmasked
rprimas core. Works identically on Windows (cmd/PowerShell) and Linux.
Thin wrappers: board_session/run_session.bat and board_session/run_session.sh.

Phases:
  0. verify_state gate (5/5 observability required)
  1. gain sweep 30..50 -> template edge at M=1, pick best gain
  1b. if edge < 0.02 everywhere: 5 MHz crypto contingency
  2. edge vs M-averaging at best gain (one pass, M=1..64)
  3. 5000-trace profiling set at best gain
  4. template attack (M=64, 120 queries, 2 episodes)

Logs to board_session/run_<ts>/session.log, writes verdict.txt.
"""
import datetime
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIT = os.path.join(ROOT, 'vivado_ascon', 'ascon_cw305_top.bit')


def venv_python():
    if os.name == 'nt':
        p = os.path.join(ROOT, '.venv', 'Scripts', 'python.exe')
    else:
        p = os.path.join(ROOT, '.venv', 'bin', 'python')
    return p if os.path.exists(p) else sys.executable


PY = venv_python()
OUT = os.path.join(ROOT, 'board_session', 'run_%s' %
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
    """Run a python tool, tee output to the log, return (rc, full_text)."""
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
    return (proc.returncode if proc else -1), text


def edge_of(text):
    m = re.search(r'mean ([+-]?\d+\.\d+) nats', text)
    return float(m.group(1)) if m else -1.0


def collect(n, gain, out, crypto_mhz=10.0, program=True):
    cmd = ['collect_dataset.py', '-b', BIT]
    if not program:
        cmd.append('--no-program')
    cmd += ['-n', str(n), '--samples', '1200', '--crypto-mhz', str(crypto_mhz),
            '-o', out, '--gain', str(gain), '--max-retry', '10']
    return run(cmd)


def verdict(text):
    with open(os.path.join(OUT, 'verdict.txt'), 'w') as f:
        f.write(text + '\n')
    log('VERDICT: %s' % text)


def main():
    log('session out dir: %s' % OUT)
    log('python: %s' % PY)
    log('bitstream: %s' % BIT)

    # ---- Phase 0: gate ----
    step('PHASE 0: verify_state — observability gate (5/5 required)')
    rc, text = run(['verify_state.py', '-b', BIT, '-n', '5'])
    if '5/5 state readbacks match oracle exactly' not in text:
        verdict('fail verify_state gate — reflash and retry once')
        return 1
    log('gate passed')

    # ---- Phase 1: gain sweep ----
    step('PHASE 1: gain sweep (30 35 40 45 50), template edge at M=1')
    best_gain, best_edge = 35, -1.0
    gain_files = {}
    for g in (30, 35, 40, 45, 50):
        h5 = os.path.join(OUT, 'gain_%d.h5' % g)
        rc, _ = collect(300, g, h5, program=False)
        if rc != 0:
            log('  !! collect failed at gain %d' % g)
            continue
        rc, etext = run(['training/template_edge.py', '--h5', h5,
                         '--n', '300', '--fit-k', '200'])
        e = edge_of(etext)
        gain_files[g] = h5
        log('  => gain %d edge = %+.4f nats' % (g, e))
        if e > best_edge:
            best_gain, best_edge = g, e
    log('[[ BEST: gain=%d edge=%+.4f ]]' % (best_gain, best_edge))

    crypto_mhz = 10.0
    profile_h5 = os.path.join(OUT, 'gain_%d.h5' % best_gain)

    # ---- Phase 1b: 5 MHz contingency ----
    if best_edge < 0.02:
        step('PHASE 1b: 5 MHz contingency at gain %d' % best_gain)
        h5 = os.path.join(OUT, 'gain_%d_5mhz.h5' % best_gain)
        rc, _ = collect(300, best_gain, h5, crypto_mhz=5, program=True)
        rc, etext = run(['training/template_edge.py', '--h5', h5,
                         '--n', '300', '--fit-k', '200'])
        e5 = edge_of(etext)
        log('  => 5 MHz edge = %+.4f nats' % e5)
        if e5 < 0.02:
            verdict('no_leak: edge < 0.02 at all gains AND both clocks '
                    '(gain=%d edge_10mhz=%+.4f edge_5mhz=%+.4f)'
                    % (best_gain, best_edge, e5))
            log('  Bitstream not leaking first-order S-box signal. '
                'Check verify_state, trigger timing, RTL/masking.')
            return 0
        best_edge, crypto_mhz = e5, 5.0
        profile_h5 = h5
        log('[[ 5 MHz: edge=%+.4f — proceeding ]]' % best_edge)

    # ---- Phase 2: edge vs M ----
    step('PHASE 2: edge vs M-averaging (gain %d, %.0f MHz)'
         % (best_gain, crypto_mhz))
    out = os.path.join(OUT, 'edge_vs_m.h5')
    run(['training/edge_vs_m.py', '--profile-h5', profile_h5,
         '--gain', str(best_gain), '--samples', '1200',
         '--M-max', '64', '--nonces', '30',
         '--crypto-mhz', str(crypto_mhz), '--out', out], timeout=2400)

    # ---- Phase 3: profiling set ----
    step('PHASE 3: profiling set (5000 traces, gain %d, %.0f MHz)'
         % (best_gain, crypto_mhz))
    prof = os.path.join(OUT, 'profiling.h5')
    collect(5000, best_gain, prof, crypto_mhz=crypto_mhz,
            program=(crypto_mhz != 10.0))

    # ---- Phase 4: template attack ----
    step('PHASE 4: template attack (M=64, 120 queries, 2 episodes)')
    attack = os.path.join(OUT, 'attack_session.h5')
    run(['training/live_loop_transformer.py', '--evidence', 'template',
         '--profile-h5', prof, '--integrator', 'naive', '--M', '64',
         '--retries', '128', '--gain', str(best_gain),
         '--episodes', '2', '--max-queries', '120',
         '--crypto-mhz', str(crypto_mhz), '--save-h5', attack],
        timeout=1800)

    # ---- Summary ----
    step('SESSION SUMMARY')
    log('  best gain:  %d' % best_gain)
    log('  crypto:     %.0f MHz' % crypto_mhz)
    log('  edge M=1:   %+.4f nats' % best_edge)
    log('  log:        %s' % LOG_PATH)
    log('  outputs:    %s' % OUT)
    verdict('complete gain=%d crypto=%.0fMHz edge=%+.4f'
            % (best_gain, crypto_mhz, best_edge))
    return 0


if __name__ == '__main__':
    sys.exit(main())
