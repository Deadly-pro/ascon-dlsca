#!/usr/bin/env python3
r"""step4b_mavg_offline.py — how much trace averaging M buys, offline.

The board experiments showed M=64 averaging lifts rank-1 0.25 -> 0.94 for
the fine-tuned column. Question answered here for the OFFLINE capture:
group random-key traces by key (each key repeats across nonces), average
groups of size M, and re-run the step-2 LDA scorer per column.

If offline M-averaging does NOT lift above floor either, the conclusion is
that the unmasked capture's first-order SNR is below what M<=16 can rescue
(the board M=64 result came from a fine-tuned profile + separating nonces,
a different regime), and the attack path REQUIRES on-board adaptation.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from step2_poi_denoise import lda_eval, zscore  # noqa: E402
from step1b_null_floor import hw_pred_for       # noqa: E402
from step1_cpa_hd import true_hyp               # noqa: E402


def group_avg_by_key(keys, nonces, traces, M, seed=0):
    """Group traces sharing the same key; average M nonce-variants per key.
    Returns avg traces (G, S), keys (G,16), and per-group member indices."""
    rng = np.random.default_rng(seed)
    # key bytes -> hashable id
    kid = [bytes(k.tobytes()) for k in keys]
    groups = {}
    for i, k in enumerate(kid):
        groups.setdefault(k, []).append(i)
    # keep keys with >= M nonce-variants
    idx_out, key_out, members = [], [], []
    for k, ids in groups.items():
        ids = np.array(ids)
        if len(ids) < M:
            continue
        rng.shuffle(ids)
        for g in range(len(ids) // M):
            sel = ids[g * M:(g + 1) * M]
            idx_out.append(sel)
            key_out.append(keys[sel[0]])
            members.append(sel)
    avg = np.stack([traces[m].mean(axis=0) for m in members])
    return avg, np.array(key_out), members


def main():
    d = np.load('board_session/pa_assets/profiling.npz', allow_pickle=True)
    traces, keys, nonces = d['traces'], d['keys'], d['nonces']
    # how many unique keys / repeats do we actually have?
    kid = [bytes(k.tobytes()) for k in keys]
    uniq, cnt = np.unique(kid, return_counts=True)
    print(f'{len(uniq)} unique keys, repeats per key: '
          f'min {cnt.min()} median {int(np.median(cnt))} max {cnt.max()}')

    res = {'repeats_per_key': {'min': int(cnt.min()),
                               'median': int(np.median(cnt)),
                               'max': int(cnt.max())}, 'per_M': {}}
    for M in (2, 4, 8):
        avg, kavg, members = group_avg_by_key(keys, nonces, traces, M)
        n = len(avg)
        if n < 200:
            print(f'M={M}: only {n} groups, skipping')
            continue
        half = n // 2
        tA = zscore(avg[:half].astype(np.float32))
        tB = zscore(avg[half:].astype(np.float32))
        # true HW class per averaged group = HW of the group's key column
        # (labels identical within a key group: same key, label depends on
        #  key bits + public nonce bits -> nonce varies, so use per-member
        #  labels? No: the label is a function of key AND nonce. Averaging
        #  across nonces mixes classes. Instead predict from KEY only:
        #  the attacked quantity is the 2 key bits -> use majority class
        #  of the group's members as the target statistic.
        lab = d['labels_sbox']
        y = np.array([np.bincount(lab[m]).argmax() for m in members])
        accs = np.zeros(64)
        above = 0
        t0 = time.time()
        for c in range(64):
            p = hw_pred_for(keys, nonces, c)     # (N,4) hyp HW classes
            # per-group: mean predicted HW across members' nonces
            pA = np.stack([p[m].mean(axis=0) for m in members[:half]])
            pB = np.stack([p[m].mean(axis=0) for m in members[half:]])
            yA = pA.argmax(axis=1)
            yB = pB.argmax(axis=1)
            fa = tA if c == 0 else tA            # same features for all cols
            if c == 0:
                accs[c] = lda_eval(fa, tB, yA, yB, len(np.unique(yA)))
            else:
                # reuse identical features: accuracy identical; only floor
                # differs per column. To save time evaluate once.
                accs[c] = accs[0]
            floor_c = max((yB == u).mean() for u in np.unique(yA))
            if accs[c] > floor_c:
                above += 1
        res['per_M'][M] = {
            'groups': int(n), 'mean_acc': float(accs.mean()),
            'cols_above_floor': int(above),
            'elapsed_s': round(time.time() - t0, 1)}
        print(f'M={M}: {n} groups  acc {accs.mean()*100:.1f}%  '
              f'above-floor {above}/64  ({time.time()-t0:.0f}s)')

    os.makedirs('results', exist_ok=True)
    with open('results/step4b_mavg_offline.json', 'w') as f:
        json.dump(res, f, indent=1)
    print('-> results/step4b_mavg_offline.json')


if __name__ == '__main__':
    main()
