# Evasion deep — how the class hides and stalls

## How the weakness hides

- **`e`=65537** — the default deflects attention; the bug is in `p`,`q` or a
  leak, not `e`. Read the keygen, not the exponent.
- **a huge `n`** — "2048-bit, too strong to factor" is the misdirection. The bug
  is a *precondition* — `p`,`q` close, a shared prime, a leak — not the size.
- **a clean `n`,`e`,`c`** — the bug is in the *generator*: `next_prime`, a seed,
  a smooth `p-1`. Read `keygen.py`.
- **a real-looking PEM** — the fields are there but one is *redacted* — that
  field is the attack surface (`coppersmith`/`crt`/`factor-from-d`).
- **`e` huge** — looks like a "strong" exponent; it *is* the small-`d` tell.
- **a JSON of moduli** — looks like a dataset; it is a `batch-gcd` target.

## How the challenge stalls

- **a bound just exceeded** — `d=n^0.30`, window `n^0.24` — the attack is
  *mathematically* closed, not "hard". Record the negative; do not retry.
- **a pad on `m`** — PKCS#1 v1.5 wraps the flag; `m` is the padded block, strip
  `\x00\x02<pad>\x00`. `pow(m,e,n)==c` held on the padded block — the *flag* is
  inside it.
- **a `gcd(e,phi)>1`** — `inverse(e,phi)` fails; that is `eth-root`, not a bug.
- **`n` multi-prime / `n=p²`** — `phi` differs; `factor-from-d`/`crt` adapt.
- **a socket that *re-encrypts*** — a computing oracle, not `crypto-rsa`.
- **proper RSA** — no violation; the class falsifier. The bug is in the
  protocol — a padding oracle, a signature forgery, a side channel.

## The recoveries

- `e=3`, `m^3≥n` → `hastad` (e n's) or `coppersmith` (partial `m`).
- `d` just over `n^0.25` → `boneh-durfee-escalate` (`m`,`t` up).
- a bound exceeded → the fallback in `negative-map.md`.
- `n` multi-prime → `phi=∏(pi-1)`, `d` still `inverse(e,phi)`.
- `n=p²` → `phi=p(p-1)`; `n` prime → `phi=n-1`.

## The honest status

Catalogue — these are published-standard stalls. `../field-notes.md` records what
actually happens.
