# Case flow: photo to coordinates

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

exif -> if no GPS, feature checklist (script, driving side,
plates) -> region -> maps verification -> coordinates.
The standard five-hop photo chain.

## Pivot

Chain complete -> verify; dead end -> back to the handout.
