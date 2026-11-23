# Rate limit: budgetpartition

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Budget partition under limits: with a
detected rate cap, order enumeration by information-per-request
- page+JS harvest first (one request, many signals), doc
endpoints next (one request, full map), path-probe last
(many requests, few signals). The enum plan IS the budget.
## Pivot

Signal harvested -> out-*; route named -> that skill.
