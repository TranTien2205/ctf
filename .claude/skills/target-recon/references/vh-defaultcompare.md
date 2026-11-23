# Vhost/subdomain: defaultcompare

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Default-vhost comparison: request the IP
directly vs the hostname vs a nonsense name. Three response
bodies: IP-default, named-vhost, wildcard-vhost. Identical
IP/nonsense responses mean no wildcard = unknown names 404 at
the vhost layer; a wildcard = every name lands somewhere -
record which posture applies.
## Pivot

Signal harvested -> out-*; route named -> that skill.
