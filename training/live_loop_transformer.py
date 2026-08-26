#!/usr/bin/env python3
r"""live_loop_transformer.py — self-play live training with the Transformer.

Same episode structure as live_loop_gru.py, but the belief integrator is
the causal Transformer (train_joint_transformer.py): per column, the
transformer attends over the FULL query history (no GRU bottleneck), the
alive mask is fed back into attention (elimination feedback), and the
model is fine-tuned every --train-every episodes on the oracle-labelled
replay buffer (S-box heads + KADD byte head + direct key head).

Episode: fresh random key -> GRU/Transformer attack loop (packed nonces,
all 64 columns) -> oracle labels -> replay -> fine-tune -> next key.

Usage (board, cold start on the NEW unmasked core — no checkpoint needed):
    .venv/bin/python training/live_loop_transformer.py \
        --fresh --gain -2 --episodes 50 --max-queries 60 \
        --train-every 5 --integrator naive \
        --out training/models/joint_xfm_unmasked_live.pt

Usage (board, resume from checkpoint):
    .venv/bin/python training/live_loop_transformer.py \
        --model training/models/joint_xfm_unmasked_live.pt \
        --npz training/data/<session>.npz \
        --gain 35 --episodes 50 --max-queries 60 \
        --train-every 5 --M 1 --lt-epochs 2 \
        --out training/models/joint_xfm_g35_live.pt

Every query (raw trace + nonce + ct, per-episode key) is recorded to an
HDF5 session file under Dataset/ (--save-h5 to choose path, --no-save to
disable), directly usable for offline profiling/preprocessing.
"""
import argparse
import os
import sys

import numpy as np
import torch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import labels as lab
from train_joint import JointCNN, N_COLS, N_CLASSES
from train_joint_transformer import JointTransformer, N_HYPS
from preprocess import align_trace, zscore


def pack_nonce(choices, rng):
    nonce = rng.integers(0, 256, size=16, dtype=np.uint8)
    for col, (n0, n1) in choices.items():
        b0, bit = col // 8, col % 8
        mask = np.uint8(0xFF ^ (1 << bit))
        nonce[b0] = (nonce[b0] & mask) | (np.uint8(n0) << bit)
        nonce[8 + b0] = (nonce[8 + b0] & mask) | (np.uint8(n1) << bit)
    return nonce


