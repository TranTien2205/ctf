# Recon checklist: domain

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Domain checklist: pasv-* first (crt.sh SANs, DNS
records, PTR, whois freshness - zero requests to target)
-> cert SAN harvest on the live TLS -> HTTP+HTTPS intake ->
vhost candidates from names -> weburl checklist on the
primary name. Passive facts become wordlist seeds.
## Pivot

Signal harvested -> out-*; route named -> that skill.
