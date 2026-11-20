# Source: username search

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

whatsmyname/namechk-style sweeps across platforms -
profile existence maps the person's footprint.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
