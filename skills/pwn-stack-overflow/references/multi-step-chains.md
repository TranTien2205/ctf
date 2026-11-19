# Multi-step chains — the standard compositions

## Leak → smash → flag (two-stage)

1. format-string or info-leak: canary, libc base, or PIE base.
2. cyclic offset measurement.
3. chain built with the leaked values (ret2libc system).
4. Flag from the response.

## Fork-brute → canary → smash → flag

1. Confirm forking + crash-or-clean oracle.
2. Byte-by-byte canary recovery.
3. Standard smash with the recovered canary preserved.

## ret2csu → arbitrary call → flag

1. No clean pops: __libc_csu_init universal pair.
2. Set r12 = GOT slot, rbx=0, r13/14/15 = edi/rsi/rdx.
3. Call any function → the system/execve.

## SROP → one syscall → flag

1. pop rax;ret + 15 + syscall;ret + fake rt_sigframe.
2. Whole-register control → execve or mprotect+shellcode.

## Smash → GOT overwrite → flag

1. Partial RELRO: GOT writable.
2. Arb-write to a GOT slot (via the smash or a write-where).
3. Next call to the redirected import → system.

## Smash → mprotect → shellcode

1. NX on but mprotect@plt reachable.
2. Chain: mprotect(buf,rwx) + read(buf,shellcode) + jmp buf.
3. Shellcode runs in the now-executable region.

## The rule

Each chain step has a falsifier; the chain dies at the first step that
falsifies — verify step-by-step, don't build the whole thing then test.
