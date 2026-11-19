# The GOT overwrite — the redirect


Partial RELRO: overwrite GOT[x] with a target — the next call to x
runs your function.

## The needs

- An arbitrary write (a write gadget or an upstream primitive).
- The import's GOT slot address (readelf -r).
- A call to that import after the write.

## Falsifier

Full RELRO: the GOT is read-only.
