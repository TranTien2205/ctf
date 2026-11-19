# per-attack pollard-pm1 deep — the smooth-predecessor split, the full treatment

## The mechanism

`p-1` `B`-smooth → `p-1 | B!` → `a^{B!} ≡ 1 mod p` → `p | a^{B!}-1` and `p|n`
→ `gcd(a^{B!}-1, n) = p`.

## Detection

- **keygen**: `p=getPrime(512)` where `p-1` is smooth, a "weak prime", a
  product of small primes + 1.
- a shared/weak `p` hint.

## The bound / falsifier

`B` ≥ the largest `p-1` factor. `gcd(a^{B!}-1,n)=1` → `p-1` not smooth enough
→ raise `B` or closed.

## The attack

```bash
crypto_attack.py pollard-pm1 --n <n> --b <B>
```

```python
a = 2
for j in range(2,B+1): a = pow(a,j,n)   # a = 2^(B!) mod n
g = gcd(a-1, n)                          # >1 → p
```

## The chain

`p` → `q=n/p` → `phi` → `d` → `m` → `pow`.

## The verify

`1 < gcd < n`, `p*q==n`.

## Variants

- Stage-2 for one large factor.
- `p+1` smooth → Williams p+1 (a different method).
- Both `p-1`,`p+1` smooth → either.

## Failure modes

- `p-1` not `B`-smooth — `gcd=1`; raise `B` or closed.
- `B` too small — the largest factor missed.

## The honest status

Pollard 1974 — catalogue.
