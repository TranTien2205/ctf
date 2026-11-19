# Per-vector map — the injection point → the value it carries

## The key vector

A public key injects `n`,`e` — the attack surface is the *number relation*
(`e` size, `p`,`q` relation), not the file. A partial private key injects the
leaked fields.

## The ciphertext vector

`c` + `n`,`e` — the wrapped `m`. `m^e<n` → a root; `m^e≥n` → the
structure/leak matters.

## The generator vector

`keygen.py` injects the *misuse* — `next_prime`, `seed`, `getPrime(d)`, `p-1`,
`e=3`, no pad, `m2=a·m1+b`, `dp`,`dq`,`qInv`, a fault. The generator line *is*
the vector.

## The batch vector

A `.json`/`list` of `n`,`e`,`c` — a *collection* of targets. `batch-gcd` for a
shared prime; `hastad` for the same `m`.

## The leak vector

`d`,`phi`,`dp`,`dq`,`qInv`,`p`-bits,`m`-partial,`p`,`q` — the terminal values.
`factor-from-d`/`crt`/`coppersmith`/`rsa-decrypt`/`eth-root`.

## The relation vector

`m2=a·m1+b`, residues `mod pi`, a fault — `franklin-reiter`, `crt`.

## The degenerate vector

`n=p²`, `n` prime, `n` multi-prime, `e`=1 — `phi` differs.

## The channel vector

a socket printing numbers → the values; a socket computing →
`crypto-symmetric-oracle`.

## The rule

The vector is *where the bug enters* — the keygen line, the redacted field, the
batch, the relation. Read it; the attack follows.
