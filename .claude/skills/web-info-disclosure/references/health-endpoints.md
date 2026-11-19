# Health and readiness endpoints

/health, /healthz, /ready, /live: orchestration endpoints that range from 'ok' to a full dependency map.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /health returns 'ok' only | minimal | little disclosure |
| /healthz with per-dependency status | dependency map | names internal services |
| /ready vs /live differences | k8s semantics | container hints |

## Steps

1. Probe /health /healthz /ready /live /startup.
2. A detailed health response names databases, queues, upstreams — the topology.
3. Failed dependency statuses name what's down and where it lives.
4. Minimal 'ok' answers close this channel fast.

## Falsifier

Falsifier — bare ok/404 across all health paths: nothing leaked.

## Traps

- Detail level varies wildly — read the whole body once.
- k8s-style /healthz often includes component-level detail.
- A health endpoint that checks the DB gives a reachability oracle.

## Commands

```bash
for p in /health /healthz /ready /live; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`status-pages.md` · `debug-endpoints.md`
