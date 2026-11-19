# The stack-args region — where high-N args live — case catalogue

x64 passes args 1-6 in registers (rdi,rsi,rdx,rcx,r8,r9); args 7+ are on the stack. The %N$p values at high N are stack memory — pointers, your input, the saved frame.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | %6$p+% reach the stack | stack args | the leak region |
| 2 | your input sits at arg N | find N | the buffer's index |
| 3 | saved regs at high N | frame pointers/canary | the leak |

## Falsifier

Falsifier — the ABI puts all needed args in registers and your input isn't a stack arg: the primitive can't reach it.
