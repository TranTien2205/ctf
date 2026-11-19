# Syscall numbers — the rax values — map

Companion to `the-syscall-num.md`.

| Call | x64 rax | x86 eax |
|---|---|---|
| read | 0 | 3 |
| write | 1 | 4 |
| execve | 59 | 11 |
| exit | 60 | 1 |
| mprotect | 10 | 125 |
| mmap | 9 | 90 |
| rt_sigreturn | 15 | 77 |
