# system() vs execve() — the call choice

ret2system calls system('/bin/sh') via libc; execve needs the syscall gadget. system is easier; execve works where libc resolution fails.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| libc reachable + /bin/sh | system easier | ret2system |
| no libc leak but syscall;ret exists | execve via syscall | regs + syscall |
| static binary | no system@plt | execve syscall only |

## Steps

1. Dynamic + leak: ret2libc system('/bin/sh').
2. Static or no-leak: execve syscall — rax=59, rdi='/bin/sh', rsi=0, rdx=0, syscall.
3. The syscall path needs pop rax/rdi/rsi/rdx + syscall gadgets.
4. system is one call; execve is the register-driven version.

## Falsifier

Falsifier — neither a libc base nor the syscall gadgets exist: no exec path.

## Traps

- Static binaries have no PLT/system — execve via raw syscall is the way.
- system('/bin/sh') needs the string; execve needs it in rdi.
- On x64, execve is syscall 59.

## Commands

```bash
r2 -A ./chal && /R syscall
```

## Cross-references

`ret2libc.md` · `rop-basics.md`
