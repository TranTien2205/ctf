# SROP — sigreturn-oriented programming — checklist

A sigreturn syscall (nr 15 on x64, nr 139 on x86) restores the whole CPU state from a crafted frame on the stack — total register control with one gadget.

## Checklist

- [ ] Find syscall;ret and a way to set rax=15 (pop rax;ret or a controlled return path).
- [ ] Craft a 248-byte rt_sigframe on the stack: all GP regs, RIP, RSP, RFLAGS, CS/SS.
- [ ] Call syscall — the kernel restores the whole frame → execute anywhere with any registers.
- [ ] Chain: pad + pop rax;ret + 15 + syscall;ret + fake_frame.

## Abort conditions

- rax must be 15 when the syscall executes — a pop rax;ret or a leftover rax works.
- The frame is 248 bytes on x64 — the stack must hold it.
- SROP gives code exec via mprotect+read shellcode, or execve via registers — the 'one syscall to rule' move.

## Falsifier

Falsifier — no syscall;ret gadget, or the stack can't hold the frame: SROP is out.
