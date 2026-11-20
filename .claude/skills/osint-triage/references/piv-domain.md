# Pivot: domain/host

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

A domain pivots through DNS, certificates, WHOIS,
and passive DNS history.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