class TemplateEngine:
    """Linear template (LDA) scoring engine: no CNN, no training.

    Leakage model: trace(t) ~ mu + alpha_c * (HW_c - E[HW_c]) + N(0,sigma^2).
    Each column gets a per-sample regression template alpha_c; a trace is
    scored by the standardized projection onto alpha_c, and each hypothesis's
    predicted HW class maps to a Gaussian log-likelihood. At -20 dB SNR this
    statistic beats the CNN ~9x on evidence edge (measured offline) and is
    immune to profiling-domain gaps.
    """

    def __init__(self, sim_h5, fit_k=600, window=1200, offset=0, temp=1.0):
        from sim_board import _fit_from_h5
        import h5py
        fit = _fit_from_h5(sim_h5, 0, fit_k, target='sbox64')
        with h5py.File(sim_h5, 'r', locking=False) as f:
            tr = f['traces'][:fit_k].astype(np.float64)
            ky = f['keys'][:fit_k]
            nn = f['nonces'][:fit_k]
        self._init_from_fit(fit, tr, ky, nn, window, offset, temp)

    def _init_from_fit(self, fit, tr, ky, nn, window=1200, offset=0, temp=1.0):
        """Shared init: fit dict + the raw traces used for the class model."""
        self.device = torch.device('cpu')
        self.window = window
        self.offset = offset
        self.temp = float(temp)
        self.mu = fit['mu'].astype(np.float64)
        self.sigma = fit['sigma'].astype(np.float64)
        self.alphas = fit['alpha'].astype(np.float64)          # (64, T)
        self.denom = np.sqrt(np.sum((self.alphas / self.sigma) ** 2, axis=1))
        self.denom = np.maximum(self.denom, 1e-9)
        fit_k = len(tr)
        self.means = np.zeros((N_COLS, N_CLASSES))
        self.vars = np.ones((N_COLS, N_CLASSES))
        self._fit_class_model(fit_k, tr, ky, nn)

    @classmethod
    def from_arrays(cls, traces, keys, nonces, window=1200, offset=0,
                    temp=1.0):
        """Fit from raw arrays (offline split validation): alphas come from
        the sbox64 regression on the SAME traces, then class model on them.
        """
        from sim_board import _fit_from_h5
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.h5', delete=True) as tmp:
            import h5py
            with h5py.File(tmp.name, 'w') as f:
                f.create_dataset('traces', data=traces.astype(np.float32))
                f.create_dataset('keys', data=keys)
                f.create_dataset('nonces', data=nonces)
            fit = _fit_from_h5(tmp.name, 0, len(traces), target='sbox64')
        e = cls.__new__(cls)
        e.ref = None
        e._init_from_fit(fit, traces, keys, nonces, window, offset, temp)
        return e

    def _fit_class_model(self, n, tr, ky, nn):
        ref = self.mu
        from preprocess import align_trace, zscore
        aligned = np.stack([align_trace(t, ref) for t in tr])
        centered = aligned - aligned.mean(1, keepdims=True)
        sc = (centered / self.sigma) @ self.alphas.T
        sc /= self.denom[None, :]
        hw = lab.round1_sbox_hw(ky, nn)                        # (n,64)
        for col in range(N_COLS):
            for v in range(N_CLASSES):
                sel = hw[:, col] == v
                if sel.sum() >= 2:
                    self.means[col, v] = sc[sel, col].mean()
                    self.vars[col, v] = max(sc[sel, col].var(), 1e-3)
    def evidence_all(self, trace, nonce):
        tr = np.asarray(trace, dtype=np.float64)
        if tr.size < self.offset + self.window:
            return None
        from preprocess import align_trace, zscore
        t = align_trace(tr, self.mu)
        t = (t - t.mean()) / self.sigma
        s = (t @ self.alphas.T) / self.denom
        nb = np.frombuffer(nonce, np.uint8)[None]
        hyps = lab.all_hypotheses()
        ev = np.full((N_COLS, N_HYPS), -1e3, dtype=np.float32)
        for col in range(N_COLS):
            pred = lab.hypothesis_labels(col, nb, hyps)[0]
            m = self.means[col]
            v = self.vars[col]
            ll = -0.5 * (s[col] - m) ** 2 / v - 0.5 * np.log(2 * np.pi * v)
            ll = ll - ll.max()
            for h, cl in enumerate(pred):
                cl = int(cl)
                if 0 <= cl < N_CLASSES:
                    ev[col, h] = ll[cl]
        return ev

    def preprocess(self, trace):
        return None  # evidence_all handles its own preprocessing


