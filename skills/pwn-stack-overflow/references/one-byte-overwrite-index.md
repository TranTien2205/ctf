# Off-by-one and single-byte overwrites — index

A single controlled byte past the buffer can still matter: zero the canary's low byte, shift the saved RBP's LSB, or corrupt a length field.

## Related modules

- `one-byte-overwrite-deep.md` — boundary conditions
- `one-byte-overwrite-checklist.md` — operational steps
- `one-byte-overwrite-catalogue.md` — case enumeration

## Cross-references

`saved-regs.md` · `canary-bypass.md`
