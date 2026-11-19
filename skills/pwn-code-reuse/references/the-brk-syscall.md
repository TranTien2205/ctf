# brk — the simpler alloc syscall


brk(addr) = syscall 12 — one arg, no flags: a simpler alloc than mmap
when r10 isn't settable.

## The chain

    pop rax ; 12
    pop rdi ; target_addr_end
    syscall

Sets the program break — a heap region grows; then write code there.
