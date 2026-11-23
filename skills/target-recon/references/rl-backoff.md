# Rate limit: backoff

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Backoff discipline: on 429/block, wait the
Retry-After value or step the rate down geometrically - never
hammer through a WAF (the whole enum dies, and a shared
instance suffers). A triggered limit is itself recorded as
an observation with its threshold.
## Pivot

Signal harvested -> out-*; route named -> that skill.
