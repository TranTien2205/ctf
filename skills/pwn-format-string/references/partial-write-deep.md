# Partial write — %hn / %hhn for byte-level control — deep

A full %n writes a qword; %hn writes 2 bytes; %hhn writes 1. Byte-wise writes let you set a large value (like an address) without printing billions of bytes for the count.

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

Falsifier — the byte-precision write can't compose the needed value at the reachable positions: the write is incomplete.

## Highest-cost traps

- %hhn writes count&0xff — set the count so its low byte is your target byte.
- Multiple %hhn in one fmtstr write several bytes — order them.
- The count is cumulative — reset via a new call or compute the deltas.

## Cross-references

`got-overwrite-fmt.md` · `arb-write-via-n.md`
