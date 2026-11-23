# Service recon: prometheus

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Prometheus server 9090: /graph UI,
/api/v1/status/runtimeinfo = version+config, /api/v1/targets
= scrape target inventory = internal service map free,
/metrics about itself.
## Pivot

Signal harvested -> out-*; route named -> that skill.
