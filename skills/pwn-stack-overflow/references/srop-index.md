# SROP — sigreturn-oriented programming — index

A sigreturn syscall (nr 15 on x64, nr 139 on x86) restores the whole CPU state from a crafted frame on the stack — total register control with one gadget.

## Related modules

- `srop-deep.md` — boundary conditions
- `srop-checklist.md` — operational steps
- `srop-catalogue.md` — case enumeration

## Cross-references

`rop-basics.md` · `ret2libc.md`
