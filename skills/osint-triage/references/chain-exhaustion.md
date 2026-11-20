# When a pivot exhausts

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

A pivot that returns nothing on its best source gets
one second source, then back to the handout for a
different pivot - do not grind a dead pivot.

## Pivot

Chain complete -> verify; dead end -> back to the handout.
