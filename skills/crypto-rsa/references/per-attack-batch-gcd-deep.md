# per-attack batch-gcd deep — the shared-prime split, the full treatment

## The mechanism

`n_i = p·q_i`, `n_j = p·q_j` for a shared `p` → `gcd(n_i,n_j) = p`. A weak or
seeded RNG produces collisions — `p` reused, both primes from a small pool, or
a predictable sequence.

## Detection

- **count** — `len(set(n_list)) >= 2` from the same generator.
- **keygen** — `random.seed`, a reused `p`, `getPrime` once, a small pool.
- **shape** — a `.json`/`.pem` set/`.txt` list of moduli.

## The bound / falsifier

A collision must exist — `gcd(n_i,n_j)>1`. All `gcd=1` → a negative; the
*count* isn't the bug.

## The attack

```bash
crypto_attack.py batch-gcd --moduli n1 n2 ...    # or --file <f>
```

```python
from math import gcd
for i in range(len(ns)):
    for j in range(i+1, len(ns)):
        g = gcd(ns[i], ns[j])
        if 1 < g:
            p = g
            qi, qj = ns[i]//p, ns[j]//p
```

## The chain

`p` → `q=n/p` → `phi` → `d` → `m` → `pow` → flag.

## The verify

`p*q==n` for each split; `pow(m,e,n)==c` for the plaintext.

## Variants

- A `.pem` batch — `RSA.importKey` each, collect `n`, `gcd`.
- A seeded RNG — regenerate the stream or `gcd` the `n`'s.
- A shared `q` not `p` — `gcd` doesn't care.

## Failure modes

- All `gcd=1` — the count ≠ the bug.
- `n` a prime power — a false "collision" if `n=p^k`.

## The honest status

Mining your Ps and Qs (Heninger et al.) — catalogue.
