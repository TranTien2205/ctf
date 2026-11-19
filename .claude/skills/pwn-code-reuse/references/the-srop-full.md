# The full SROP recipe — every register


## Steps

1. rax = 15 (rt_sigreturn) — via pop rax or a sigreturn-imp import.
2. syscall gadget — fires the frame load.
3. The 248-byte frame follows on the stack — every register set.
4. rip in the frame = your next gadget; rdi/rsi/rdx = the args.

## The frame layout (x64)

    +0x00 r8 .. +0x38 r15 — the callee regs
    +0x40 rdi, +0x48 rsi, +0x50 rbp, +0x58 rbx
    +0x60 rdx, +0x68 rax, +0x70 rcx, +0x78 rsp
    +0x80 rip, +0x88 eflags, +0x90 cs, +0x98 fs/gs/ss

## Falsifier

The frame (248 bytes) doesn't fit the buffer.
