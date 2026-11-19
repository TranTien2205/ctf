# ret2libc — call libc functions via a leak — checklist

When the binary imports no system but links libc, a leak of ANY libc address plus the known offset reaches system()/execve(). The chain is leak → compute base → call.

## Checklist

- [ ] Leak: puts@plt on a GOT entry prints that libc function's real address.
- [ ] Compute libc_base = leaked - known_offset (the offset is version-specific — get libc.so or leak more).
- [ ] chain: pop rdi;ret + binsh_in_libc + system_addr + exit_addr.
- [ ] Send as the second stage after the leak triggers.

## Abort conditions

- The libc VERSION matters for offsets — leak more than one address or fingerprint it.
- puts(GOT[x]) prints the resolved address of x — if x isn't resolved yet it's the PLT address; call it once first.
- system needs '/bin/sh' — a leak of libc gives the string too (search the leaked range or compute its offset).

## Falsifier

Falsifier — no leak primitive exists (no read to an address you control, no puts of a pointer): libc base stays hidden; ret2libc is out without it.
