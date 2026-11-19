# The x64 registers — the arg registers


Function args: rdi, rsi, rdx, rcx, r8, r9 — the first six.
Syscall args: rdi, rsi, rdx, r10, r8, r9 — note r10.

## The pops

Each arg register needs a pop — the scarcest (rdx, the rare ones)
constrain the chain first.
