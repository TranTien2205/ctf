# Rate limit: detect

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Rate-limit detection: 429 responses, Retry-After
headers, X-RateLimit-Remaining counters, sudden 403 blocks
after N requests, response-time stair-stepping. Probe by
counting identical-request response changes - the first
sign names the limit. Record the limit shape verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
