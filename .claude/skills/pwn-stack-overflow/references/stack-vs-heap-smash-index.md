# Stack smash vs heap metadata — the ownership boundary — index

Both are 'write past a buffer'; which class owns it depends on WHERE the corruption lands: stack frames belong here, heap chunk metadata belongs to pwn-heap-corruption.

## Related modules

- `stack-vs-heap-smash-deep.md` — boundary conditions
- `stack-vs-heap-smash-checklist.md` — operational steps
- `stack-vs-heap-smash-catalogue.md` — case enumeration

## Cross-references

`class-boundary.md` · `unsorted-bin-fd.md`
