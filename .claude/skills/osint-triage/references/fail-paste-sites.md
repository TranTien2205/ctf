# When paste-sites fails

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

When `paste-sites` returns nothing: the three usual causes
(stripped data, private/recent content, wrong pivot type),
the one fallback source, and the signal to abandon the
pivot entirely rather than re-query.

## Abandon

Two best-source misses on one pivot -> back to the handout
for a different pivot.
