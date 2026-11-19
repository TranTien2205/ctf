# Detection — naming it format-string — deep

Signals the class is open: a printf-family call whose format argument is user-controlled, and the %p leak confirms it in one probe.

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

Falsifier — the format argument is a literal (printf("%s",buf)): nothing is interpreted; the class is closed.

## Highest-cost traps

- The %p leak is the cheapest confirm in pwn — one probe.
- The class boundary is WHO is the format string, not whether a string reaches printf.

## Cross-references

`format-literal-boundary.md` · `primitive-matrix.md`
