# Authenticated recon: multiaccount

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Multi-account comparison: two accounts give
the ID space (sequential? uuid?), per-account object counts,
and cross-account reference behavior in URLs. Account B
requesting account A's id = the controlled IDOR measurement -
recon records the id shape and the response DIFF, not a
verdict.
## Pivot

Signal harvested -> out-*; route named -> that skill.
