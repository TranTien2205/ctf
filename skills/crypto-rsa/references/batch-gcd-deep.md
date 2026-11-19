# batch-gcd deep — the shared-prime attack, the full treatment

## The mechanism

`n_i = p·q_i`, `n_j = p·q_j` for a shared prime `p` → `gcd(n_i, n_j) = p`. A weak
or seeded RNG that generates `p` once and `q` fresh — or that draws both primes
from a small pool — produces collisions. This is the "Mining your Ps and Qs"
class of bug.

## Detection

- **count** — `len(set(n_list)) >= 2` from the same generator.
- **keygen** — `random.seed(...)`, `getPrime` called once, a reused `p`, a
  comment like "efficient primes" or "shared".
- **shape** — a `.json`, `.pem` set, or `.txt` list of moduli.

## The bound / falsifier

A collision must exist — `gcd(n_i, n_j) > 1` for some pair. All `gcd=1` → no
shared prime → a **negative**; route per-`n` to `fermat`/`wiener`/etc. The
*count* of moduli is not the bug — the *collision* is.

## The attack

```python
from math import gcd
ns = [n1, n2, n3, ...]
for i in range(len(ns)):
    for j in range(i+1, len(ns)):
        g = gcd(ns[i], ns[j])
        if 1 < g:
            p = g
            qi, qj = ns[i]//p, ns[j]//p
            print(f'n[{i}] = {p} * {qi}')
            print(f'n[{j}] = {p} * {qj}')
```

Or: `python3 tools/crypto_attack.py batch-gcd --moduli n1 n2 ...` /
`--file <path>`.

## The chain

`p` → `q = n//p` → `phi = (p-1)*(q-1)` → `d = pow(e,-1,phi)` → `m = pow(c,d,n)`
→ `pow(m,e,n)==c` → the flag.

## The verify

`p*q == n` for each split modulus — the split is real. Then `pow(m,e,n)==c` for
the plaintext.

## Worked shape

```python
# n = p * q where p was reused across two keys
n1 = p * q1; n2 = p * q2
gcd(n1, n2) == p          # the collision
# → p, q1, q2 — both keys split
phi1=(p-1)*(q1-1); d1=pow(e,-1,phi1); m1=pow(c1,d1,n1)
```

## Variants

- **A `.pem` batch** — `RSA.importKey` each, collect `n`, `gcd` pairwise.
- **A seeded RNG** — `random.seed` then `getPrime` — either regenerate the
  prime stream or `gcd` the emitted `n`'s.
- **`n` sharing `q` not `p`** — `gcd` doesn't care which factor is shared.
- **A "weak prime pool"** — `p`,`q` from a small set → many collisions.

## Failure modes

- All `gcd=1` — the RNG was fine; the *count* isn't the bug.
- `n` already a prime power — a false "collision" if `n` was `p^k`.

## The honest status

Standard published attack — catalogue, no local solve.
