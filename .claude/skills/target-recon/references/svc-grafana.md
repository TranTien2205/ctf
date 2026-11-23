# Service recon: grafana

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Grafana: /login, X-Grafana-Org-Id headers,
/api/health = version verbatim, /api/datasources unauth
posture check, default admin/admin = documented check.
Dashboard panels leak datasource types = backend identity.
## Pivot

Signal harvested -> out-*; route named -> that skill.
