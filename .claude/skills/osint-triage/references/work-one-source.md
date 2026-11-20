# One source at a time

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

Do not query five sources on the same pivot - each source
has a best pivot type; run the right one first.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
