# Service recon: consul

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Consul: HTTP API on 8500 - /v1/agent/self (version,
config verbatim), /v1/catalog/services (service inventory =
internal surface map), /v1/kv/?recurse (key-value tree =
config+secret leak when unauthenticated). Each GET is one
cheap request.
## Pivot

Signal harvested -> out-*; route named -> that skill.
