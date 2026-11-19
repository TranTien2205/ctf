# Realtime and GraphQL endpoint discovery — case catalogue

ws:// endpoints, /graphql, /api/v*/ subscriptions: the non-HTTP-REST surface that's easy to miss in a bounded sweep.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /graphql responds to a POST | GraphQL present | web-graphql |
| 2 | Upgrade: websocket on a path | WS surface | web-websocket |
| 3 | /socket.io/ or /ws/ paths | realtime API | web-websocket |

## Falsifier

Falsifier — no realtime or GraphQL surface: stick to the HTTP inventory.
