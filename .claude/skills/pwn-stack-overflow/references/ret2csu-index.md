# ret2csu — the universal gadget pair — index

__libc_csu_init carries two gadgets that set rdx, rsi, rdi, and call an arbitrary function — the fallback when the binary is sparse of clean pops.

## Related modules

- `ret2csu-deep.md` — boundary conditions
- `ret2csu-checklist.md` — operational steps
- `ret2csu-catalogue.md` — case enumeration

## Cross-references

`rop-basics.md` · `ret2libc.md`
