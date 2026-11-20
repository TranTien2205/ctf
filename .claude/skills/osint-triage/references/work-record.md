# Record the chain

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

Each hop: pivot, source, result, confidence. The answer
needs the chain; the writeup needs the evidence.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
