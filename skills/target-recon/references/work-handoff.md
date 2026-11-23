# The handoff contract

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon's product is an observation list: stack, surface,
interesting endpoints, oddities. classify.py consumes
it; web-triage or the category router takes over.

## Pivot

Signal harvested -> out-*; route named -> that skill.
