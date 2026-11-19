# Realtime and GraphQL endpoint discovery — checklist

ws:// endpoints, /graphql, /api/v*/ subscriptions: the non-HTTP-REST surface that's easy to miss in a bounded sweep.

## Checklist

- [ ] POST {query:{__typename}} to /graphql-like paths.
- [ ] Check for Upgrade responses on /ws /socket.io/ /realtime.
- [ ] These classes have their own skills — disclosure's job is naming them.

## Abort conditions

- GraphQL endpoints often sit behind /api/graphql, /v1/graphql — check spec/docs first.
- Socket.io answers on /socket.io/?EIO=... — a transport probe.

## Falsifier

Falsifier — no realtime or GraphQL surface: stick to the HTTP inventory.
