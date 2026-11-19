# Libc fingerprinting — which libc is it? — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a leaked libc addr but unknown version | offsets unknown | fingerprint |
| two leaked symbols | delta between them names the version | libc-database |
| challenge ships libc.so.6 | the exact version | use its symbols |

## Falsifier

Falsifier — the leaked address doesn't match any known libc version's deltas: the leak isn't a libc pointer, or the libc is nonstandard.
