# The format-literal boundary — when the class is closed — deep

printf("%s", buf) passes your input as an ARGUMENT to a literal format — nothing is interpreted. The class is open only when your input IS the format argument.

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

Falsifier — every call passes your input as an argument to a literal format: nothing is interpreted; the class is closed.

## Highest-cost traps

- The class is about WHO is the format string, not whether a string reaches printf.
- printf(input) is the bug; printf("%s",input) is safe.
- A wrapper like log(buf) that calls printf(buf) internally is still open.

## Commands

```bash
r2 -A ./chal && pdf @ <func> | grep -iE 'printf|format'
```

## Cross-references

`primitive-matrix.md`
