# per-attack crt deep — residues / Bellcore / dp-dq-qInv, the full treatment

## The three recoveries

### 1. Residue reconstruction
`m mod p_i` for several `p_i`, `∏pi>m` → CRT → `m`. The `crt` id's
`--residues/--moduli` form.

### 2. Bellcore fault
A correct `sig=m^d` and a faulty `sig'` of the same `m` → `sig'^e-m≡0 mod p`
(correct half) → `gcd(sig'^e-m,n)=p`/`q`. **Manual** — no `crypto_attack.py` flag.

### 3. dp/dq/qInv leak
`dp=d mod p-1` in a partial key → `e·dp-1=k(p-1)` → `p` candidates from `e·dp-1`.
**Manual** — a `gcd`/loop.

## Detection

- residues: `m mod pi`, `∏pi>m`.
- a fault: `sig`+`sig_faulty`.
- `dp`,`dq`,`qInv` in a partial key.

## The bounds

- `∏pi>m` (unique `m`) · a correct+faulty pair · `e·dp-1` divisible by `k`.

## The attacks

```bash
crypto_attack.py crt --residues "r1,r2" --moduli "p1,p2"
```

```python
# Bellcore — manual
q = gcd(pow(sig_faulty,e,n)-m, n)
# dp — manual
for k in range(1,e): p=(e*dp-1)//k+1; 
    if n%p==0: break
```

## The verify

`pow(m,e,n)==c` / `gcd==q` / `p*q==n`.
