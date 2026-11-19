# Syscall arg mapping — the kernel's order


x64 syscall args differ from function args: rdi, rsi, rdx, r10, r8,
r9 — NOT rcx/r8/r9 for arg4+.

## The table

- execve(59): rdi=path, rsi=argv, rdx=envp.
- read(0): rdi=fd, rsi=buf, rdx=count.
- write(1): rdi=fd, rsi=buf, rdx=count.
- mprotect(10): rdi=addr, rsi=len, rdx=prot.
- mmap(9): rdi=addr, rsi=len, rdx=prot, r10=flags, r8=fd, r9=off.
- exit(60): rdi=code.

## Falsifier

A needed syscall's arg lands in a register no gadget reaches (r10
especially): the syscall can't be composed.
