# Off-by-one and single-byte overwrites — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| write reaches exactly one byte past the buffer | off-by-one | LSB corruption |
| canary's low byte is 0 (usually) | canary's LSB is fixed | a byte-overwrite keeps it valid |
| saved RBP low byte corruptible | frame shift | frame-pointer control |

## Falsifier

Falsifier — the overwritten byte reaches nothing security-relevant: no exploitable effect.
