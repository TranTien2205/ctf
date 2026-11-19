# Realtime and GraphQL endpoint discovery — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /graphql responds to a POST | GraphQL present | web-graphql |
| Upgrade: websocket on a path | WS surface | web-websocket |
| /socket.io/ or /ws/ paths | realtime API | web-websocket |

## Falsifier

Falsifier — no realtime or GraphQL surface: stick to the HTTP inventory.
