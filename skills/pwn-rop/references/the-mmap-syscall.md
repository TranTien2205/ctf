# The mmap syscall — allocating RWX


mmap via syscall (num=9): rdi=addr, rsi=len, rdx=prot, r10=flags,
r8=fd, r9=off — the four+arg registers.

## The r10 problem

r10's pop is rare — substitutes: a default-flags path, brk(12) with
one arg, or an existing WX region.
