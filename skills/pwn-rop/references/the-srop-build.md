# Building SROP — the frame chain


Sigreturn-oriented programming: set rax=15, hit a syscall gadget,
and place a full fake sigframe after it — every register including
rip loads at once.

## The layout

    pop rax ; 15
    syscall_gadget
    <248-byte fake frame: r8..r15, rdi, rsi, rbp, rbx, rdx, rax,
     rcx, rsp, rip, eflags, cs, fs/gs, ss>

## The needs

- A way to set rax=15 (pop rax, or a write to a saved-rax slot).
- The 248 bytes must fit the buffer.

## The payoff

Sets rsp AND rip — the pivot and the call in one shot.
