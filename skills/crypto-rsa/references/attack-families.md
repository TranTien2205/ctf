# Attack families — the six primitives, expanded

## Family 1 — the wrap (the power never modded)

`c = m^e` with `m^e < n` → `c` is a plain integer power.

- `small-e-root` — `e`th root of `c`.
- `nth-root` — the general root.
- `hastad` — `e` broadcasts, CRT + root.

**Bound**: `m^e < n` (root) or `∏ni > m^e` (hastad).
**Verify**: `pow(m,e)==c` / `pow(m,e)==x` (the CRT value).

## Family 2 — the gap (close primes)

`|p-q|` small → `n = a²-b²`, `a=(p+q)/2` near `√n`.

- `fermat` — the `a` climb.

**Bound**: `|p-q|` small — `O(|p-q|)` iterations.
**Verify**: `p*q==n`.

## Family 3 — the divisor (gcd)

- `batch-gcd` — a shared prime across ≥2 `n`.
- `pollard-pm1` — `p-1` `B`-smooth.

**Bound**: a collision (`batch-gcd`) / `B`≥largest `p-1` factor (`pollard`).
**Verify**: `gcd>1`, `p*q==n`.

## Family 4 — the exponent (ed≡1 mod φ algebra)

- `common-modulus` — `gcd(e1,e2)=1`, Bezout.
- `wiener` — `d<n^0.25`, CF.
- `boneh-durfee` — `d<n^0.292`, lattice.
- `factor-from-d` — `d`/`phi`/`dp` held.

**Bound**: `gcd=1` / `n^0.25` / `n^0.292` / the value held.
**Verify**: `pow(c,d,n)==m` then `pow(m,e,n)==c`.

## Family 5 — the partial knowledge (small roots)

- `coppersmith-high-bits` — top `n/2` bits of `p`.
- `coppersmith-core` — `f(x)=a+x`, `|x|<n^0.25`.
- partial `m` — `f(x)=pad+x`, `|x|<n^(1/e)`.

**Bound**: the unknown `< n^0.25` (factor) / `< n^(1/e)` (message).
**Verify**: `p|n` / `pow(m,e,n)==c`.

## Family 6 — the leak / relation

- `franklin-reiter` — `m2=a·m1+b`.
- `crt` — residues, a fault, or `dp`.
- `rsa-decrypt` / `eth-root` — the factors held.

**Bound**: linear relation / `∏pi>m` / a fault / `gcd(e,phi)>1`.
**Verify**: `pow(m,e,n)==c` / `gcd=q` / `p*q==n`.

## The bound hierarchy

```
n^0.25 ─ wiener
n^0.292 ─ boneh-durfee   (the small-d ceiling)
n^0.25 ─ coppersmith     (the partial-p window)
m^e<n ─ small-e          (the wrap)
≥e n's ─ hastad          (the broadcast)
```
