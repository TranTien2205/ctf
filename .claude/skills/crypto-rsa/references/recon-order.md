# Recon order — what to read first, second, third

## 1 — the source / the generator

`keygen.py`, `chal.py`, `gen.py` — the generator is where the bug lives. One
line names the misuse: `next_prime`, `getPrime(d)`, `seed`, `p-1`, `e=3`, no
pad. Read it before the numbers.

## 2 — the counts

`len(set(n))`, `len(set(e))`, `len(c)` — the family is in the counts:
- `≥2` `n` → `batch-gcd`/`hastad`
- `2` `e` on `1` `n` → `common-modulus`
- `≥e` `c` same `m` → `hastad`
- `1` `n` → the single-modulus attacks

## 3 — the exponent

`e` → `3/5/17` (small-e) / `65537` (default) / `~n` (small-d) / `gcd(e,phi)>1`
(`eth-root`). `e` is a one-character fingerprint.

## 4 — the leak

`d`, `phi`, `dp`, `dq`, `qInv`, `p`-bits, `m`-partial, a fault — the terminal
attacks. A `.pem`/`.der` is `n`,`e` or a partial private key.

## 5 — the relation

`m2=a·m1+b`, residues `mod pi`, a correct+faulty `sig` — `franklin-reiter`,
`crt`.

## 6 — the degenerate

`n` square / prime / smooth / multi-prime — `phi` differs; `isqrt`, `isPrime`,
`factorint`.

## The order rationale

Source first — it *names* the bug; counts second — they pick the *family*;
exponent third — `e` is the cheapest discriminator; the leak fourth — it often
ends it; relation and degenerate last — the rare cases. Then `attack-table.md`.
