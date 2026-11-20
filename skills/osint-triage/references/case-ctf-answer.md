# Case flow: flag in public data

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

The answer is a string published somewhere: identify
the publication type (paste, repo, social post, record),
then the source family that indexes it.

## Pivot

Chain complete -> verify; dead end -> back to the handout.
