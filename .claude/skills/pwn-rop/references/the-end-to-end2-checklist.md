# End to end — the second worked run — checklist

Companion to `the-end-to-end2.md`.

## Checklist

- [ ] 1. Offset 40 (measured).
- [ ] 2. pop_rax/pop_rdi/pop_rsi/pop_rdx/syscall all present.
- [ ] 3. /bin/sh at 0x4c3020 (strings).
- [ ] 4. Chain: the five gadgets + syscall → execve fires.
- [ ] 5. The shell's banner; cat flag; the hook.
