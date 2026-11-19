# Partial write — %hn / %hhn for byte-level control — index

A full %n writes a qword; %hn writes 2 bytes; %hhn writes 1. Byte-wise writes let you set a large value (like an address) without printing billions of bytes for the count.

## Related modules

- `partial-write-deep.md` — boundary conditions
- `partial-write-checklist.md` — operational steps
- `partial-write-catalogue.md` — case enumeration

## Cross-references

`got-overwrite-fmt.md` · `arb-write-via-n.md`
