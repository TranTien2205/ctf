# ret2dlresolve — resolving a symbol that was never imported — index

The dynamic linker's lazy-resolution machinery can be tricked into resolving an ARBITRARY symbol name at runtime: craft fake relocation/symbol/string entries, call the resolver stub, and 'system' materializes even though the binary never imported it.

## Related modules

- `ret2dlresolve-deep.md` — boundary conditions
- `ret2dlresolve-checklist.md` — operational steps
- `ret2dlresolve-catalogue.md` — case enumeration

## Cross-references

`ret2libc.md` · `fgot-overwrite.md`
