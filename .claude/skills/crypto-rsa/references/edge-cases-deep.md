# Edge cases deep — the degenerate and boundary shapes

## `n` is a perfect square

`n = p²` → `isqrt(n)` is exact → `phi = p(p-1)`, `d = inverse(e, phi)`. Check
`n` for a square root before assuming two primes.

## `n` is prime

`phi = n-1` → `d = inverse(e, n-1)`. A "prime modulus" is textbook RSA on a
single prime — still recoverable if the model holds. Check `isPrime(n)`.

## `n` is a product of >2 primes

`n = p·q·r` → `phi = ∏(pi-1)`. `factor-from-d`/`rsa-decrypt` still work with
the right `phi`; `fermat`/`batch-gcd`/`pollard` still find a factor; `boneh-durfee`
bound degrades (smaller `β`).

## `n` is smooth / has a small factor

`n` = many small factors → trial division / `sympy.factorint` splits it. A
smooth `n` is degenerate — `phi` is computable directly.

## `e` = 1

`c = m` — no encryption. `m = c` directly.

## `e` shares a factor with φ

`gcd(e, φ) > 1` → `inverse` fails → `eth-root`: `gcd(e,phi)` candidate roots;
`pow`+format picks the true one.

## `m` = 0 or `m` = 1

`c` = 0 or 1 trivially. `m = c`.

## `m` ≥ n

The plaintext wraps — `m mod n` is encrypted. A "decrypt" gives `m mod n`; the
full `m` is unrecoverable unless the relation leaks it.

## `c` = 0 or `c` = 1

`m` = 0 or 1 (or an `e`th root of 1 for `c=1`).

## `p` = `q` (a square)

Covered by `n=p²`. `phi = p(p-1)`.

## `d` = 1 or `e` = 1

`m` = `c`. Trivial.

## `phi` directly given

`factor-from-d` / `rsa-decrypt` — `d = inverse(e, phi)`.

## `dp`, `dq`, `qInv` given without `d`

`crt` reconstruction — `p`,`q` from `dp` (`p` divides `e·dp-1` candidates) or
the consistent `qInv`.

## `n`, `e` only — no `c`

A *key-recovery* challenge — the answer is `d`,`phi`,`p`,`q`, not `m`. The same
attacks; the verify is `pow(c,d,n)==m` skipped for `p*q==n`/`e·d≡1 mod phi`.

## `n` enormous (4096+ bits)

Size is not the bug — the precondition is. The lattice attacks still run; the
cheap ones are unchanged.
