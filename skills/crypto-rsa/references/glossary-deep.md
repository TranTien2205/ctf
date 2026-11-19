# Glossary deep — every term, indexed

## The parameters

- **`n`** = `p·q` — the modulus; the product of two primes.
- **`e`** — the public exponent; `gcd(e,φ)=1` normally.
- **`d`** — the private exponent; `ed≡1 mod φ`.
- **`φ`** = `(p-1)(q-1)` — Euler's totient; `λ=lcm(p-1,q-1)` is the Carmichael form.
- **`dp`,`dq`,`qInv`** — the CRT exponents (`d mod p-1`, `d mod q-1`,
  `q^{-1} mod p`).
- **`c`** = `m^e mod n` — the ciphertext.

## The attacks

- **continued fraction (CF)** — `e/n`'s convergents `k/d` — Wiener.
- **LLL** — the lattice reduction; Boneh-Durfee, Coppersmith.
- **Coppersmith** — small roots of `f(x)≡0 mod p`/`mod n` via LLL.
- **Håstad broadcast** — CRT + root over `e` coprime moduli.
- **Bezout** — `a·e1+b·e2=1` — common-modulus.
- **Fermat** — `n=a²-b²` — close primes.
- **Pollard p-1** — `gcd(a^{B!}-1,n)` — smooth predecessor.
- **Bellcore** — a faulty CRT signature → `gcd(s'^e-m,n)`.
- **Franklin-Reiter** — `gcd` of related polynomials.
- **e-th root** — `gcd(e,φ)>1` → `g` roots.

## The bounds

- `n^0.25` (Wiener `d`, Coppersmith factor) · `n^0.292` (Boneh-Durfee `d`) ·
  `n^(1/e)` (Coppersmith message) · `m^e<n` · `≥e` n's · `B`-smooth · `∏pi>m`.

## The verify

`pow(m,e,n)==c` / `p*q==n` / `pow(c,d,n)==m` — the deterministic gates.
