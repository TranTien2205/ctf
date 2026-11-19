# Realtime and GraphQL endpoint discovery — deep

ws:// endpoints, /graphql, /api/v*/ subscriptions: the non-HTTP-REST surface that's easy to miss in a bounded sweep.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no realtime or GraphQL surface: stick to the HTTP inventory.

## Highest-cost traps

- GraphQL endpoints often sit behind /api/graphql, /v1/graphql — check spec/docs first.
- Socket.io answers on /socket.io/?EIO=... — a transport probe.

## Commands

```bash
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"{__typename}"}' '$BASE/graphql'
```

## Cross-references

`api-docs-exposure.md`
