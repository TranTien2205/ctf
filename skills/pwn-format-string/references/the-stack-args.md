# The stack-args region — where high-N args live

x64 passes args 1-6 in registers (rdi,rsi,rdx,rcx,r8,r9); args 7+ are on the stack. The %N$p values at high N are stack memory — pointers, your input, the saved frame.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| %6$p+% reach the stack | stack args | the leak region |
| your input sits at arg N | find N | the buffer's index |
| saved regs at high N | frame pointers/canary | the leak |

## Steps

1. x64: rdi,rsi,rdx,rcx,r8,r9 = args 1-6; the stack args are N≥6.
2. x86: all args on the stack — N starts at 1.
3. Your input buffer lands at some N — the arg-offset-finder finds it.
4. Higher N reaches saved registers, return addresses, the canary.

## Falsifier

Falsifier — the ABI puts all needed args in registers and your input isn't a stack arg: the primitive can't reach it.

## Traps

- The arg-offset N is ABI- and call-site-dependent — measure per function.
- x86 vs x64 differ fundamentally in where args live.

## Cross-references

`arg-offset-finder.md` · `width-precision-fields.md`
