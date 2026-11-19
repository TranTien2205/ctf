# syscall/int 0x80 — the direct path — checklist

Companion to `syscall-gadgets.md`.

## Checklist

- [ ] rax = syscall number (59 = execve, 60 = exit, 0 = read, 1 = write).
- [ ] rdi, rsi, rdx = args 0-2.
- [ ] gadget: `syscall` (often `syscall; ret`).
