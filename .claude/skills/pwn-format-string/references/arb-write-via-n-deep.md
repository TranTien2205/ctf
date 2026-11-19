# Arbitrary write via %n — the count write — deep

%n writes 'the number of bytes printed so far' to a pointer argument. Control the count with %c/field-width and you write an arbitrary value to an arbitrary address — the write primitive.

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

Falsifier — you can't plant a pointer at a %N$n position, or the write count can't reach the needed value: no controlled write.

## Highest-cost traps

- %n writes the CUMULATIVE count — all printed bytes before it count.
- %hhn writes 1 byte, %hn 2, %n 8 — choose by the target's width.
- The count must be a small positive number — use %hhn for byte-wise.

## Cross-references

`got-overwrite-fmt.md` · `multi-target-write.md`
