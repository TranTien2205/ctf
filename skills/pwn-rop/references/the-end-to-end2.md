# End to end — the second worked run


Static, NX, no PIE, has syscall + pops, /bin/sh in rodata:

1. Offset 40 (measured).
2. pop_rax/pop_rdi/pop_rsi/pop_rdx/syscall all present.
3. /bin/sh at 0x4c3020 (strings).
4. Chain: the five gadgets + syscall → execve fires.
5. The shell's banner; cat flag; the hook.

No leak needed — the static case's short run.
