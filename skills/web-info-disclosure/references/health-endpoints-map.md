# Health and readiness endpoints — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /health returns 'ok' only | minimal | little disclosure |
| /healthz with per-dependency status | dependency map | names internal services |
| /ready vs /live differences | k8s semantics | container hints |

## Falsifier

Falsifier — bare ok/404 across all health paths: nothing leaked.
