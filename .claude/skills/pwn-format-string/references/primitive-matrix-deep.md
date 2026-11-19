# The format-specifier matrix — what each one buys — deep

The specifier is the whole primitive: %p/%x read, %s dereferences, %n/%hn/%hhn write. Choosing the right one IS the exploit.

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

Falsifier — the format argument is a literal and your input is an argument to it (printf("%s", buf)): nothing is interpreted; the class is closed.

## Highest-cost traps

- %n writes the count of bytes printed SO FAR — the %c/field-width controls it.
- x64: the first 6 args are in registers; the stack-args start at %7$p-ish.
- %s dereferences a POINTER — you plant it; %p just prints the value.

## Cross-references

`arg-offset-finder.md` · `arb-read-via-s.md`
