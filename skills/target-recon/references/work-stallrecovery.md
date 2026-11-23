# Recon workflow: stallrecovery

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Stall recovery: when the intake produces
nothing new three steps running - stop scanning, re-read what
was harvested (the missed endpoint is usually in the JS or a
header), run classify.py on the partial list (a weak signal
is still a route), and only then widen enumeration one level.
## Pivot

Signal harvested -> out-*; route named -> that skill.
