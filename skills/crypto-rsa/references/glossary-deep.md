# Glossary deep — every term, defined

## The construction

- **n** — the modulus `p·q`; public.
- **p, q** — the secret primes.
- **φ(n), phi** — `(p-1)(q-1)` (for `n=pq`); the group order.
- **e** — the public exponent; `gcd(e,φ)=1` normally.
- **d** — the private exponent; `ed ≡ 1 mod φ`.
- **c** — the ciphertext `m^e mod n`.
- **m** — the plaintext / the flag.
- **dp, dq, qInv** — `d mod (p-1)`, `d mod (q-1)`, `q^{-1} mod p` — the CRT
  private-key components.

## The attacks

- **Wiener's attack** — `d < n^0.25` → `k/d` a CF convergent of `e/n`.
- **Boneh-Durfee** — `d < n^0.292` → bivariate small-root lattice.
- **Coppersmith's method** — small roots of `f(x)≡0 mod p`/`mod n` via LLL.
- **batch-gcd** — `gcd(n_i,n_j)` for a shared prime.
- **common-modulus** — `gcd(e1,e2)=1` → Bezout `m=c1^a c2^b`.
- **Fermat factorisation** — `n=a²-b²` for `|p-q|` small.
- **Pollard p-1** — `a^{B!}≡1 mod p` for `p-1` `B`-smooth.
- **Håstad broadcast** — same `m`, `e` moduli → CRT + root.
- **Franklin-Reiter** — `m2=a·m1+b` → a shared polynomial root.
- **Bellcore / CRT fault** — `gcd(s'^e - m, n)` leaks a prime.
- **eth-root** — `gcd(e,φ)>1` → the `g` `e`th-root candidates.
- **small-e / nth-root** — `m^e<n` → the exact root.
- **factor-from-d** — `ed-1=k·2^t·r` → split `n` via `g^r` chains.

## The bounds

- **`n^0.25`** — Wiener's `d` bound; Coppersmith-`β=½` window.
- **`n^0.292`** — Boneh-Durfee's `d` bound.
- **`n^(1/e)`** — Coppersmith partial-message bound.
- **`B`-smooth** — every prime factor of `p-1` is `≤ B`.
- **coprime** — `gcd=1`.

## The machinery

- **LLL** — the Lenstra-Lenstra-Lovász lattice reduction; finds short vectors.
- **CRT** — Chinese Remainder Theorem — `x` from `x mod p_i`.
- **CF** — continued fractions — the convergents `k_i/d_i` of `e/n`.
- **Bezout** — `a·e1+b·e2=gcd` — the extended-gcd coefficients.
- **PKCS#1 v1.5 pad** — `\x00\x02<random>\x00<m>` — strip after a recovery.
- **OAEP** — the randomized pad — defeats `hastad`/`small-e` on a wrapped `m`.

## The verify

- **`pow(m,e,n)==c`** — the plaintext gate.
- **`p*q==n`** — the factor gate.
- **`pow(c,d,n)==m`** — the `d` gate.
