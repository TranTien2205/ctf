# syscall/int 0x80 — the direct path


`syscall` (x64) or `int 0x80` (x86) gadgets invoke the kernel directly —
no libc needed, the static-binary path.

## x64 syscall needs

- rax = syscall number (59 = execve, 60 = exit, 0 = read, 1 = write).
- rdi, rsi, rdx = args 0-2.
- gadget: `syscall` (often `syscall; ret`).

## execve recipe

    pop rax ; 59
    pop rdi ; "/bin/sh" addr
    pop rsi ; 0
    pop rdx ; 0
    syscall

## Falsifier

No syscall/int gadget exists (dynamic binary, no syscall stub): the
syscall route is closed — ret2libc instead.
