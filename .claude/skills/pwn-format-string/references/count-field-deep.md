# The count field — %c and field-width to set %n's value — deep

%n writes 'bytes printed so far'. The %Nc specifier and field-width control that count: %999c prints 999 bytes, so %n writes 999.

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

Falsifier — the count can't reach the needed value in one call (a huge address byte): use %hhn byte-wise or a different write target.

## Highest-cost traps

- %Nc counts as N printed bytes even though only 1 arg char is shown.
- The count is cumulative across all printed output in the call.
- %hhn writes count&0xff — the low byte is what matters.

## Cross-references

`arb-write-via-n.md` · `partial-write.md`
