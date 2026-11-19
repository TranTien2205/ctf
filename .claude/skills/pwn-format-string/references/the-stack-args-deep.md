# The stack-args region — where high-N args live — deep

x64 passes args 1-6 in registers (rdi,rsi,rdx,rcx,r8,r9); args 7+ are on the stack. The %N$p values at high N are stack memory — pointers, your input, the saved frame.

## Mechanism internals

The format string is an interpreter: each specifier consumes an argument by position, %p/%x read, %s dereferences, %n writes the cumulative byte-count. The whole primitive is argument-position arithmetic plus count control — the exploit is locating your planted value's index N and steering the count to the value you want written.

## Boundary conditions

- x64: args 1-6 in registers; stack args N≥6.
- A literal format closes the class.
- Full RELRO closes GOT.
- glibc ≥2.35 removes the hooks.
- %s/%n reads/writes until a \x00 — null bytes truncate.
- The count is cumulative — byte-wise writes compose it.

## Falsifier

Falsifier — the ABI puts all needed args in registers and your input isn't a stack arg: the primitive can't reach it.

## Highest-cost traps

- The arg-offset N is ABI- and call-site-dependent — measure per function.
- x86 vs x64 differ fundamentally in where args live.

## Cross-references

`arg-offset-finder.md` · `width-precision-fields.md`
