# Dynamic linking internals — how PLT/GOT really work — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a call to func@plt | lazy-bind via resolver | the PLT stub |
| GOT holds the resolved addr | the lookup table | overwrite it |
| first call resolves then caches | binding on demand | the lazy path |

## Falsifier

Falsifier — full RELRO binds everything at startup: no lazy path exists; GOT[x] is already the real addr.
