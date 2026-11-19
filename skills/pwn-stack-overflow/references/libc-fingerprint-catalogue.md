# Libc fingerprinting — which libc is it? — case catalogue

A leaked libc address is only useful with the right libc VERSION's offsets: fingerprint the version from two leaked symbols or the libc.so the challenge ships.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a leaked libc addr but unknown version | offsets unknown | fingerprint |
| 2 | two leaked symbols | delta between them names the version | libc-database |
| 3 | challenge ships libc.so.6 | the exact version | use its symbols |

## Falsifier

Falsifier — the leaked address doesn't match any known libc version's deltas: the leak isn't a libc pointer, or the libc is nonstandard.
