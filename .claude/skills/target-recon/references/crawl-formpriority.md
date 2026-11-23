# Crawl strategy: formpriority

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Form harvest priority: auth forms first
(endpoint + field names = login surface), then search/upload/
filter forms (injection surfaces), then newsletter-style
dead-ends. Each form = action+method+inputs recorded - the
author's own param inventory.
## Pivot

Signal harvested -> out-*; route named -> that skill.
