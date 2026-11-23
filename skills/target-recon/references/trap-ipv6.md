# Recon trap: ipv6

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Trap: assuming IPv4. A target answering only on
[::1]:port or a dual-stack host can serve different vhosts
per family - if scope names a hostname, check AAAA exists
before declaring the target dead on A alone.
## Pivot

Signal harvested -> out-*; route named -> that skill.
