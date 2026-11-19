# Direct parameter access — the %N$p / %N$n syntax — deep

The $ syntax addresses an argument by index: %7$p reads the 7th arg, %7$s derefs it, %7$n writes to it. The whole primitive is index-addressed.

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

Falsifier — the format string can't address your argument's position: the primitive can't reach it.

## Highest-cost traps

- glibc requires all specifiers in one call to be positional if any is — mixing fails.
- The offset N shifts with the call's frame depth.
- Argument 1 is the format string itself in some ABIs — check the indexing.

## Cross-references

`arg-offset-finder.md` · `the-stack-args.md`
