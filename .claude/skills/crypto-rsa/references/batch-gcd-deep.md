# batch-gcd deep — the shared-prime break, in full

## The precondition

Two or more RSA moduli produced by a generator that reuses a prime. The reuse is
the bug — a bad RNG, a seeded counter, a keygen that does `q = next_prime(p)`
for one and `p = next_prime(seed2)` for another landing on the same value.

## Why gcd works

`n1 = p·q1`, `n2 = p·q2` → `gcd(n1,n2) = p` exactly, because `p` divides both and
nothing else does (assuming `q1 ≠ q2`). One `gcd` call splits two moduli.

## The batch algorithm

For `k` moduli, the naive O(k²) pairwise `gcd` is fine for a CTF batch:

```python
from math import gcd
shared = {}
for i in range(len(ns)):
    for j in range(i+1, len(ns)):
        g = gcd(ns[i], ns[j])
        if 1 < g < ns[i]:
            shared[i]=g; shared[j]=g
```

For very large batches, a **product tree + remainder tree** computes `gcd(ni,
∏n / ni)` efficiently — but a CTF is small; the pairwise loop is the right tool.

## The tool

```bash
python3 tools/crypto_attack.py batch-gcd --moduli n1 n2 n3 ... --e <e> --c <c>
```

## The bound / falsifier

- Needs **≥2** moduli. One `n` → never.
- Needs **a collision** — all `gcd=1` → proper RNG → negative.

## The verify

`p*q==ni` → `d_i = inverse(e, (p-1)(q_i-1))` → `pow(c_i, d_i, n_i) == m` →
`pow(m, e, n_i)==c_i`.

## The real-world shape

"Mining your Ps and Qs" (2012) factored ~0.5% of the public TLS/SSH key space
this way — embedded devices with poor entropy produced shared primes at scale.
The Debian OpenSSL RNG bug (2008) is the extreme: ~32k possible keys. The CTF
version is the same shape, miniaturised.

## The traps

- A `.json`/`keylist` carries every `n` — extract them all; the colliding pair
  may be non-adjacent.
- A shared `q` is identical — `gcd` doesn't care which prime repeats.
- A shared `e` is normal — only a shared **prime** splits.
- Proper RNG → all `gcd=1` → the count is not a bug.
