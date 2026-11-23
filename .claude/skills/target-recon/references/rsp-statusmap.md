# Response reading: statusmap

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Status-code taxonomy reading: 200 real vs 200
wildcard-shell (baseline diff decides), 301/302 (redirect
target = observation), 401/403 (gated - exists!), 404
(absent), 405 (exists, wrong method), 500 (debug posture),
503/429 (limit/CDN). Each status on each probe is a different
observation - a 403 is an endpoint found, not a dead end.
## Pivot

Signal harvested -> out-*; route named -> that skill.
