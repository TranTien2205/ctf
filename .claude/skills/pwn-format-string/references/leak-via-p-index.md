# Leak via %p/%x — reading the stack — index

A run of %p specifiers dumps consecutive stack words: pointers, the canary, return addresses — the leak primitive that feeds every downstream chain.

## Related modules

- `leak-via-p-deep.md` — boundary conditions
- `leak-via-p-checklist.md` — operational steps
- `leak-via-p-catalogue.md` — case enumeration

## Cross-references

`format-string-leak.md` · `canary-pie-composition.md`
