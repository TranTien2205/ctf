# CMAC, OMAC, and the MAC-variant zoo — deep

CBC-MAC's variable-length forgery was fixed by CMAC/OMAC: the last block is
XOR'd with a derived subkey before encryption, which kills the simple
splice. Naming the construction correctly is the whole game.

## Boundary conditions

- The module's table is the discriminator: when a row's observation is absent, the row's attack is dead — do not tune it.
- Rows assume honest crypto; a tag verified before decryption overrides every row (see `authenticated-boundary.md`).
- A row that applies only under a precondition fails silently when the precondition is untested — `preconditions.md` first.
- Timing-dependent rows need 50+ samples on both sides before the row's conclusion is trusted.
- When two rows both appear to apply, run the cheaper probe first; the discriminator was designed so the cheapest probe decides.

## The table, verbatim

| Construction | Structure | Forgery |
|---|---|---|
| raw CBC-MAC | last CBC block | variable-length splice |
| ECBC/EMAC | CBC-MAC then encrypt with K2 | splice closed; check for raw |
| CMAC/OMAC | CBC-MAC + subkey xor | closed to the naive splice |
| XCBC | three keys | closed |
| HMAC | two-pad hash | `hmac-vs-raw-mac.md` |
| GMAC | GHASH | `gcm-nonce-reuse.md` for misuse |
| Poly1305 | one-time polynomial | nonce reuse → forge |

## Falsifier

The module's own abort conditions fire: the observed surface does not match any row, or a row's precondition probe returns the negative result it names.

## Cross-references

`preconditions.md` · `falsifiers.md` · `../field-notes.md`
