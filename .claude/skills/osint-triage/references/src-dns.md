# Source: DNS/certificates

Routing module for `osint-triage`. Pivot -> source -> verify ->
next pivot. The router names one unique pivot and one source at a
time; `../ctf-osint/` owns the depth per source family.

crt.sh certificate transparency, passive DNS,
WHOIS/RDAP - the domain family's core sources.

## Pivot

Pivot extracted -> src-*; result verified -> next piv-*.
