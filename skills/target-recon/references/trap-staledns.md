# Recon trap: staledns

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Trap: stale DNS or a moved target. The name
resolves but the port is silent because the instance moved -
check the supplied target against resolution time, try the
IP directly, and record 'resolves-but-silent' as its own
observation rather than hammering.
## Pivot

Signal harvested -> out-*; route named -> that skill.
