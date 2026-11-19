# The static binary — no libc to ret to


A statically-linked binary has no PLT/GOT — but it has plenty of
gadgets (the linked-in libc code) and usually a `syscall` gadget —
the direct-syscall route.

## The recipe

    pop rax ; 59
    pop rdi ; "/bin/sh" (binary's own or planted)
    pop rsi ; 0
    pop rdx ; 0
    syscall

## The abundance

Static binaries are gadget-rich — finding a syscall gadget and the
pops is usually easy; finding "/bin/sh" may need a planted string.

## Falsifier

No syscall gadget even in a static binary: the last resort is a
`int 0x80`/`sysenter`/`call rax` shape — or a different target.
