# Dynamic linking internals — how PLT/GOT really work — case catalogue

The PLT/GOT mechanism is the ret2plt/ret2libc/GOT-overwrite foundation: understand it and those chains write themselves.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a call to func@plt | lazy-bind via resolver | the PLT stub |
| 2 | GOT holds the resolved addr | the lookup table | overwrite it |
| 3 | first call resolves then caches | binding on demand | the lazy path |

## Falsifier

Falsifier — full RELRO binds everything at startup: no lazy path exists; GOT[x] is already the real addr.
