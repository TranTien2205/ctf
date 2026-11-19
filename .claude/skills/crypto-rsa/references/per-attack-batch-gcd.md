# batch-gcd — the shared-prime attack, complete

## What it is

A batch of RSA moduli `n_1..n_k` from a key generator that reused primes.
`gcd(n_i, n_j) = p` for a shared prime `p` splits both `n_i` and `n_j`.

## The mechanism

`n_i = p·q_i`, `n_j = p·q_j` → `gcd(n_i,n_j) = p`. A seeded/weak RNG that
generates `p` once and `q` fresh (or reuses a prime pool) produces collisions.

## Detection

- **count**: `len(n_list) >= 2`.
- **keygen**: `random.seed(...)`, a shared `p`, `reused_prime`, `getPrime` once.
- **shape**: a `.json`/`list`/`txt` of moduli — a *batch*.

## The bound / falsifier

A collision must exist — `gcd(n_i,n_j) > 1` for some pair. All `gcd=1` → no
shared prime → a negative; route per-`n` to `fermat`/`wiener`/etc.

## The attack

```python
from math import gcd
ns = [n1, n2, n3, ...]
for i in range(len(ns)):
    for j in range(i+1, len(ns)):
        g = gcd(ns[i], ns[j])
        if g > 1:
            p = g; q_i = ns[i]//p; q_j = ns[j]//p
            print(f'shared {p}: n{i} = {p}*{q_i}')
```

Or: `python3 tools/crypto_attack.py batch-gcd --moduli n1 n2 ...`.

## The chain

`p` → `q = n/p` → `phi = (p-1)(q-1)` → `d = inverse(e, phi)` → `m = c^d mod n`
→ `pow(m,e,n)==c`.

## The verify

`p*q == n` for each split modulus; then `pow(m,e,n)==c` for the plaintext.

## Variants

- **A `.pem` set** — extract `n` per key, `gcd` pairwise.
- **A seeded RNG** — `random.seed` + `getPrime` — regenerate the prime sequence,
  or `gcd` the emitted `n`'s.
- **A shared `q`** — same split; `gcd` doesn't care which prime is shared.

## Failure modes

- All `gcd=1` — no reuse; the count is not the bug.
- `n` already factored — a false collision if `n` was `p`·`q` for a *small*
  shared `q`.

## The honest status

Standard published attack — catalogue, no local solve.
