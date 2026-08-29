#!/usr/bin/env python3
r"""probe_evidence.py — measure LIVE per-query evidence quality directly.

Fixed known key, separating nonces, M-averaged captures. Reports:
  - mean evidence edge E[logp(true hyp) - mean logp(others)] per query
  - fraction of columns with positive edge
  - naive-Bayes rank of the true hyp after all queries (convergence forecast)
  - the SAME statistics computed on npz val traces (offline reference)

If live edge << npz edge  -> preprocessing/alignment domain gap.
If live edge <= 0         -> anti-correlated (masked core or broken pairing).
If live edge > 0          -> keep training, N queries needed = 4.6/edge.

Usage:
    .venv/bin/python training/probe_evidence.py \
        --model training/models/joint_xfm_g35.pt \
        --npz training/data/husky_g35_full.npz \
        --key 0f1e2d3c4b5a69788796a5b4c3d2e1f0 \
        --gain 35 --n-queries 40 --M 16
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'training'))

import labels as lab
from live_loop_transformer import XfmEngine, pack_nonce


def bayes_report(ev_list, truth_list):
    """Naive-Bayes accumulate per column; return (mean edge, rank1_frac, n)."""
    edges, posts, truths = [], {}, {}
    for ev, col, th in zip(ev_list, [e[0] for e in truth_list],
                           [e[1] for e in truth_list]):
        others = [h for h in range(4) if h != th]
        edges.append(ev[col, th] - ev[col, others].mean())
        posts.setdefault(col, np.zeros(4))
        p = posts[col]
        p += ev[col] - ev[col].max()
        truths[col] = th
    r1 = sum(int(np.argmax(np.exp(posts[c]))) == t
             for c, t in truths.items()) / max(len(truths), 1)
    return float(np.mean(edges)), r1, len(truths)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--npz', required=True)
    ap.add_argument('--key', required=True)
    ap.add_argument('--gain', type=int, default=35)
    ap.add_argument('--n-queries', type=int, default=40)
    ap.add_argument('--M', type=int, default=16)
    ap.add_argument('--retries', type=int, default=20)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--device', default=None)
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon',
                                         'ascon_cw305_top.bit'))
    args = ap.parse_args()

    dev = args.device or ('cuda' if __import__('torch').cuda.is_available()
                          else 'cpu')
    eng = XfmEngine(args.model, args.npz, device=dev)
    key = bytes.fromhex(args.key)
    bits = np.unpackbits(np.frombuffer(key, np.uint8), bitorder='little')
    hyps = lab.all_hypotheses()
    rng = np.random.default_rng(args.seed)

    # ---- offline reference: npz val-split edges ----
    d = np.load(args.npz, allow_pickle=True)
    kb = np.frombuffer(key, np.uint8)[None]
    nb_all = None
    val_edge = None
    try:
        import torch
        from train_joint import JointCNN, N_COLS
        cnn = JointCNN()
        cnn.load_state_dict(d.get('cnn_state') or
                            __import__('torch').load(
                                args.model, map_location='cpu')['state_dict'])
        cnn.eval()
        tr, ks, ns = d['traces'], d['keys'], d['nonces']
        vb = np.unpackbits(ks[2400:], axis=1, bitorder='little')
        with torch.no_grad():
            lp = torch.log_softmax(cnn(torch.tensor(
                tr[2400:, None].astype(np.float32))), -1).numpy()
        e = []
        for c in range(N_COLS):
            pred = lab.hypothesis_labels(c, ns[2400:], hyps)
            th = (vb[:, c] << 1) | vb[:, 64 + c]
            tv = np.array([lp[i, c, pred[i, th[i]]]
                           for i in range(len(th))])
            ov = np.array([[lp[i, c, pred[i, h]] for h in range(4)
                            if h != th[i]] for i in range(len(th))])
            e.append((tv - ov.mean(1)).mean())
        val_edge = float(np.mean(e))
    except Exception as ex:
        print(f'[!] npz reference skipped: {ex}')

    # ---- live probe ----
    import live_query
    lq = live_query.LiveQuery(args.bitstream, key, gain=args.gain)
    ev_list, truth = [], []
    cols = rng.permutation(64)
    try:
        for i in range(args.n_queries):
            col = int(cols[i % 64])
            th = int((bits[col] << 1) | bits[64 + col])
            nonce = pack_nonce({col: (int(rng.integers(2)),
                                      int(rng.integers(2)))}, rng) \
                if False else None
            # use a truly separating nonce pair
            best = None
            for n0 in (0, 1):
                for n1 in (0, 1):
                    nn = np.zeros(16, dtype=np.uint8)
                    nn[col // 8] |= np.uint8(n0 << (col % 8))
                    nn[8 + col // 8] |= np.uint8(n1 << (col % 8))
                    s = {int(v) for v in
                         lab.hypothesis_labels(col, nn[None], hyps)[0]}
                    sc = (len(s), sum(a != b for a in s for b in s))
                    if best is None or sc > best[0]:
                        best = (sc, n0, n1)
            nonce = pack_nonce({col: (best[1], best[2])}, rng)
            pool, retries = [], 0
            while len(pool) < args.M and retries < args.retries:
                tr, _ct = lq.query(nonce)
                retries += 1
                if tr is not None:
                    pool.append(tr)
            if not pool:
                print(f'  q{i}: no good trace')
                continue
            trace = np.mean(pool, axis=0)
            ev = eng.evidence_all(trace, nonce)
            if ev is None:
                continue
            ev_list.append(ev)
            truth.append((col, th))
            if (i + 1) % 10 == 0:
                m, r1, nc = bayes_report(ev_list, truth)
                print(f'  q{i+1:3d}: edge {m:+.4f} nats/q, '
                      f'true-hyp rank-1 {r1*100:.0f}% over {nc} cols')
    finally:
        lq.close()

    m, r1, nc = bayes_report(ev_list, truth)
    print('\n===== VERDICT =====')
    print(f'live edge      : {m:+.4f} nats/query over {nc} columns')
    if val_edge is not None:
        print(f'npz val edge   : {val_edge:+.4f} nats/query')
        print(f'live/npz ratio : {m / val_edge:.2f}x'
              if abs(val_edge) > 1e-6 else 'npz edge ~ 0')
    print(f'naive-Bayes rank-1 after {len(ev_list)} queries: {r1*100:.0f}%')
    if m <= 0:
        print('ANTI-CORRELATED — stop attacking; check core/profile pairing')
    elif m < 0.01:
        print('ALIVE BUT WEAK — need ~%.0f queries/column at this M'
              % (4.6 / m))
    else:
        print('HEALTHY — ~%.0f queries/column to 0.99 posterior'
              % (4.6 / m))


if __name__ == '__main__':
    main()
