# Trap: guessing before pivoting

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

A plausible-looking answer from one weak match -
verify with a second attribute first; decoys are
built exactly for the guess.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