class XfmEngine:
    """Joint CNN + Transformer scoring engine (per-column attention state).

    model_path=None (or --fresh) builds a fresh randomly-initialized model —
    the oracle fine-tune loop then trains it from scratch on live leakage.
    """

    def __init__(self, model_path, npz_path, device='cpu', window=256,
                 fresh=False, temp=1.0):
        self.device = torch.device(device)
        self.temp = float(temp)
        if fresh or model_path is None or not os.path.exists(model_path):
            print(f'[+] cold start: fresh JointTransformer '
                  f'(no checkpoint loaded)')
            self.cnn = JointCNN()
            self.model = JointTransformer(cnn=self.cnn)
            self.window = window
        else:
            ckpt = torch.load(model_path, map_location='cpu')
            self.window = ckpt['window']
            self.cnn = JointCNN()
            self.cnn.load_state_dict(ckpt['state_dict'])
            self.model = JointTransformer(cnn=self.cnn)
            self.model.embed_in.load_state_dict(ckpt['embed_in'])
            with torch.no_grad():
                self.model.pos.copy_(ckpt['pos'])
            self.model.enc.load_state_dict(ckpt['enc'])
            self.model.head.load_state_dict(ckpt['head'])
            self.model.kadd_head.load_state_dict(ckpt['kadd_head'])
            self.model.key_head.load_state_dict(ckpt['key_head'])
        self.model.eval().to(self.device)
        self.ref = None
        self.offset = 0
        if npz_path and os.path.exists(npz_path):
            d = np.load(npz_path, allow_pickle=True)
            self.ref = d.get('ref')
            self.offset = int(d.get('offset', 0)) if 'offset' in d else 0
            if self.ref is None:
                self.ref = d['traces'].mean(axis=0).astype(np.float32)

    def preprocess(self, trace):
        if trace.size < self.offset + self.window:
            return None
        t = trace.astype(np.float64)
        if self.ref is not None:
            t = align_trace(t, self.ref)
        t = zscore(t).astype(np.float32)
        return t[self.offset:self.offset + self.window]

    def evidence_all(self, trace, nonce):
        """(64,4) evidence from the CNN for all columns."""
        tr = self.preprocess(trace)
        if tr is None:
            return None
        hyps = lab.all_hypotheses()
        nb = np.frombuffer(nonce, np.uint8)[None]
        with torch.no_grad():
            x = torch.tensor(tr[None, None], dtype=torch.float32,
                             device=self.device)
            lp = torch.log_softmax(self.cnn(x) / self.temp, dim=-1)[0].cpu()
        ev = np.full((N_COLS, N_HYPS), -1e3, dtype=np.float32)
        for col in range(N_COLS):
            pred = lab.hypothesis_labels(col, nb, hyps)[0]
            for h, v in enumerate(pred):
                v = int(v)
                if v in range(N_CLASSES):
                    ev[col, h] = lp[col, v].item()
        return ev

    def step(self, ev, ev_hist, prev_hist, alive_hist):
        """Causal transformer update. prev_hist/alive_hist are pure post
        histories (len == len(ev_hist)); the uninformative initial prior
        (zeros/ones) is prepended here. Returns post (64,4)."""
        pad0 = np.zeros((N_COLS, N_HYPS), dtype=np.float32)
        pad1 = np.ones((N_COLS, N_HYPS), dtype=np.float32)
        evt = torch.tensor(np.stack(ev_hist, 1), dtype=torch.float32,
                           device=self.device)                             # (64,T,4)
        prev = torch.tensor(np.stack([pad0] + prev_hist, 1),
                            dtype=torch.float32, device=self.device)
        alive = torch.tensor(np.stack([pad1] + alive_hist, 1),
                             dtype=torch.float32, device=self.device)
        with torch.no_grad():
            post = self.model.forward_causal(evt, prev, alive)[:, -1]
        return post.cpu().numpy()


