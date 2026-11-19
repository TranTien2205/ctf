# The writable buffer — where stage-2 data can live


A chain often needs a writable region to stage data: the fake rt_sigframe,
the mprotect target, the dlresolve structures. The region must be
readable/writable and at a known address.

## Candidates

- The stack (if it's large enough / unpivoted).
- A bss/.data region (static address under non-PIE).
- A malloc'd buffer (address from a leak).

## Falsifier

No writable region at a known address: the staged data can't be placed —
the chain must avoid needing one.
