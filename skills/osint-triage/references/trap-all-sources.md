# Trap: all sources on one pivot

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

Running ten sources on a weak pivot wastes the
clock - the right source on the right pivot
first.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
