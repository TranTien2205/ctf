# Crib-dragging — reading P1 XOR P2 — index

With P1 XOR P2 in hand (from a reused keystream), a guessed word in one message reveals the corresponding bytes of the other. Slide the crib across offsets; each hit grows the recovered region.

## Related modules

- `crib-drag-deep.md` — mechanism internals and boundary conditions
- `crib-drag-variant.md` — when the surface shape changes
- `crib-drag-checklist.md` — the ordered operational steps
- `crib-drag-catalogue.md` — case enumeration

## Cross-references

`ctr-nonce-reuse.md` · `single-byte-xor.md`
