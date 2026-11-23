# Wordlist selection: bysize

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Wordlist sizing: directory-list-2.3-small (~87k)
is already too big for recon - start with common.txt (~4.7k)
or raft-small (~6k). The question is the budget: each word
is one request against a possibly-shared instance. Bigger
lists are a decide.py-gated escalation, not a recon move.
## Pivot

Signal harvested -> out-*; route named -> that skill.
