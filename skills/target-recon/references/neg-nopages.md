# Recon negative: nopages

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Negative: no crawlable pages. A bare API or SPA
shell - the surface lives in JS/endpoints, not links. Record
'no pages' and pivot to bundle/API harvest rather than forcing
a crawler.
## Pivot

Signal harvested -> out-*; route named -> that skill.
