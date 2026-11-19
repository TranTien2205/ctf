# GOT overwrite — partial RELRO — index

Under partial RELRO, the GOT stays writable: overwrite an imported function's GOT slot to point at system/another function — the next call to it goes to your target.

## Related modules

- `fgot-overwrite-deep.md` — boundary conditions
- `fgot-overwrite-checklist.md` — operational steps
- `fgot-overwrite-catalogue.md` — case enumeration

## Cross-references

`ret2libc.md` · `write-where.md`
