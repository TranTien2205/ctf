# Param-level recon: casecheck

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Case-sensitivity check: Admin vs admin on param
names and values - case-insensitive matching = normalization
gap candidates (authz bypass by case, WAF evasion notes).
Recorded per param where it matters (usernames, roles,
filters).
## Pivot

Signal harvested -> out-*; route named -> that skill.
