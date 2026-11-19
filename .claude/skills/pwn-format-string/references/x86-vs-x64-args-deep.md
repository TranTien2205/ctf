# x86 vs x64 argument layout — where your buffer sits — deep

x86 puts all args on the stack (low N reaches your input); x64 puts the first 6 in registers (your input is at high N). The arg-offset differs fundamentally.

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

Falsifier — the ABI/layout assumption doesn't match the measured N: always measure; the N is per-call-site.

## Highest-cost traps

- x86 %1$p is your data quickly; x64 needs higher N.
- The register args on x64 mean the FIRST %p values aren't stack memory.

## Commands

```bash
readelf -h ./chal | grep Class
```

## Cross-references

`arg-offset-finder.md` · `the-stack-args.md`
