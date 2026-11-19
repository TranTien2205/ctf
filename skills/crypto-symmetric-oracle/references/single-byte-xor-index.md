# Single-byte and repeating-key XOR — index

A byte-XOR cipher is broken by frequency: try all 256 keys, score English-ness. Repeating-key XOR is the same problem after recovering key length by normalized Hamming distance.

## Related modules

- `single-byte-xor-deep.md` — mechanism internals and boundary conditions
- `single-byte-xor-variant.md` — when the surface shape changes
- `single-byte-xor-checklist.md` — the ordered operational steps
- `single-byte-xor-catalogue.md` — case enumeration

## Cross-references

`crib-drag.md` · `ctr-nonce-reuse.md`
