# Pivot cell: handle / paste-sites

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

Whether the `paste-sites` source yields on a `handle` pivot.

## Read

First-source, useful, or wrong-pivot - the pivot's type
against what the source indexes. First-source pairings
state the exact lookup; wrong-pivot cells are recorded so
the source is never re-tried on this pivot type.
