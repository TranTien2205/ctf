# Mobile recon: apiextract

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

API-shape extraction from mobile clients:
the request shapes the app emits (paths, headers like
X-Api-Key, signature schemes, cert pins) = the expected
request template; replaying the SHAPE (not the creds) is
recon - the api-* intake applies to the extracted base.
## Pivot

Signal harvested -> out-*; route named -> that skill.
