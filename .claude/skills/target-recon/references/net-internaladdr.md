# Network recon: internaladdr

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Internal-address leakage: RFC1918/link-local
addresses in JS configs (api_base: http://10.x/...), HTML
comments, error traces, redirect Locations, response bodies.
Each leaked internal name/IP = naming-convention + topology
signal and a potential ssrf target list for later stages.
## Pivot

Signal harvested -> out-*; route named -> that skill.
