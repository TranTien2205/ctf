# Packing the payload — endian, alignment, and width — index

The payload is raw bytes: addresses packed little-endian at the pointer width, padding to the exact offset, the chain's qwords in order.

## Related modules

- `byte-packing-deep.md` — boundary conditions
- `byte-packing-checklist.md` — operational steps
- `byte-packing-catalogue.md` — case enumeration

## Cross-references

`bad-chars.md` · `endianness-and-width.md`
