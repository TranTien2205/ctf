# Multi-step chains â€” the standard compositions — checklist

Companion to `multi-step-chains.md`.

## Checklist

- [ ] format-string or info-leak: canary, libc base, or PIE base.
- [ ] cyclic offset measurement.
- [ ] chain built with the leaked values (ret2libc system).
- [ ] Flag from the response.
- [ ] Confirm forking + crash-or-clean oracle.
- [ ] Byte-by-byte canary recovery.
- [ ] Standard smash with the recovered canary preserved.
- [ ] No clean pops: __libc_csu_init universal pair.
- [ ] Set r12 = GOT slot, rbx=0, r13/14/15 = edi/rsi/rdx.
- [ ] Call any function â†’ the system/execve.
- [ ] pop rax;ret + 15 + syscall;ret + fake rt_sigframe.
- [ ] Whole-register control â†’ execve or mprotect+shellcode.
- [ ] Partial RELRO: GOT writable.
- [ ] Arb-write to a GOT slot (via the smash or a write-where).
- [ ] Next call to the redirected import â†’ system.
- [ ] NX on but mprotect@plt reachable.
- [ ] Chain: mprotect(buf,rwx) + read(buf,shellcode) + jmp buf.
- [ ] Shellcode runs in the now-executable region.
