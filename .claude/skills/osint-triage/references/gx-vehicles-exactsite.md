# Geo cell: vehicles -> exact-site

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

How far the `vehicles` feature narrows a geolocation to `exact-site`.

## Read

Narrows-to, hints, or no-power - the feature's discrimination
strength at this granularity. Combine cells: two hints at the
same level can reach a narrows-to together.
