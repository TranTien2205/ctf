# Redirect recon: chainmap

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Redirect-chain mapping: follow each 3xx within
the same host/port - record the hop list verbatim (each
Location + status). Chains reveal flow boundaries: http->https,
host->www, root->login->app. A chain exiting the supplied
host is a scope note, not a follow.
## Pivot

Signal harvested -> out-*; route named -> that skill.
