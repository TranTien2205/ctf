# The sigreturn frame — all registers at once


rt_sigreturn restores every register from a 248-byte frame on the
stack — one syscall sets rdi/rsi/rdx/rip AND everything else.

## The frame (x64)

    +0x00..: the register block — r8..r15, rdi, rsi, rbp, rbx,
             rdx, rax, rcx, rsp, rip, eflags, cs/gs/fs/ss...

Set rax=15, call syscall, lay the frame after — the whole CPU state
is yours.

## Falsifier

The frame doesn't fit the buffer or no syscall gadget exists.
