# Stack pivot — when the writable area is too small — index

The buffer is too small for the chain, or the stack isn't where you want it. Pivot: point RSP elsewhere with a 'leave; ret' or 'xchg rsp, rXx' gadget.

## Related modules

- `stack-pivot-deep.md` — boundary conditions
- `stack-pivot-checklist.md` — operational steps
- `stack-pivot-catalogue.md` — case enumeration

## Cross-references

`rop-basics.md` · `fgot-overwrite.md`
