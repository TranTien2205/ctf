# Passive recon: certsan

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Read SANs off the live certificate itself:
openssl s_client -connect host:port -servername host -showcerts
| openssl x509 -text | grep Subject Alternative Name. Yields
sibling names, wildcard scope, internal FQDNs - the passive
inventory that needs no external service.
## Pivot

Signal harvested -> out-*; route named -> that skill.
