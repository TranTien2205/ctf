# __malloc_hook / __free_hook overwrite — old glibc — index

On glibc ≤ 2.34, __malloc_hook and __free_hook are writable function pointers called on every malloc/free — a %n write to them gives a hook that fires on the next allocation.

## Related modules

- `hooks-overwrite-deep.md` — boundary conditions
- `hooks-overwrite-checklist.md` — operational steps
- `hooks-overwrite-catalogue.md` — case enumeration

## Cross-references

`got-overwrite-fmt.md` · `glibc-version-matrix.md`
