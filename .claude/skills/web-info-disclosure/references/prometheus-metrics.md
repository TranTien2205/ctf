# Prometheus /metrics mining

A /metrics endpoint is a topology map: service names, queue names, error counts, request rates — and occasionally a flag-leaking label.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /metrics with # HELP/# TYPE lines | prometheus | read all metric names |
| custom app metrics | internal names | service map |
| label values with secrets/paths | leaking labels | read directly |

## Steps

1. Fetch /metrics; read every metric name and label.
2. Custom app metrics name internal components, queues, endpoints.
3. Label values occasionally carry tokens, paths, user ids.
4. The metric names tell you what the app does internally — recon.

## Falsifier

Falsifier — no /metrics or it's stripped to standard runtime counters only: nothing extra disclosed.

## Traps

- Pushgateway/node_exporter paths also leak (/metrics on :9100 is out of scope).
- A /metrics with auth 403 is still a service boundary worth noting.

## Commands

```bash
curl -s '$BASE/metrics' | head -50
```

## Cross-references

`status-pages.md`
