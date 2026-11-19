# CMAC, OMAC, and the MAC-variant zoo — map

| Construction | Structure | Forgery |
|---|---|---|
| raw CBC-MAC | last CBC block | variable-length splice |
| ECBC/EMAC | CBC-MAC then encrypt with K2 | splice closed; check for raw |
| CMAC/OMAC | CBC-MAC + subkey xor | closed to the naive splice |
| XCBC | three keys | closed |
| HMAC | two-pad hash | `hmac-vs-raw-mac.md` |
| GMAC | GHASH | `gcm-nonce-reuse.md` for misuse |
| Poly1305 | one-time polynomial | nonce reuse → forge |

Expanded rows and abort conditions: `cmac-and-variants.md` and `cmac-and-variants-deep.md`.
