# Service recon: memcached

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

memcached: text protocol - 'version' returns
VERSION x.y; 'stats' returns counters + limits; 'stats items'
lists slabs = data inventory. Unauthenticated text answers =
the observation. A flush_all or set would be write-shaped -
recon stops at version/stats.
## Pivot

Signal harvested -> out-*; route named -> that skill.
