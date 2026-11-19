# The 64KB window — %hn reach


A %hn writes 2 bytes — the low 16 bits. A same-64KB redirect (the target
shares the high 6 bytes) is reachable with ONE specifier — no byte-wise
composition.

## Decision

- target's high 6 bytes match: %hn suffices — one write.
- target differs above 64KB: need %n or %hhn sequence — more writes.

## Steps

1. Compare the slot's current value to the target.
2. If only the low 2 bytes differ: one %hn writes them.
3. In-binary targets (non-PIE) almost always fit the 64KB window.

## Falsifier

The target differs above byte 2: needs %n or multiple %hhn.
