# Health and readiness endpoints — case catalogue

/health, /healthz, /ready, /live: orchestration endpoints that range from 'ok' to a full dependency map.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /health returns 'ok' only | minimal | little disclosure |
| 2 | /healthz with per-dependency status | dependency map | names internal services |
| 3 | /ready vs /live differences | k8s semantics | container hints |

## Falsifier

Falsifier — bare ok/404 across all health paths: nothing leaked.
