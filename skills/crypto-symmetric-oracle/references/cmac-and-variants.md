# CMAC, OMAC, and the MAC-variant zoo

CBC-MAC's variable-length forgery was fixed by CMAC/OMAC: the last block is
XOR'd with a derived subkey before encryption, which kills the simple
splice. Naming the construction correctly is the whole game.

## The family

| Construction | Structure | Forgery |
|---|---|---|
| raw CBC-MAC | last CBC block | variable-length splice |
| ECBC/EMAC | CBC-MAC then encrypt with K2 | splice closed; check for raw |
| CMAC/OMAC | CBC-MAC + subkey xor | closed to the naive splice |
| XCBC | three keys | closed |
| HMAC | two-pad hash | `hmac-vs-raw-mac.md` |
| GMAC | GHASH | `gcm-nonce-reuse.md` for misuse |
| Poly1305 | one-time polynomial | nonce reuse → forge |

## Detection

- Source names: `cmac`, `omacf`, `omac1`, `CBC_MAC`.
- Tag = 16 bytes, input variable-length, no per-message subkey field: CMAC
  or raw CBC-MAC — test the splice once to distinguish.
- Tag = 16 bytes paired with a nonce field: GMAC/Poly1305.

## The one probe

Request MAC(m) for a one-block m; forge MAC(m || m') by the raw splice. If
it verifies, it was raw CBC-MAC; if rejected, CMAC-family — route out of
this branch.

## Falsifier

The MAC is CMAC/HMAC/Poly1305 — variable-length splice impossible at the
crypto level.
