# Evidence — what proves each stage — deep

Each stage has a hard signal: the leak (reflected pointers), the offset (0x41414141 at N), the write (the target's value changed), the redirect (execution went to your target).

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

Falsifier — the write's target doesn't change when %n fires: the pointer isn't at the expected arg position; re-find N.

## Highest-cost traps

- A leak that shows only the literal 'AAAA' means the buffer isn't a printf arg.
- The write is proven by the target's changed value, not the %n syntax.

## Cross-references

`workflow.md` · `falsifiers.md`
