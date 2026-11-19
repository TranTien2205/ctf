# Fmtstr to RIP — redirecting execution — deep

The write primitive's goal is execution: overwrite a return address, a GOT entry, or a hook — the next return/call/malloc goes to your chain.

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

Falsifier — no writable redirect target is reachable by the write primitive, or the redirect's arg state is wrong: no execution redirect.

## Highest-cost traps

- The redirect target's CALL args come from the call site, not your fmtstr — check what's passed.
- A ret-addr redirect continues a ROP chain; a GOT redirect makes a call.

## Cross-references

`got-overwrite-fmt.md` · `ret-addr-overwrite.md`
