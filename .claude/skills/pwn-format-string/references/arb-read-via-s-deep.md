# Arbitrary read via %s — dereference a planted pointer — deep

%s dereferences a pointer argument — plant a pointer where a %N$s arg reads it and %s prints the memory it points to. An arbitrary read in one specifier.

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

Falsifier — you can't plant a pointer where a %N$s arg reads it: no controlled dereference; only the leak-via-%p path remains.

## Highest-cost traps

- %s reads until a null byte — a \x00 in the target truncates the read.
- The pointer must be at a %N$s-readable argument position.
- A GOT entry or a flag-path address is the usual target.

## Cross-references

`arb-write-via-n.md` · `arg-offset-finder.md`
