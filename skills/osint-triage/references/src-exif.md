# Source: EXIF/metadata

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

exiftool on the artifact - GPS, camera, timestamps;
the cheapest first source on any media pivot.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
