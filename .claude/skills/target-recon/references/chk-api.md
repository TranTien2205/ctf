# Recon checklist: api

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

API-only checklist: openapi/swagger/graphql doc hunt
(one fetch = whole map) -> options/method matrix on each
found route -> content-type acceptance -> auth scheme
inventory (401 WWW-Authenticate) -> version discovery
(/v1 vs /v2) -> id-shape per resource -> error-shape
reading -> out-*.
## Pivot

Signal harvested -> out-*; route named -> that skill.
