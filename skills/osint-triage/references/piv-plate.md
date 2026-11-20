# Pivot: license plate

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

A plate needs jurisdiction first (format, colors,
region), then the registries that exist for it.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
