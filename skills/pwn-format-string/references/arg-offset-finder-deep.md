# The argument-offset finder — where your buffer lands — deep

Every %N$p or %N$n needs the offset N where YOUR input sits as a printf argument. AAAA.%N$p scanning N until 0x41414141 returns is the measurement.

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

Falsifier — your input never appears as a %N$p value at any N: the buffer isn't a printf argument; the primitive can't reach it.

## Highest-cost traps

- The offset N is per-call — it shifts if the call site changes.
- x86: all args on the stack, so N starts low; x64: the register args come first.
- The planted pointer for %s must land where a %N$s arg reads it.

## Commands

```bash
# send 'AAAA.%1$p'..'AAAA.%20$p' and find which prints 0x41414141
```

## Cross-references

`primitive-matrix.md` · `the-stack-args.md`
