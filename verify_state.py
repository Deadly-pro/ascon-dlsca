import numpy as np, h5py, itertools, math

fn = 'Dataset/underclock_1.0MHz.h5'
with h5py.File(fn, 'r') as f:
    X = f['traces'][:].astype(np.float64)
    keys = f['keys'][:]
n, T = X.shape
split = int(0.8*n)
Xz = (X - X.mean(1, keepdims=True)) / (X.std(1, keepdims=True)+1e-9)
Xz = (Xz - Xz.mean(0)) / (Xz.std(0)+1e-12)
Xtr, Xva = Xz[:split], Xz[split:]
keys_tr, keys_va = keys[:split], keys[split:]

# Use just 2 bytes (e.g. byte0 and byte1) for a toy boundary test
true_key = keys_va[0]   # treat this held-out trace's key as the "real" one
print('[+] true key for toy test:', bytes(true_key).hex())

hw_tr = np.array([[bin(int(b)).count('1') for b in row] for row in keys_tr], int)

def fit_byte_template(byte_idx):
    y = hw_tr[:, byte_idx].astype(float)
    z = (y - y.mean())/(y.std()+1e-12)
    r = z @ Xtr / len(Xtr)
    pk = int(np.abs(r).argmax())
    mu, sig = np.zeros(9), np.zeros(9)
    for h in range(9):
        idx = np.where(hw_tr[:, byte_idx] == h)[0]
        if len(idx)==0:
            mu[h]=0; sig[h]=1e6
        else:
            vals = Xtr[idx, pk]
            mu[h] = vals.mean(); sig[h]=vals.std()+1e-6
    return pk, mu, sig

pk0, mu0, sig0 = fit_byte_template(0)
pk1, mu1, sig1 = fit_byte_template(1)

x_attack = Xva[0]  # single attack trace
def byte_ll(byte_idx, pk, mu, sig, key_byte):
    h = bin(int(key_byte)).count('1')
    val = x_attack[pk]
    return -0.5*((val-mu[h])**2/sig[h]**2) - math.log(sig[h])

# Brute over full 2-byte space (256^2 = 2^16), rank by HW likelihood
scores = []
for kb0 in range(256):
    for kb1 in range(256):
        s = 0.0
        s += byte_ll(0, pk0, mu0, sig0, kb0)
        s += byte_ll(1, pk1, mu1, sig1, kb1)
        scores.append(((kb0, kb1), s))
scores.sort(key=lambda x: -x[1])

true_pair = (int(true_key[0]), int(true_key[1]))
rank = next(i for i,(k,_) in enumerate(scores) if k == true_pair)
print('[+] toy 2-byte brute: true (k0,k1) rank =', rank, 'of', len(scores),
    '(space=256^2≈6.5e4)')
