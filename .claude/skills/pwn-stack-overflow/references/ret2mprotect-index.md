# ret2mprotect — make the stack executable — index

Can't disable NX but can call mprotect: mark a region RWX, then write and jump to shellcode there.

## Related modules

- `ret2mprotect-deep.md` — boundary conditions
- `ret2mprotect-checklist.md` — operational steps
- `ret2mprotect-catalogue.md` — case enumeration

## Cross-references

`ret2shellcode.md` · `rop-basics.md`
