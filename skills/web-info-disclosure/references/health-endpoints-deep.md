# Health and readiness endpoints — deep

/health, /healthz, /ready, /live: orchestration endpoints that range from 'ok' to a full dependency map.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — bare ok/404 across all health paths: nothing leaked.

## Highest-cost traps

- Detail level varies wildly — read the whole body once.
- k8s-style /healthz often includes component-level detail.
- A health endpoint that checks the DB gives a reachability oracle.

## Commands

```bash
for p in /health /healthz /ready /live; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`status-pages.md` · `debug-endpoints.md`
