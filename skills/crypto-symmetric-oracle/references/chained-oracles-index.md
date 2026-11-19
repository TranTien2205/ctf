# Chained oracles — combining two distinguishers — index

Sometimes neither oracle alone suffices: a verify oracle gives 1 bit but the decrypt endpoint gives length. Chain them — each oracle answers what the other can't.

## Related modules

- `chained-oracles-deep.md` — mechanism internals and boundary conditions
- `chained-oracles-checklist.md` — the ordered operational steps
- `chained-oracles-catalogue.md` — case enumeration

## Cross-references

`cbc-padding-oracle.md` · `verify-oracle.md`
