# Off-by-one and single-byte overwrites — case catalogue

A single controlled byte past the buffer can still matter: zero the canary's low byte, shift the saved RBP's LSB, or corrupt a length field.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | write reaches exactly one byte past the buffer | off-by-one | LSB corruption |
| 2 | canary's low byte is 0 (usually) | canary's LSB is fixed | a byte-overwrite keeps it valid |
| 3 | saved RBP low byte corruptible | frame shift | frame-pointer control |

## Falsifier

Falsifier — the overwritten byte reaches nothing security-relevant: no exploitable effect.
