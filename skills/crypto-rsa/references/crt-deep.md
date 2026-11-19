# crt deep — residues / Bellcore fault / dp-dq-qInv, the full treatment

## The three recoveries

### 1. Residue reconstruction
`m` given mod `p_i` for several `p_i`, `∏pi > m` → CRT → `m`. The classic
"split the secret across primes" — the `crt` id's `--residues/--moduli` form.

### 2. Bellcore fault
A CRT-signing device returns a correct `sig = m^d` and a faulty `sig'` of the
same `m`. `sig'^e - m ≡ 0 mod p` (correct half) but `≢0 mod q` →
`gcd(sig'^e - m, n) = p` (or `q`). **Manual** — `gcd`, not a `crypto_attack.py`
flag.

### 3. dp/dq/qInv leak
`dp = d mod (p-1)` etc. in a partial private key → recover `p`,`q`:
`e·dp - 1 = k·(p-1)` for some `k` → try `p` candidates from `e·dp-1`.
**Manual** — a `gcd`/loop, not a `crypto_attack.py` flag.

## Detection

- **residues**: `m mod pi` for several `pi`, `∏pi>m`.
- **a fault**: `sig_correct` and `sig_faulty` of the same `m`.
- **`dp`,`dq`,`qInv`** in a partial private key.

## The bounds

- residues: `∏pi > m` for a unique `m`.
- fault: a correct+faulty pair on the same `m`.
- `dp`: `e·dp - 1` divisible by some `k` giving `p`.

## The attacks

```bash
python3 tools/crypto_attack.py crt --residues "r1,r2,..." --moduli "p1,p2,..."
```

```python
# Bellcore — manual
q = gcd(pow(sig_faulty, e, n) - m, n)
# dp — manual
for k in range(1, e):
    p = (e*dp - 1)//k + 1
    if n % p == 0: break
```

## The verify

`pow(m,e,n)==c` / `gcd==q` / `p*q==n`.
