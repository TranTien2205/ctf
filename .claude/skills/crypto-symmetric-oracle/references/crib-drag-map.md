# Crib-dragging — reading P1 XOR P2 — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| P1 XOR P2 contains printable-on-both-sides at some offset | valid crib hit | extend left and right |
| Crib produces gibberish everywhere | crib absent at all offsets | try common protocol words |
| Both messages partially known | stitch: each crib confirms the other | iterate the loop |

## Falsifier

Falsifier — every offset under every reasonable crib is non-printable in at least one direction: the keystreams were not the same (nonces differ) or the underlying data is binary/compressed.
