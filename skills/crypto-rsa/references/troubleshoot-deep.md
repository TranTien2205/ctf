# Troubleshoot deep — the failure → the read → the file

## The arithmetic is slow

- **The LLL** (`boneh-durfee`,`coppersmith`) — `fpylll` absent → pure-python LLL
  on a `ω~O(m²)` lattice. Give it the budget; raise `m`,`t` to approach the
  bound. `crypto_attack.py list` reports `lll_backend`.
- **`fermat`** — the `a` walk is `O(|p-q|)`; `--max-iters` bounds it.
- **`pollard-pm1`** — `a^{B!}` is `O(B)` `pow`s; `B` bounds it.

## The attack returns nothing

- **`wiener`/`boneh-durfee`** — `d≥n^0.25`/`n^0.292` → the bound, not a failure.
- **`coppersmith`** — the window `< n^0.25`/`n^(1/e)` → the leak is too small.
- **`fermat`** — `|p-q|` too large → the `a` budget passed.
- **`hastad`** — `<e` n's / `∏n<m^e` / a pad → the CRT didn't reach `m`.
- **`common-modulus`** — `gcd(e1,e2)>1` → `m^gcd`, not `m`.
- **`pollard-pm1`** — `p-1` not `B`-smooth → `gcd=1`.
- **`franklin-reiter`** — the relation isn't `a·m1+b`.

## The value fails the verify

- **`pow(m,e,n)≠c`** — the wrong `m` (`eth-root` root, a decoy, a wrong pad
  strip). Try the other `g` candidates; check `pow` on the padded block.
- **`p*q≠n`** — the wrong `p` (a gcd-1 false split, a partial `p`).
- **`pow(c,d,n)`≠`m`/`pow(m,e,n)`≠`c`** — the wrong `d`/`phi`.

## The wrong class

- Every bound met → **no RSA violation** → `crypto-symmetric-oracle`,
  `crypto-ecc-dlog`, `crypto-prng`, or `web-*`. `class-boundary.md`.

## The tool contract

- `crypto_attack.py <id> --help` — the real flags. The contract test scans the
  corpus — an invented flag fails the gate.
- `franklin-reiter`, the Bellcore `sig`, and `dp`/`dq`/`qInv` are **manual** —
  no `crypto_attack.py` flag.
