# Source: reverse image search

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

Google lens, tineye, yandex - find earlier copies
and the origin page. Crop to the distinctive part.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
