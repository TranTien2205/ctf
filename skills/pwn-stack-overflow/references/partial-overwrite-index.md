# Partial overwrite — low-byte control without a full leak — index

Can't leak a full pointer? Overwrite only the low 1-2 bytes of a saved return or GOT entry — redirect to a nearby target in the same page.

## Related modules

- `partial-overwrite-deep.md` — boundary conditions
- `partial-overwrite-checklist.md` — operational steps
- `partial-overwrite-catalogue.md` — case enumeration

## Cross-references

`pie-leak.md` · `fgot-overwrite.md`
