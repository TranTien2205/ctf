# Canary + PIE leak composition — defeating both at once — deep

PIE and a canary together need TWO leaks: a code pointer for the base AND the canary word. The fmtstr's %p run can leak both in one call.

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

Falsifier — the %p run doesn't reach the depths where both values sit: one or both stay hidden.

## Highest-cost traps

- The canary's depth and the code pointer's depth are different — read both.
- The code pointer's offset-to-base is symbol-specific — get it from the binary.

## Cross-references

`leak-via-p.md` · `skip-canary-by-write.md`
