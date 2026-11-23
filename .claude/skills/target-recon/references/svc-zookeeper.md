# Service recon: zookeeper

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Zookeeper 2181: four-letter words - 'stat'
(connection state), 'srvr' (server stats), 'envi' (environment
= version, hostname, paths), 'mntr'. A four-letter word
returning stats unauthenticated = the observation; ruok ->
imok is the liveness probe.
## Pivot

Signal harvested -> out-*; route named -> that skill.
