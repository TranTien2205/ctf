# Common mistakes deep — the wrong moves, and why they fail

## "e=3 means small-e-root"

`e=3` is only weak when `m³<n`. A real flag is usually longer — `m³` wraps, the
exact root fails. Route: `hastad` (≥3 moduli of the same `m`), `coppersmith`
(partial `m`), or `franklin-reiter` (a relation). Check `m^e<n` before the root.

## "a large n is safe"

The modulus size is not the bug — a 4096-bit `n` with `q=next_prime(p)` falls to
`fermat` in seconds. The bug is a *precondition violation*, not the size. Read
the keygen.

## "a large e is strong"

`e`≈`n` is the *small-`d`* tell — `e=inverse(d,phi)` for small `d` ≈ `n`. The
larger `e`, the smaller `d` → `wiener`/`boneh-durfee`.

## "20 moduli means batch-gcd"

The count is not the bug — a *collision* is. `gcd(ni,nj)=1` everywhere → no
shared prime; `batch-gcd` is a negative. The bug might be `hastad` (same `m`) or
a per-`n` attack.

## "the PEM is the private key"

A `.pem`/`crt` *public* key is `n`,`e` only — extract and move on. A *partial*
private key's redacted field is the attack surface — `coppersmith`/`crt`/
`factor-from-d` on what is *not* redacted.

## "the lattice failed = try again"

A bound exceeded is a theorem, not a tuning problem. `d≥n^0.292` → Boneh-Durfee
cannot work; window `<n^0.25` → Coppersmith cannot work. Record the negative;
route the fallback.

## "the root is the flag"

`pow(m,e,n)==c` is the gate. A flag-shaped string that fails `pow` is a decoy;
a padded `m` is the padded block — strip `\x00\x02<pad>\x00`; an `eth-root`
candidate must `pow`-verify and match the format.

## "phi is (p-1)(q-1) always"

`n=p²` → `phi=p(p-1)`; `n` prime → `phi=n-1`; `n=p·q·r` → `phi=∏(pi-1)`. The
degenerate `n` needs the degenerate `phi`.

## "inverse(e,phi) failing is a bug"

`gcd(e,phi)>1` is `eth-root` — a *signature*, not an error. `p`,`q` held → the
gcd candidates; `pow`+format picks the true root.

## "a socket printing n,e,c is an oracle"

A socket that *prints* the values is transport — treat as the numbers. A socket
that *computes* on your `m` is `crypto-symmetric-oracle`. The difference is a
menu/loop.

## "recovered d = decrypt done"

`pow(c,d,n)==m` recovers `m`; `pow(m,e,n)==c` *verifies* it. Run both — a wrong
`d` gives garbage that may look flag-shaped.
