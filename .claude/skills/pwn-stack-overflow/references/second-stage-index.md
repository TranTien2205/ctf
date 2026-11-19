# Two-stage exploits — leak first, then exploit — index

Many chains need two rounds: first a leak (canary, libc base, stack address), then the real payload built with the leaked values.

## Related modules

- `second-stage-deep.md` — boundary conditions
- `second-stage-checklist.md` — operational steps
- `second-stage-catalogue.md` — case enumeration

## Cross-references

`canary-bypass.md` · `ret2libc.md`
