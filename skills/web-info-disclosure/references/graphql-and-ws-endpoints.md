# Realtime and GraphQL endpoint discovery

ws:// endpoints, /graphql, /api/v*/ subscriptions: the non-HTTP-REST surface that's easy to miss in a bounded sweep.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /graphql responds to a POST | GraphQL present | web-graphql |
| Upgrade: websocket on a path | WS surface | web-websocket |
| /socket.io/ or /ws/ paths | realtime API | web-websocket |

## Steps

1. POST {query:{__typename}} to /graphql-like paths.
2. Check for Upgrade responses on /ws /socket.io/ /realtime.
3. These classes have their own skills — disclosure's job is naming them.

## Falsifier

Falsifier — no realtime or GraphQL surface: stick to the HTTP inventory.

## Traps

- GraphQL endpoints often sit behind /api/graphql, /v1/graphql — check spec/docs first.
- Socket.io answers on /socket.io/?EIO=... — a transport probe.

## Commands

```bash
curl -s -X POST -H 'Content-Type: application/json' -d '{"query":"{__typename}"}' '$BASE/graphql'
```

## Cross-references

`api-docs-exposure.md`
