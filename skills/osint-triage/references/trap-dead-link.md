# Trap: trusting a dead link

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

A result behind a dead link goes to the Wayback
Machine, not to 'cannot verify'.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
