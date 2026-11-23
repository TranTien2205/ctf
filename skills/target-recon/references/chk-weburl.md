# Recon checklist: weburl

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

URL-target recon checklist: GET / (headers+cookies+
body) -> JS/bundle harvest -> robots/sitemap/well-known ->
stack playbook row -> openapi/graphql/doc probes -> forms+
params inventory -> method/content-type matrix -> git/env/
backup probes -> oddity list -> out-*. Each box needs a
verbatim record or a recorded negative.
## Pivot

Signal harvested -> out-*; route named -> that skill.
