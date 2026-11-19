# Uninitialized read as a leak primitive — index

A buffer returned/read without full initialization carries stale stack bytes — pointers, the canary, addresses — a leak without a format string.

## Related modules

- `uninit-read-deep.md` — boundary conditions
- `uninit-read-checklist.md` — operational steps
- `uninit-read-catalogue.md` — case enumeration

## Cross-references

`canary-bypass.md` · `pie-leak.md`
