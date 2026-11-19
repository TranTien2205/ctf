# __malloc_hook / __free_hook overwrite — old glibc — deep

On glibc ≤ 2.34, __malloc_hook and __free_hook are writable function pointers called on every malloc/free — a %n write to them gives a hook that fires on the next allocation.

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

Falsifier — glibc ≥ 2.35: the hooks are gone; use GOT or ret-addr instead.

## Highest-cost traps

- __free_hook = system + a freed chunk holding '/bin/sh' is the classic.
- The hooks are libc globals — need the libc base under ASLR.
- Removed in glibc 2.35 — check the version.

## Cross-references

`got-overwrite-fmt.md` · `glibc-version-matrix.md`
