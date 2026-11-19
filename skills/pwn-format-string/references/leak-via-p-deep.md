# Leak via %p/%x — reading the stack — deep

A run of %p specifiers dumps consecutive stack words: pointers, the canary, return addresses — the leak primitive that feeds every downstream chain.

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

Falsifier — the output truncates the %p run or only some args are reachable: the needed depth isn't readable.

## Highest-cost traps

- A %p leak is data-dependent — the canary's depth varies by call depth.
- PIE base needs a code pointer; libc base needs a libc pointer — different leaks.
- The canary ends in 00 (little-endian) — the signature is the 00 byte.

## Cross-references

`format-string-leak.md` · `canary-pie-composition.md`
