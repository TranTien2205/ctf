# No libc route — the pure-binary chain


A static binary's chain needs no libc: the gadgets are all in the
binary; the syscall is the kernel's door.

## The shape

    [pops for rax/rdi/rsi/rdx] [syscall] — execve direct.

## The string

"/bin/sh" must be in the binary's rodata or planted — check
strings first.
