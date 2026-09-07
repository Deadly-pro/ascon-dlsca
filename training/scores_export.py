#!/usr/bin/env python3
r"""scores_export.py — run the per-column adaptive SCA loop at a fixed target
key for ALL 64 columns and export the (64,4) hypothesis scores for
fullkey_assemble.py (confident columns taken directly, weak columns
brute-forced, candidate verified against the public-output oracle).

Reuses adaptive.py's machinery (Profile, separating-nonce picker, LR scoring)
but, unlike attack_column, ALWAYS records the final per-column log-scores —
converged or not — so the assembler's margin logic + bounded brute force can
finish the key even when some columns don't converge.

Board usage (after profiling + finetuning per runbook_monday.md):
  python3 scores_export.py --key <target hex> --model-frm \
      "training/models/mon_c{col}.pt" --npz training/data/prof_mon.npz \
      --M 16 --max-queries 48 --gain 35 --out attack_scores.npz

Offline selftest (no hardware, perfect classifier; validates bit order,
score plumbing, npz format, and end-to-end assembly):
  .venv/bin/python training/scores_export.py --selftest
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import labels as lab
import ascon_ref as ar
from ascon_ref import _le32_words
from cw305_ascon_shim import REG_TAGOUT
from fullkey_assemble import recover

AD = b'\x00' * 4
PT = b'\x00' * 4


def column_scores(prof, lq, col, M, max_queries, converge_p, stable_n,
                  rng, prior=None, temp=1.0, verbose=True):
    """One column's adaptive loop; ALWAYS returns the (4,) log-scores.

    Trimmed from adaptive.attack_column: same separating-nonce selection,
    M-averaging, LR/posterior scoring and convergence test — but the final
    accumulated log-scores are returned whether or not it converged.
    """
    from adaptive import pick_separating_nonce, score_trace, score_trace_logits
    log_acc = np.zeros(4)
    post = np.ones(4) / 4
    stable = 0
    n_cap = 0
    t0 = time.time()
    for _ in range(max_queries):
        nonce = pick_separating_nonce(col, prof.support, rng, post=post)
        pool = []
        guard = 0
        while len(pool) < M and guard < 8 * M:
            guard += 1
            trace, _ct = lq.query(nonce)
            if trace is None:
                continue
            pool.append(trace)
        if len(pool) < M:
            continue                      # too many bad captures this nonce
        n_cap += 1
        trace = prof.preprocess(np.mean(pool, axis=0))
        if trace is None:
            continue
        if prior is not None:
            logits_row = prof.logits(trace[None])[0]
            sc = score_trace_logits(logits_row, prior, temp, nonce,
                                    col, prof.classes)
        else:
            logp_row = prof.log_probs(trace[None])[0]
            sc = score_trace(logp_row, nonce, col, prof.classes)
        log_acc += np.where(np.isfinite(sc), sc, -1e3)
        post = np.exp(log_acc - log_acc.max())
        post /= post.sum()
        top = int(post.argmax())
        stable = stable + 1 if post[top] > converge_p else 0
        if stable >= stable_n:
            break
    if verbose:
        print(f'  col {col:2d}: {n_cap:3d} queries, top hyp {int(log_acc.argmax())} '
              f'post {post.max():.3f}  [{time.time()-t0:.0f}s]')
    return log_acc, n_cap, int(post.argmax()), float(post.max())


def oracle_pair(lq):
    """One board query at a fresh nonce -> (nonce, ct||tag) in natural order.

    ct (4B) from readOutput tail; full tag (16B) from REG_TAGOUT, both
    un-scrambled with _le32_words (le32 is an involution)."""
    nonce = np.random.randint(0, 256, 16, dtype=np.uint8)
    trace, ro = lq.query(nonce)
    tries = 0
    while trace is None and tries < 8:
        trace, ro = lq.query(nonce)
        tries += 1
    if ro is None or len(ro) != 16:
        return bytes(nonce), None
    ct_nat = _le32_words(bytes(ro[12:16]))
    raw_tag = bytes(lq.t.fpga_read(REG_TAGOUT, 16))
    tag_nat = _le32_words(raw_tag)
    return bytes(nonce), ct_nat + tag_nat


def run_attack(args):
    from adaptive import Profile, fit_lr, make_lq
    key = bytes.fromhex(args.key)
    if len(key) != 16:
        sys.exit('--key must be 16 bytes hex')
    rng = np.random.default_rng(args.seed)
    lq = make_lq(args, 0, key)
    scores = np.zeros((64, 4))
    diag = []
    try:
        for col in range(64):
            model = args.model_frm.format(col=col)
            if not os.path.exists(model):
                sys.exit(f'[!] missing model for col {col}: {model}')
            prof = Profile(model, args.npz)
            prior = temp = None
            if args.lr:
                temp, prior = fit_lr(prof, args.npz)
            sc, nq, top, pmax = column_scores(
                prof, lq, col, args.M, args.max_queries,
                args.converge_p, args.stable_n, rng, prior=prior,
                temp=temp if temp is not None else 1.0,
                verbose=not args.quiet)
            scores[col] = sc
            diag.append((col, nq, top, round(pmax, 3)))
        nonce, ct_tag = oracle_pair(lq)
    finally:
        lq.close()
    np.savez(args.out, scores=scores, nonce=np.frombuffer(nonce, np.uint8),
             ct_tag=np.frombuffer(ct_tag, np.uint8) if ct_tag is not None
             else np.zeros(20, np.uint8),
             diag=np.array(diag, dtype=object))
    print(f'[+] saved -> {args.out}')
    n_conf = sum(1 for _, _, _, p in diag if p > 0.99)
    print(f'    confident columns (post>0.99): {n_conf}/64  '
          f'(need >= 52 for the assembler)')
    return args.out


# ── offline selftest: perfect classifier -> full chain -> assembled key ─────
class FakeProf:
    """Perfect per-column classifier: reads the nonce embedded in the trace,
    returns the TRUE class for its column under the true key bits."""
    def __init__(self, col, key, classes):
        self.col, self.key, self.classes = col, key, list(classes)
        self.support = set(self.classes)
        self.window = 16
        self.arch = 'fake'
    def preprocess(self, trace):
        return np.asarray(trace, dtype=np.float32)
    def log_probs(self, traces):
        out = []
        for tr in traces:
            nonce = np.clip(tr[:16], 0, 255).astype(np.uint8)
            w1 = int(ar.bytes_to_int(bytes(self.key[0:8])))
            w2 = int(ar.bytes_to_int(bytes(self.key[8:16])))
            k0 = (w1 >> self.col) & 1
            k1 = (w2 >> self.col) & 1
            true_cls = int(lab.hypothesis_labels(
                self.col, nonce[None], np.array([[k0, k1]]))[0][0])
            logits = np.random.normal(0, 0.01, len(self.classes))
            logits[self.classes.index(true_cls)] += 8.0
            logits -= logits.max()
            lp = np.exp(logits); lp /= lp.sum()
            out.append(np.log(np.maximum(lp, 1e-12)))
        return np.array(out)


class FakeLQ:
    """Returns traces that embed the query nonce (perfect-capture board)."""
    def __init__(self):
        self.t = None
    def query(self, nonce):
        tr = np.concatenate([np.asarray(nonce, dtype=np.float64),
                             np.random.normal(0, 1e-3, 32)])
        return tr, b'\x00' * 16
    def close(self):
        pass


def selftest():
    key = bytes.fromhex('8826d916cdfb21c6c1ff91a761565a70')
    classes = list(range(6))
    rng = np.random.default_rng(3)
    lq = FakeLQ()
    scores = np.zeros((64, 4))
    for col in range(64):
        prof = FakeProf(col, key, classes)
        sc, nq, top, pmax = column_scores(
            prof, lq, col, M=1, max_queries=20, converge_p=0.99,
            stable_n=3, rng=rng, verbose=False)
        scores[col] = sc
    # oracle pair from the reference (the board gives the same bytes)
    nonce = bytes(rng.integers(0, 256, 16, dtype=np.uint8))
    ct_tag = ar.ascon_encrypt(key, nonce, AD, PT)
    out = '/tmp/scores_selftest.npz'
    np.savez(out, scores=scores, nonce=np.frombuffer(nonce, np.uint8),
             ct_tag=np.frombuffer(ct_tag, np.uint8))
    rk, nv, kk = recover(scores, nonce, ct_tag, max_weak=8, verbose=False)
    ok = rk == key
    print(f'scores_export selftest: loop 64 cols -> npz -> assemble -> '
          f'{"KEY RECOVERED " + rk.hex() if ok else "FAIL"} '
          f'({nv} verifications)')
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--key', help='target key hex (the key under attack)')
    ap.add_argument('--model-frm', default='training/models/c{col}.pt',
                    help='per-column model path format with {col}')
    ap.add_argument('--npz', help='profiling npz (ref/mu/sigma + LR fit)')
    ap.add_argument('--lr', action='store_true', help='LR scoring (calibrated)')
    ap.add_argument('--M', type=int, default=16)
    ap.add_argument('--max-queries', type=int, default=48)
    ap.add_argument('--converge-p', type=float, default=0.99)
    ap.add_argument('--stable-n', type=int, default=3)
    ap.add_argument('--gain', type=int, default=35)
    ap.add_argument('--offset', type=int, default=0)
    ap.add_argument('--bitstream', default='vivado_ascon/ascon_cw305_top.bit')
    ap.add_argument('--std-floor', type=float, default=0.001)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--out', default='attack_scores.npz')
    ap.add_argument('--quiet', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        sys.exit(0 if selftest() else 1)
    if not args.key:
        ap.error('need --key <hex> (or --selftest)')
    run_attack(args)


if __name__ == '__main__':
    main()
