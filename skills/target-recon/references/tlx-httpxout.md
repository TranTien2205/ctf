# Tool output parsing: httpxout

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

httpx (projectdiscovery) output -> observations:
title, status, content-length, webserver, tech-detect per
url - the tech list = stack signals; only the verified tech
hits are observations, detected-with-confidence vs guessed
separated.
## Pivot

Signal harvested -> out-*; route named -> that skill.
