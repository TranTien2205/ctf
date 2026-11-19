# Real-world cases — the published shapes this corpus models

## The mining-vehicle / close-prime keygen

A generator that derives `q` from `p` — `next_prime(p)`, `p+k`, `p` reseeded
deterministically. Published pattern: `|p-q|` small → `fermat` splits `n` in
seconds. This is the most common "RSA" CTF bug.

## The shared-prime batch

A key generator with a weak/seeded RNG that reuses primes — published as the
"Mining your Ps and Qs" family. `batch-gcd` over a `.json` of moduli: a
collision `gcd(ni,nj)=p` splits both. The count is not the bug; the collision is.

## The Wiener device

A "small private exponent for fast decryption" — `e=inverse(d,phi)` ≈ `n`.
Published: `d<n^0.25` → Wiener's CF; `d<n^0.292` → Boneh-Durfee. The tell is the
exponent size, not the modulus.

## The low-exponent broadcast

`e=3` or `e=17`, the same `m` encrypted for `e` recipients — the Håstad
broadcast attack, published 1988. CRT + integer root. A pad defeats it.

## The common-modulus broadcast

Two exponents `e1`,`e2` (`gcd=1`) on one `n`, same `m` — the common-modulus
attack, a Bezout. Published as the textbook "no shared modulus" rule.

## The partial-key-exposure recovery

A `priv.pem` with `p`/`d`/`dp` partially redacted or leaked — Coppersmith's
small-root (1996) recovers `p` if `≥n/4` bits are known in a contiguous window;
`crt` recovers `p`,`q` from `dp`,`dq`,`qInv`.

## The fault attack (Bellcore)

A CRT-signing device that occasionally returns a bad signature — `gcd(s'^e-m,n)`
leaks `q` (Boneh-DeMillo-Lipton 1997). The `crt` module handles it.

## The smooth-predecessor prime

`p` chosen so `p-1` is smooth (or generated weakly) — Pollard's `p-1` method
splits it. The tool's `pollard-pm1` with a `B` bound.

## The honest status

These are **published-standard** shapes — the corpus models them; none is a
local solve. `verified-chains.md` records the standing.
