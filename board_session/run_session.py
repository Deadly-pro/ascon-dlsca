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


def collect(n, gain, out, crypto_mhz=10.0, program=True, extclk=False):
    cmd = ['collect_dataset.py', '-b', BIT]
    if not program:
        cmd.append('--no-program')
    cmd += ['-n', str(n), '--samples', '1200', '--crypto-mhz', str(crypto_mhz),
            '-o', out, '--gain', str(gain), '--max-retry', '10']
    if extclk:
        cmd += ['--extclk']
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

    # ---- Phase 1: config hunt — gain × clock × phase-lock (10 min) ----
    # New fast core's S-box leak lives in ~5 samples; free-running ADC jitter
    # smears it to zero. extclk (ADC locked to crypto clock) is the fix.
    step('PHASE 1: config hunt — (gain, mhz, extclk) edge at M=1')
    configs = [(35, 10, True), (30, 10, True), (35, 5, True),
               (35, 10, False), (30, 10, False)]
    best_gain, best_edge = 35, -1.0
    best_cfg = (35, 10, False)
    crypto_mhz = 10.0
    for g, mhz, ext in configs:
        tag = 'extclk' if ext else 'clkgen'
        h5 = os.path.join(OUT, 'cfg_g%d_%dmhz_%s.h5' % (g, mhz, tag))
        rc, _ = collect(500, g, h5, crypto_mhz=mhz, extclk=ext,
                        program=(mhz != 10.0 or ext))
        if rc != 0:
            log('  !! collect failed g%d %dmhz %s' % (g, mhz, tag))
            continue
        rc, etext = run(['training/template_edge.py', '--h5', h5,
                         '--n', '500', '--fit-k', '350'])
        e = edge_of(etext)
        log('  => g%d %dMHz %s edge = %+.4f nats' % (g, mhz, tag, e))
        if e > best_edge:
            best_gain, best_edge, best_cfg = g, e, (g, mhz, ext)
            crypto_mhz = float(mhz)
    g, mhz, ext = best_cfg
    log('[[ BEST: gain=%d %.0fMHz %s edge=%+.4f ]]'
        % (g, mhz, 'extclk' if ext else 'clkgen', best_edge))

    # ---- Decision: no leak anywhere -> negative verdict ----
    if best_edge < 0.02:
        verdict('no_leak: edge < 0.02 across gain/clock/phase-lock grid '
                'best=%d %.0fMHz edge=%+.4f' % (best_gain, crypto_mhz,
                                                best_edge))
        log('  New rprimas core: no measurable first-order S-box leak at any '
            'capture config. Not an attack problem — RTL/SNR floor.')
        return 0

    g, mhz, ext = best_cfg
    profile_h5 = os.path.join(OUT, 'cfg_g%d_%dmhz_%s.h5'
                              % (g, mhz, 'extclk' if ext else 'clkgen'))

    # ---- Phase 2: edge vs M ----
    step('PHASE 2: edge vs M-averaging (gain %d, %.0f MHz, %s)'
         % (best_gain, crypto_mhz, 'extclk' if ext else 'clkgen'))
    out = os.path.join(OUT, 'edge_vs_m.h5')
    cmd = ['training/edge_vs_m.py', '--profile-h5', profile_h5,
           '--gain', str(best_gain), '--samples', '1200',
           '--M-max', '64', '--nonces', '30',
           '--crypto-mhz', str(crypto_mhz), '--out', out]
    if ext:
        cmd.append('--extclk')
    run(cmd, timeout=2400)

    # ---- Phase 3: profiling set ----
    step('PHASE 3: profiling set (5000 traces, gain %d, %.0f MHz, %s)'
         % (best_gain, crypto_mhz, 'extclk' if ext else 'clkgen'))
    prof = os.path.join(OUT, 'profiling.h5')
    collect(5000, best_gain, prof, crypto_mhz=crypto_mhz, extclk=ext,
            program=True)

    # ---- Phase 4: template attack ----
    step('PHASE 4: template attack (M=64, 120 queries, 2 episodes)')
    attack = os.path.join(OUT, 'attack_session.h5')
    cmd = ['training/live_loop_transformer.py', '--evidence', 'template',
           '--profile-h5', prof, '--integrator', 'naive', '--M', '64',
           '--retries', '128', '--gain', str(best_gain),
           '--episodes', '2', '--max-queries', '120',
           '--crypto-mhz', str(crypto_mhz), '--save-h5', attack]
    if ext:
        cmd.append('--extclk')
    run(cmd, timeout=1800)

    # ---- Summary ----
    step('SESSION SUMMARY')
    log('  best gain:   %d' % best_gain)
    log('  crypto:      %.0f MHz' % crypto_mhz)
    log('  phase lock:  %s' % ('extclk' if ext else 'clkgen'))
    log('  edge M=1:    %+.4f nats' % best_edge)
    log('  log:         %s' % LOG_PATH)
    log('  outputs:     %s' % OUT)
    verdict('complete gain=%d crypto=%.0fMHz phase=%s edge=%+.4f'
            % (best_gain, crypto_mhz, 'extclk' if ext else 'clkgen',
               best_edge))
    return 0


if __name__ == '__main__':
    sys.exit(main())
