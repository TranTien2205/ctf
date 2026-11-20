# Pivot: handle/username

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

A username is the highest-yield pivot - it crosses
platforms verbatim. identity pivot depth owns it.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
