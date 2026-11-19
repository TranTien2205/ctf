# Return-address overwrite via %n — write into saved state — deep

The saved return address on the stack is a write target: overwrite it with the target's address and the function's return goes to your chain — %n as the write primitive.

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

Falsifier — the saved return's stack address isn't predictable/leakable, or the write can't reach it: no ret-addr redirect.

## Highest-cost traps

- The saved return's address is a STACK address — needs a stack leak or predictable layout.
- %n writes 8 bytes — usually you want %hhn at controlled offsets for a targeted value.
- PIE + ASLR means the stack address must be leaked.

## Cross-references

`got-overwrite-fmt.md` · `arb-write-via-n.md`
