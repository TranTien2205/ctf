# GOT overwrite via %n — partial RELRO's prize — index

Under partial RELRO, the GOT is writable: plant a GOT slot's address as a %N$n arg and overwrite it — the next call to that import goes to your target.

## Related modules

- `got-overwrite-fmt-deep.md` — boundary conditions
- `got-overwrite-fmt-checklist.md` — operational steps
- `got-overwrite-fmt-catalogue.md` — case enumeration

## Cross-references

`ret-addr-overwrite.md` · `partial-write.md`
