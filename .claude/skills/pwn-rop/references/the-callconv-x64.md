# x64 SysV deep — the register order


The order: rdi rsi rdx rcx r8 r9 — then stack. Float args in xmm0-7
(rarely needed). The callee may use red-zone bytes below rsp — the
chain shouldn't live there.
