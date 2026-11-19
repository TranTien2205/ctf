# Prometheus /metrics mining — deep

A /metrics endpoint is a topology map: service names, queue names, error counts, request rates — and occasionally a flag-leaking label.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no /metrics or it's stripped to standard runtime counters only: nothing extra disclosed.

## Highest-cost traps

- Pushgateway/node_exporter paths also leak (/metrics on :9100 is out of scope).
- A /metrics with auth 403 is still a service boundary worth noting.

## Commands

```bash
curl -s '$BASE/metrics' | head -50
```

## Cross-references

`status-pages.md`
