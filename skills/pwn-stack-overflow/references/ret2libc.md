# ret2libc — call libc functions via a leak

When the binary imports no system but links libc, a leak of ANY libc address plus the known offset reaches system()/execve(). The chain is leak → compute base → call.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| libc linked, ASLR on | need a libc leak | leak via puts/printf/read |
| a GOT entry you can print | base recoverable | puts(GOT[x]) |
| no useful import but libc present | libc functions reachable | compute + call |

## Steps

1. Leak: puts@plt on a GOT entry prints that libc function's real address.
2. Compute libc_base = leaked - known_offset (the offset is version-specific — get libc.so or leak more).
3. chain: pop rdi;ret + binsh_in_libc + system_addr + exit_addr.
4. Send as the second stage after the leak triggers.

## Falsifier

Falsifier — no leak primitive exists (no read to an address you control, no puts of a pointer): libc base stays hidden; ret2libc is out without it.

## Traps

- The libc VERSION matters for offsets — leak more than one address or fingerprint it.
- puts(GOT[x]) prints the resolved address of x — if x isn't resolved yet it's the PLT address; call it once first.
- system needs '/bin/sh' — a leak of libc gives the string too (search the leaked range or compute its offset).

## Commands

```bash
r2 -A ./chal && is @ libc
readelf -r ./chal | grep GOT
```

## Cross-references

`ret2plt.md` · `pie-leak.md` · `rop-basics.md`
