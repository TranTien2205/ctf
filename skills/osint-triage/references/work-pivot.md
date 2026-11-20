# Pivot-first method

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

Extract the ONE unique pivot in the handout (a handle, a
photo, a hash, a plate), work one source on it, verify,
then pivot on what it returns.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
