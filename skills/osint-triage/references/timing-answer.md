# When the answer is temporal

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

Questions like 'what was X on date Y' route to
archives and historical sources first - current
sources answer the wrong question.

## Pivot

Chain complete -> verify; dead end -> back to the handout.
