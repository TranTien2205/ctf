# Edge cases — the degenerate RSA shapes

- `n=p²` → `phi=p(p-1)`; `n` prime → `phi=n-1`; `n` multi-prime → `phi=∏(pi-1)`.
- `e=1` → `m=c`; `m=0`/`m=1` → `c=0`/`1`.
- `gcd(e,phi)>1` → `eth-root`, not a failed `inverse`.
- `m≥n` → `m mod n` encrypted — full `m` unrecoverable.
- `c=0`/`c=1` → `m=0`/`m=1` (or an `e`th root of 1).
- `n`,`e` only, no `c` → a *key-recovery* challenge — answer `d`/`phi`/`p`,`q`.
- `n` enormous → size is not the bug; the precondition is.
- a partial `.pem` → the non-redacted field is the attack surface.
- a socket printing `n`,`e`,`c` → transport; computing → `crypto-symmetric-oracle`.
See `edge-cases-deep.md`.
