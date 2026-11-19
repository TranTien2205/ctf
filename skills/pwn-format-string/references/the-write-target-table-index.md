# The write-target table — GOT vs ret-addr vs hook — index

Three redirectable targets for a %n write: a GOT entry (call-time redirect), a saved return address (return-time), a malloc/free hook (alloc-time). Choose by what's reachable and what fires.

## Related modules

- `the-write-target-table-deep.md` — boundary conditions
- `the-write-target-table-checklist.md` — operational steps
- `the-write-target-table-catalogue.md` — case enumeration

## Cross-references

`got-overwrite-fmt.md` · `ret-addr-overwrite.md` · `hooks-overwrite.md`
