# The fd/bk pointers on the stack — the free-list boundary — index

Freed chunk metadata (fd/bk) sits near stack data; smashing into it corrupts the allocator — the stack↔heap boundary.

## Related modules

- `unsorted-bin-fd-deep.md` — boundary conditions
- `unsorted-bin-fd-checklist.md` — operational steps
- `unsorted-bin-fd-catalogue.md` — case enumeration

## Cross-references

`../pwn-heap-corruption/`
