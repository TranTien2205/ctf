# Syscall arg mapping — the kernel's order — checklist

Companion to `the-syscall-args.md`.

## Checklist

- [ ] execve(59): rdi=path, rsi=argv, rdx=envp.
- [ ] read(0): rdi=fd, rsi=buf, rdx=count.
- [ ] write(1): rdi=fd, rsi=buf, rdx=count.
- [ ] mprotect(10): rdi=addr, rsi=len, rdx=prot.
- [ ] mmap(9): rdi=addr, rsi=len, rdx=prot, r10=flags, r8=fd, r9=off.
- [ ] exit(60): rdi=code.
