# Hop record template

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

pivot | source | query | result | confidence | next
- six fields per hop; the writeup assembles from it.

## Pivot

Chain complete -> verify; dead end -> back to the handout.
