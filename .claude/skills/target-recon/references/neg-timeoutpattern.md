# Recon negative: timeoutpattern

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Negative: uniform timeouts. Every probe
timing out identically = tarpit, rate-limit, or dead service -
not signal absence. Change nothing by volume; record
'uniform timeout' with sample RTTs and check the port's
liveness once.
## Pivot

Signal harvested -> out-*; route named -> that skill.
