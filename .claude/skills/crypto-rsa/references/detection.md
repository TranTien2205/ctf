# Detection — the signals that name the attack

## The counts

- `n` count ≥2 → `batch-gcd`/`hastad`; 1 → single-modulus.
- `e` count on 1 `n` — 2 → `common-modulus`.
- `c` count ≥`e` same `m` → `hastad`.

## The exponent

- `e`=3/5/17/257 → `small-e`/`hastad`/`franklin-reiter`.
- `e`=65537 → the bug is elsewhere (a leak, the primes, a relation).
- `e`≈`n` → `wiener`/`boneh-durfee`.
- `gcd(e,phi)>1` → `eth-root`.
- `e`=1 → `c=m`.

## The leak

- `d`/`phi`/`dp`/`dq`/`qInv`/`p`/`q` → `factor-from-d`/`crt`/`rsa-decrypt`.
- `p`/`m` bits → `coppersmith-*`.
- `sig`+`sig_faulty` → `crt` Bellcore.
- `m` residues `mod pi` → `crt`.

## The degenerate

`isqrt(n)**2==n` → `n=p²` → `phi=p(p-1)` · `isPrime(n)` → `phi=n-1` ·
`factorint(n)` → smooth `n` · multi-prime → `phi=∏(pi-1)`.

## The keygen tell

`next_prime`/`p+k`/`q=p+2` → `fermat` · `seed`/reused `p` → `batch-gcd` ·
`getPrime(d)` small → `wiener`/`boneh-durfee` · `p-1` smooth → `pollard-pm1` ·
`e=3`,no pad → `small-e`/`hastad` · `a·m1+b` → `franklin-reiter` ·
`dp`,`dq`,`qInv` → `crt` · `d`/`phi`/`p`,`q` → `factor-from-d`/`rsa-decrypt` ·
`redact`/`XXXX` → `coppersmith`/`crt`/`factor-from-d`.

## The route

`attack-table.md` → `per-bound.md` → `crypto_attack.py <id>` → `verify.md`.
