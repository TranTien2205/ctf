# API recon: verdisc

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

API version discovery: /v1 /v2 /api/v1 path prefixes,
Accept-Version / X-API-Version headers, ?version= or ?v= query.
Old versions keep old bugs: if /api/v2/ exists, probe /api/v1/
once - deprecated authz or validation is a classic CTF route.
Record every version that answers with its status verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