class XfmLoop:
    """One episode's attack state (per-column attention history)."""

    def __init__(self, eng, integrator='xfm'):
        self.eng = eng
        self.integrator = integrator
        self.cum = np.zeros((N_COLS, N_HYPS), dtype=np.float32)
        self.ev_hist = []
        self.prev_hist = []
        self.alive_hist = []
        self.post = np.zeros((N_COLS, N_HYPS), dtype=np.float32)
        self.post[:, 0] = 1.0
        self.alive = np.ones((N_COLS, N_HYPS), dtype=np.float32)
        self.stable = np.zeros(N_COLS, dtype=int)
        self.done = np.zeros(N_COLS, dtype=bool)
        self.top = np.zeros(N_COLS, dtype=int)

    def step(self, ev):
        cols = [c for c in range(N_COLS) if not self.done[c]]
        if not cols:
            return
        self.ev_hist.append(ev)
        if self.integrator == 'naive':
            # Bayes-optimal log-evidence accumulation (uniform prior);
            # bypasses the transformer integrator entirely
            self.cum[cols] += ev[cols]
            mx = self.cum[cols].max(1, keepdims=True)
            p = np.exp(self.cum[cols] - mx)
            pn = p / p.sum(1, keepdims=True)
            post = np.zeros((N_COLS, N_HYPS), dtype=np.float32)
            post[cols] = pn
        else:
            post = self.eng.step(ev, self.ev_hist, self.prev_hist,
                                 self.alive_hist)
        self.post[cols] = post[cols]
        self.alive[cols] = (post[cols] > 1e-3).astype(np.float32)
        for c in cols:
            if self.alive[c].sum() == 0:
                self.alive[c, int(self.post[c].argmax())] = 1.0
            self.top[c] = int(self.post[c].argmax())
            if self.post[c, self.top[c]] > 0.99:
                self.stable[c] += 1
                if self.stable[c] >= 5:
                    self.done[c] = True
            else:
                self.stable[c] = 0
        self.prev_hist.append(self.post.copy())
        self.alive_hist.append(self.alive.copy())
        # keep history bounded (all three stay in lockstep)
        if len(self.ev_hist) > 64:
            del self.ev_hist[:-32]
            del self.prev_hist[:-32]
            del self.alive_hist[:-32]

    def pick_choices(self, rng):
        hyps = lab.all_hypotheses()
        choices = {}
        for col in range(N_COLS):
            if self.done[col]:
                continue
            alive = self.alive[col] > 0.5
            if alive.sum() == 0:
                alive[self.post[col].argmax()] = True
            best = None
            ties = []
            for n0 in (0, 1):
                for n1 in (0, 1):
                    nn = np.zeros(16, dtype=np.uint8)
                    nn[col // 8] |= np.uint8(n0 << (col % 8))
                    nn[8 + col // 8] |= np.uint8(n1 << (col % 8))
                    pred = lab.hypothesis_labels(col, nn[None], hyps)[0]
                    s = {int(v) for v in pred[alive]}
                    score = (len(s), sum(int(a) != int(b)
                                         for a in s for b in s if a != b))
                    if best is None or score > best[0]:
                        best = (score, n0, n1)
                        ties = [(n0, n1)]
                    elif score == best[0]:
                        ties.append((n0, n1))
            n0, n1 = ties[int(rng.integers(len(ties)))]
            choices[col] = (n0, n1)
        return choices


def fine_tune(eng, buf, args):
    """Oracle-supervised CNN+Transformer fine-tune on the replay buffer.

    Three losses, all oracle-labelled (the key is known in the lab):
      1. CNN S-box HW heads:  (trace -> 64 x 6)   vs round1_sbox_hw
      2. CNN KADD byte head:  (trace -> 8 x 9)    vs kadd_words_hw
         (the strong -0.1 dB leak; regularizes the weak S-box columns)
      3. Transformer replay:  replay each episode's evidence stream
         through the causal transformer with the true hypothesis per
         column as target at every step — this is the self-play piece
         the GRU version had and this one was missing.
    """
    hyps = lab.all_hypotheses()
    Xs, Ys, Ks = [], [], []
    for ep in buf:
        kb = np.frombuffer(ep['key'], np.uint8)[None]
        nb = np.frombuffer(b''.join(ep['nonces']), np.uint8).reshape(-1, 16)
        kb_rep = np.repeat(kb, len(nb), axis=0)
        Ys.append(lab.round1_sbox_hw(kb_rep, nb))         # (B,64)
        Ks.append(lab.kadd_words_hw(kb_rep, nb))          # (B,8)
        Xb = []
        for tr in ep['traces']:
            p = eng.preprocess(tr)
            if p is None:
                break
            Xb.append(p)
        if len(Xb) != len(ep['traces']):
            continue
        Xs.append(np.array(Xb, dtype=np.float32))
    if not Xs:
        return
    X = torch.tensor(np.concatenate(Xs), dtype=torch.float32)[:, None]
    Y = torch.tensor(np.concatenate(Ys), dtype=torch.int64)
    K = torch.tensor(np.concatenate(Ks), dtype=torch.int64)
    dev = eng.device
    X, Y, K = X.to(dev), Y.to(dev), K.to(dev)
    lossf = torch.nn.CrossEntropyLoss()
    # eng.model includes eng.cnn — use model.parameters() once (no dupes)
    opt = torch.optim.Adam(eng.model.parameters(), lr=1e-4)
    eng.model.train()
    total_loss = 0.0
    for _ in range(args.lt_epochs):
        # CNN S-box heads + KADD byte head, chunked so the autograd graph
        # stays bounded (a single backward over B x 64 columns OOMs on CPU)
        for i in range(0, len(X), 128):
            xb = X[i:i + 128]
            loss = 0.0
            logits = eng.model.cnn(xb)                     # (B,64,6)
            for c in range(N_COLS):
                loss = loss + lossf(logits[:, c], Y[i:i + 128, c])
            klogits = eng.model.kadd_logits(xb)            # (B,72)
            loss = loss + lossf(klogits.view(-1, 9),
                                K[i:i + 128].view(-1))
            loss.backward()
            total_loss += loss.item()
        # transformer trajectory replay per episode (backward per episode
        # keeps the autograd graph bounded; full-buffer OOMs CPU RAM)
        for ep in buf:
            bits = np.unpackbits(np.frombuffer(ep['key'], np.uint8),
                                 bitorder='little')
            th = torch.tensor([[int((bits[c] << 1) | bits[64 + c])
                                for c in range(N_COLS)]],
                              dtype=torch.int64, device=dev)  # (1,64)
            ev_stream = []
            for nonce_b, tr in zip(ep['nonces'], ep['traces']):
                ev = eng.evidence_all(tr, nonce_b)         # (64,4)
                if ev is None:
                    continue
                ev_stream.append(torch.tensor(ev, dtype=torch.float32,
                                              device=dev))
            if not ev_stream:
                continue
            # (64, T, 4): cap to last 32 steps — the causal transformer
            # only needs the final portion of the trajectory
            evt = torch.stack(ev_stream, 1)[:, -args.replay_max:]
            prev_hist = [torch.zeros(N_COLS, N_HYPS, device=dev)]
            alive_hist = [torch.ones(N_COLS, N_HYPS, device=dev)]
            rloss = 0.0
            for t in range(evt.shape[1]):
                post = eng.model.forward_causal(
                    evt[:, :t + 1],
                    torch.stack(prev_hist, 1),
                    torch.stack(alive_hist, 1))[:, -1]      # (64,4)
                rloss = rloss + lossf(post, th[0])
                prev_hist.append(post.detach())
                alive_hist.append((post.detach() > 1e-3).float())
            rloss.backward()
            total_loss += rloss.item()
    opt.step()
    eng.model.eval()
    print(f'    [ft] total loss {total_loss:.3f} on {len(X)} traces')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model', default=None,
                    help='joint xfm checkpoint (optional with --fresh)')
    ap.add_argument('--fresh', action='store_true',
                    help='cold start: ignore --model, init random weights')
    ap.add_argument('--npz', default=None,
                    help='profiling npz for align ref/offset (optional)')
    ap.add_argument('--window', type=int, default=256,
                    help='trace window used when no npz/checkpoint exists')
    ap.add_argument('--out', default=None)
    ap.add_argument('--episodes', type=int, default=50)
    ap.add_argument('--max-queries', type=int, default=60)
    ap.add_argument('--train-every', type=int, default=5)
    ap.add_argument('--lt-epochs', type=int, default=2)
    ap.add_argument('--M', type=int, default=1)
    ap.add_argument('--replay-max', type=int, default=32,
                    help='cap fine-tune replay to the last N query steps')
    ap.add_argument('--retries', type=int, default=20,
                    help='max consecutive bad traces per query before skip')
    ap.add_argument('--device', default=None,
                    help='torch device: cpu or cuda (default: auto)')
    ap.add_argument('--evidence', choices=('cnn', 'template'), default='cnn',
                    help='evidence source: CNN heads or linear template (LDA)')
    ap.add_argument('--integrator', choices=('xfm', 'naive'), default='xfm',
                    help="belief update: trained transformer or naive "
                         "Bayes evidence accumulation")
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--temp', type=float, default=1.0,
                    help='CNN softmax temperature scaling')
    ap.add_argument('--save-h5', default=None,
                    help='session dataset path (default: auto under '
                         'Dataset/, DISABLE with --no-save)')
    ap.add_argument('--no-save', action='store_true',
                    help='disable session dataset recording')
    ap.add_argument('--gain', type=int, default=35)
    ap.add_argument('--sim', action='store_true')
    ap.add_argument('--sim-h5', default=os.path.join(ROOT, 'Dataset',
                                                     'husky_g35_full.h5'))
    ap.add_argument('--profile-h5', default=None,
                    help='profiling h5 for template engine (default: --sim-h5)')
    ap.add_argument('--sim-amp', type=float, default=1.0)
    ap.add_argument('--sim-flat', type=float, default=0.0)
    ap.add_argument('--sim-target', default='sbox64')
    ap.add_argument('--bitstream',
                    default=os.path.join(ROOT, 'vivado_ascon',
                                         'ascon_cw305_top.bit'))
    ap.add_argument('--crypto-mhz', type=float, default=10.0,
                    help='crypto clock MHz (PLL1); lower = more samples/cycle')
    args = ap.parse_args()

    device = args.device or ('cuda' if torch.cuda.is_available() else 'cpu')
    fresh = args.fresh or (args.model is None) or (not os.path.exists(args.model))
    if args.evidence == 'template':
        profile_h5 = args.profile_h5 or args.sim_h5
        eng = TemplateEngine(profile_h5, fit_k=600, window=args.window,
                             offset=0, temp=args.temp)
        args.model = args.model or '(template)'
    else:
        eng = XfmEngine(args.model, args.npz, device=device,
                        window=args.window, fresh=fresh, temp=args.temp)
    default_out = 'training/models/joint_xfm_fresh_live.pt'
    out = args.out or ((args.model[:-3] + '_live.pt') if args.model
                       else default_out)
    print(f'[+] XFM engine: window {eng.window}, offset {eng.offset}, '
          f'device {device}')
    print(f'[+] {args.episodes} eps x <= {args.max_queries} q, '
          f'ft every {args.train_every}, out {out}')

    rng = np.random.default_rng(args.seed)
    lq = None
    if not args.sim:
        import live_query
        lq = live_query.LiveQuery(args.bitstream, os.urandom(16),
                                  gain=args.gain, crypto_mhz=args.crypto_mhz)

    # ---- session dataset recording (crash-safe: written per query) ----
    h5 = None
    ep_group = None
    h5_path = None
    if not args.no_save:
        import shutil
        free_gb = shutil.disk_usage(ROOT).free / 1e9
        if free_gb < 2.0:
            print(f'[!] only {free_gb:.1f} GB free — starting with '
                  f'recording DISABLED (--save-h5 to retry explicitly)')
        else:
            import h5py
            from datetime import datetime
            h5_path = args.save_h5 or os.path.join(
                ROOT, 'Dataset',
                'live_xfm_session_%s.h5' % datetime.now().strftime('%Y%m%d_%H%M%S'))
            try:
                h5 = h5py.File(h5_path, 'w')
            except OSError as e:
                print(f'[!] cannot open {h5_path}: {e} — recording disabled')
                h5 = None
        if h5 is not None:
            h5.attrs['created'] = datetime.now().isoformat()
            h5.attrs['model'] = str(args.model) if args.model else '(fresh)'
            h5.attrs['fresh'] = bool(fresh)
            h5.attrs['gain'] = args.gain
            h5.attrs['M'] = args.M
            h5.attrs['integrator'] = args.integrator
            h5.attrs['window'] = eng.window
            h5.attrs['offset'] = eng.offset
            h5.attrs['bitstream'] = args.bitstream
            print(f'[+] recording session dataset to {h5_path}')

    # ---- emergency cleanup: checkpoint + H5 close even on Ctrl+C/kill ----
    import atexit
    import signal

    def _sigterm_to_exit(signum, frame):
        raise SystemExit(0)

    try:
        signal.signal(signal.SIGTERM, _sigterm_to_exit)
    except (ValueError, OSError):
        pass

    def _emergency_cleanup():
        if h5 is not None:
            try:
                h5.close()
                print(f'[+] session dataset closed ({h5_path})')
            except Exception:
                pass
        try:
            if not hasattr(eng, 'cnn'):
                return  # template engine has no weights to save
            state = {
                'arch': 'joint_xfm', 'window': eng.window,
                'state_dict': eng.cnn.state_dict(),
                'embed_in': eng.model.embed_in.state_dict(),
                'pos': eng.model.pos,
                'enc': eng.model.enc.state_dict(),
                'head': eng.model.head.state_dict(),
                'kadd_head': eng.model.kadd_head.state_dict(),
                'key_head': eng.model.key_head.state_dict(),
                'd_model': 64, 'best_val_acc': 0.0, 'seed': args.seed,
                'target': 'sbox', 'joint': True}
            torch.save(state, out + '.tmp')
            os.replace(out + '.tmp', out)
            print(f'[+] wrote {out}')
        except Exception as e:
            print(f'[!] could not save checkpoint: {e}')

    atexit.register(_emergency_cleanup)

    def start_episode(ep, key_bytes):
        nonlocal h5
        try:
            g = h5.create_group(f'ep_{ep:03d}')
        except (OSError, RuntimeError) as e:
            print(f'[!] dataset write failed: {e}')
            disable_recording('write error')
            return None
        # raw bytes contain NULLs -> must store as u1 array, not vlen str
        g.attrs['key'] = np.frombuffer(key_bytes, dtype=np.uint8)
        return g

    def disable_recording(why):
        # degrade gracefully: training continues without recording
        nonlocal h5, h5_path
        try:
            h5.close()
        except Exception:
            pass
        h5 = None
        try:
            if h5_path and os.path.exists(h5_path):
                os.remove(h5_path)
                h5_path = None
        except OSError:
            pass
        print(f'[!] session recording DISABLED ({why}); training continues')

    def safe_append(g, nonce_b, trace, ct_b):
        if h5 is None or g is None:
            return
        try:
            append_query(g, nonce_b, trace, ct_b)
        except (OSError, RuntimeError, ValueError) as e:
            print(f'[!] dataset write failed: {e}')
            disable_recording('write error')

    def append_query(g, nonce_b, trace, ct_b):
        n = 0 if 'traces' not in g else g['traces'].shape[0]
        samples = int(np.asarray(trace).size)
        if 'traces' in g and g['traces'].shape[1] != samples:
            raise ValueError(f'trace width {samples} != dataset width '
                             f'{g["traces"].shape[1]}')
        if 'traces' not in g:
            g.create_dataset('traces', (0, samples), maxshape=(None, samples),
                             dtype='f4', chunks=(1, samples))
            g.create_dataset('nonces', (0, 16), maxshape=(None, 16),
                             dtype='u1')
            g.create_dataset('cts', (0, 16), maxshape=(None, 16),
                             dtype='u1')
        for name, arr in (('traces', np.asarray(trace, dtype=np.float32)[None]),
                          ('nonces', np.frombuffer(nonce_b, np.uint8)[None]),
                          ('cts',    np.frombuffer(ct_b,   np.uint8)[None])):
            d = g[name]
            d.resize(n + 1, axis=0)
            d[n] = arr

    buf = []
    stats = {'cracked_64': 0, 'best_match': 0.0, 'q_sum': 0, 'n_ep': 0}
    for ep in range(1, args.episodes + 1):
        key = os.urandom(16)
        if args.sim:
            from sim_board import SimBoard
            lq = SimBoard(args.sim_h5, key, column=0, amp=args.sim_amp,
                          seed=args.seed + ep, flat_p=args.sim_flat,
                          target=args.sim_target)
        else:
            lq.set_key(key)
        loop = XfmLoop(eng, integrator=args.integrator)
        ep_nonces, ep_traces = [], []
        if h5 is not None:
            ep_group = start_episode(ep, key)
        for q in range(1, args.max_queries + 1):
            choices = loop.pick_choices(rng)
            nonce = pack_nonce(choices, rng)
            pool = []
            flat_streak = 0
            last_nonce, last_ct = None, None
            while len(pool) < args.M and flat_streak < args.retries:
                trace, ct = lq.query(nonce)
                if trace is None:
                    flat_streak += 1
                    continue
                flat_streak = 0
                pool.append(trace)
                last_nonce, last_ct = bytes(nonce), ct
            if not pool:
                print(f'  [!] q {q}: no good trace after {args.retries} '
                      f'retries, skipping query')
                continue
            if args.M > 1 and args.evidence == 'template':
                from preprocess import align_trace
                ref = eng.mu
                pool = [align_trace(np.asarray(t, dtype=np.float64), ref)
                        for t in pool]
            trace = np.mean(pool, axis=0)
            ep_nonces.append(bytes(nonce))
            ep_traces.append(trace)
            if last_ct is not None:
                safe_append(ep_group, bytes(nonce), trace,
                            bytes(last_ct).ljust(16, b'\x00'))
            ev = eng.evidence_all(trace, nonce)
            if ev is None:
                continue
            loop.step(ev)
            if loop.done.all():
                break
        if args.sim:
            lq.close()
        bits = np.unpackbits(np.frombuffer(key, np.uint8), bitorder='little')
        truth = np.array([int((bits[c] << 1) | bits[64 + c])
                          for c in range(N_COLS)])
        n_done = int(loop.done.sum())
        wrong = sum(1 for c in range(N_COLS)
                    if int(loop.top[c]) != int(truth[c]))
        match = 100.0 * (1 - wrong / N_COLS)
        stats['n_ep'] += 1
        stats['q_sum'] += q
        stats['best_match'] = max(stats['best_match'], match)
        if n_done == N_COLS:
            stats['cracked_64'] += 1
        print(f'  ep {ep:3d}  key {key.hex()[:8]}…  q {q:3d}  '
              f'done {n_done:2d}/64  bit-match {match:5.1f}%', flush=True)
        # ---- full-key assembly + oracle verification ----
        # readOutput returns tag[:12]+ct[:4] for the shim's fixed query
        # (AD = 4 zero bytes, PT = 4 zero bytes) -> use fpga_expected
        if last_ct is not None:
            cand = bytearray(16)
            for c in range(N_COLS):
                if loop.done[c] or True:      # use top hyp regardless of lock
                    cand[c // 8] |= ((int(loop.top[c]) >> 1) & 1) << (c % 8)
                    cand[8 + c // 8] |= (int(loop.top[c]) & 1) << (c % 8)
            from ascon_ref import fpga_expected
            ok = bytes(fpga_expected(bytes(cand), last_nonce)) == bytes(last_ct)
            tag_ok = 'FULL KEY VERIFIED' if ok else 'key mismatch'
            n_top_right = N_COLS - wrong
            print(f'      [verify] top-1 assembled key '
                  f'{bytes(cand).hex()[:16]}… vs true {key.hex()[:16]}… '
                  f'-> {tag_ok} ({n_top_right}/64 cols correct)', flush=True)
            if ok:
                stats['keys_cracked'] = stats.get('keys_cracked', 0) + 1
        buf.append({'key': key, 'nonces': ep_nonces, 'traces': ep_traces})
        if len(buf) > 16:
            buf.pop(0)
        if ep % args.train_every == 0:
            fine_tune(eng, buf, args)

    if h5 is not None:
        h5.close()
        print(f'[+] session dataset closed')
    if lq is not None:
        try:
            lq.close()
        except Exception:
            pass
    if not hasattr(eng, 'cnn'):
        print('[+] template engine: no checkpoint to save')
    else:
        state = {'arch': 'joint_xfm', 'window': eng.window,
                 'state_dict': eng.cnn.state_dict(),
                 'embed_in': eng.model.embed_in.state_dict(),
                 'pos': eng.model.pos,
                 'enc': eng.model.enc.state_dict(),
                 'head': eng.model.head.state_dict(),
                 'kadd_head': eng.model.kadd_head.state_dict(),
                 'key_head': eng.model.key_head.state_dict(),
                 'd_model': 64, 'best_val_acc': 0.0, 'seed': args.seed,
                 'target': 'sbox', 'joint': True}
        torch.save(state, out)
        print(f'[+] wrote {out}')
    print(f'[+] {stats["cracked_64"]}/{stats["n_ep"]} eps locked 64/64, '
          f'{stats.get("keys_cracked", 0)} keys oracle-VERIFIED, '
          f'best bit-match {stats["best_match"]:.1f}%, '
          f'avg q {stats["q_sum"]/max(stats["n_ep"],1):.1f}')


if __name__ == '__main__':
    main()
