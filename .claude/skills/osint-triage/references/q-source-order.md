# Question: which source first

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

The pivot type names the first source - a photo
starts at exif, a handle at username search,
a domain at crt.sh.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
