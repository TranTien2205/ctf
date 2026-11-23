# Response reading: headeranom

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Header-anomaly reading: missing headers
the stack normally sets (stripped = hardened/custom),
extra headers the stack never sets (X-Debug, custom X-*),
order anomalies (proxy injections). A header that varies
per request (X-Request-Id, cf-ray) marks edge presence.
## Pivot

Signal harvested -> out-*; route named -> that skill.
