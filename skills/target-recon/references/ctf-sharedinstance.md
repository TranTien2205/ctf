# CTF-specific recon: sharedinstance

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Shared-instance etiquette: other solvers
hit the same target - keep request counts small, no aggressive
wordlists, no write-shaped probes during recon (a registration
is fine; a delete is not). A killed instance helps nobody;
recon on shared infra is always the cheap end of the matrix.
## Pivot

Signal harvested -> out-*; route named -> that skill.
