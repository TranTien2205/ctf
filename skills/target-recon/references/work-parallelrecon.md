# Recon workflow: parallelrecon

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Parallel recon: independent reads can
overlap - JS fetch + robots + sitemap + openapi in one batch.
Writes never overlap on a shared instance. Batch the cheap
GETs; serialize anything that could trigger rate-limit or
WAF state.
## Pivot

Signal harvested -> out-*; route named -> that skill.
