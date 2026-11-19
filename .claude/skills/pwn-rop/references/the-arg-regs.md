# The arg registers — the deep list


x64 SysV arg registers: rdi, rsi, rdx, rcx, r8, r9 — integer/pointer
args in order; xmm0-7 for floats; stack for the rest.

## The syscall set

rdi, rsi, rdx, r10, r8, r9 — note r10 for the fourth; rcx is
destroyed by the syscall instruction itself (holds the return addr).
