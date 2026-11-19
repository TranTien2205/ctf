# crt — the residue/fault/dp attacks, complete

## What it is

Three distinct recoveries under one id:

1. **Residue reconstruction** — `m` given mod `p_i`, `∏pi > m` → CRT → `m`.
2. **Bellcore fault** — a correct + faulty signature of the same `m` →
   `gcd(s'^e - m, n) = q`.
3. **dp/dq/qInv leak** — `dp=d mod (p-1)` etc. → recover `p`,`q`.

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
crypto_attack.py crt --residues r1 r2 --moduli p1 p2          # m = CRT
crypto_attack.py # crt --residues/--moduli only — Bellcore/dp are manual (gcd / dp-loop), not tool flags  # Bellcore
crypto_attack.py # crt --residues/--moduli only — dp/dq/qInv recovery is manual
```

## The verify

`pow(m,e,n)==c` / `gcd==q` / `p*q==n`.
