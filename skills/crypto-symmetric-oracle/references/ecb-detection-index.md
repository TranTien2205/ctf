# ECB detection — one request, deterministic — index

ECB leaks structure: identical plaintext blocks produce identical ciphertext blocks. Detection needs one request holding enough repeated material to fill two blocks — no statistical test, no second round-trip.

## Related modules

- `ecb-detection-deep.md` — mechanism internals and boundary conditions
- `ecb-detection-variant.md` — when the surface shape changes
- `ecb-detection-checklist.md` — the ordered operational steps
- `ecb-detection-catalogue.md` — case enumeration

## Cross-references

`ecb-byte-at-a-time.md` · `ecb-cut-and-paste.md` · `block-alignment.md`
