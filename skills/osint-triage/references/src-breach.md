# Source: breach corpora

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

HaveIBeenPwned/dehashed-style lookups - email ->
breaches -> passwords/names. CTF-legal only.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
