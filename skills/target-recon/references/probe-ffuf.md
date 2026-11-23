# Probe: ffuf

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

ffuf -u URL/FUZZ -w wordlist -fc 404 - the fast
path enumerator; calibrate the 404 baseline
first (a wildcard 200 means match on size).

## Pivot

Signal harvested -> out-*; route named -> that skill.
