# Multi-target write — several %n in one fmtstr — index

One fmtstr can carry several %N$n writes: overwrite a GOT entry AND a return address, or write several bytes of one address via %hhn at increasing offsets.

## Related modules

- `multi-target-write-deep.md` — boundary conditions
- `multi-target-write-checklist.md` — operational steps
- `multi-target-write-catalogue.md` — case enumeration

## Cross-references

`partial-write.md` · `arb-write-via-n.md`
