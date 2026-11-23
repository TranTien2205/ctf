# Baseline calibration: errorbase

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Error baseline: a deliberately bad request
(huge path, bad method, bad version) - capture the error
shape verbatim. Per-endpoint error shapes are the parser
identity + debug posture oracle for every later probe.
## Pivot

Signal harvested -> out-*; route named -> that skill.
