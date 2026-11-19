# Return-address overwrite via %n — write into saved state — index

The saved return address on the stack is a write target: overwrite it with the target's address and the function's return goes to your chain — %n as the write primitive.

## Related modules

- `ret-addr-overwrite-deep.md` — boundary conditions
- `ret-addr-overwrite-checklist.md` — operational steps
- `ret-addr-overwrite-catalogue.md` — case enumeration

## Cross-references

`got-overwrite-fmt.md` · `arb-write-via-n.md`
