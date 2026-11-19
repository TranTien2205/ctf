# The stack-args region — where high-N args live — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| %6$p+% reach the stack | stack args | the leak region |
| your input sits at arg N | find N | the buffer's index |
| saved regs at high N | frame pointers/canary | the leak |

## Falsifier

Falsifier — the ABI puts all needed args in registers and your input isn't a stack arg: the primitive can't reach it.
