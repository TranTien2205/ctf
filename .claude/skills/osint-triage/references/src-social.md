# Source: social platforms

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

The platform's own search and profile data -
public-only; each platform's quirks are in
ctf-osint.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
