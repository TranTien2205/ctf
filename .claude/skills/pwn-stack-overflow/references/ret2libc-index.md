# ret2libc — call libc functions via a leak — index

When the binary imports no system but links libc, a leak of ANY libc address plus the known offset reaches system()/execve(). The chain is leak → compute base → call.

## Related modules

- `ret2libc-deep.md` — boundary conditions
- `ret2libc-checklist.md` — operational steps
- `ret2libc-catalogue.md` — case enumeration

## Cross-references

`ret2plt.md` · `pie-leak.md` · `rop-basics.md`
