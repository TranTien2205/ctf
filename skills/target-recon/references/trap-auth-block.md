# Trap: fuzzing behind auth

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Everything 302s to /login - find credentials
or a session first; unauthenticated fuzzing
measures nothing.

## Pivot

Signal harvested -> out-*; route named -> that skill.
