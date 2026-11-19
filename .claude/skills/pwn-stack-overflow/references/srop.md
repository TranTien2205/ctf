# SROP — sigreturn-oriented programming

A sigreturn syscall (nr 15 on x64, nr 139 on x86) restores the whole CPU state from a crafted frame on the stack — total register control with one gadget.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| syscall;ret gadget exists | srop possible | one gadget + the frame |
| you control 300+ bytes of stack | frame fits | lay out the rt_sigframe |
| need control of many registers at once | srop is the answer | one syscall |

## Steps

1. Find syscall;ret and a way to set rax=15 (pop rax;ret or a controlled return path).
2. Craft a 248-byte rt_sigframe on the stack: all GP regs, RIP, RSP, RFLAGS, CS/SS.
3. Call syscall — the kernel restores the whole frame → execute anywhere with any registers.
4. Chain: pad + pop rax;ret + 15 + syscall;ret + fake_frame.

## Falsifier

Falsifier — no syscall;ret gadget, or the stack can't hold the frame: SROP is out.

## Traps

- rax must be 15 when the syscall executes — a pop rax;ret or a leftover rax works.
- The frame is 248 bytes on x64 — the stack must hold it.
- SROP gives code exec via mprotect+read shellcode, or execve via registers — the 'one syscall to rule' move.

## Commands

```bash
r2 -A ./chal && /R syscall
```

## Cross-references

`rop-basics.md` · `ret2libc.md`
