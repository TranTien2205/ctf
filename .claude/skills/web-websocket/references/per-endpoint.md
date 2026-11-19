# Per-endpoint — every socket path's protocol

## `/ws` `/websocket` `/socket` `/realtime` `/stream` — the generic channel

- handshake: `Origin`/cookie/`?token=`/`Authorization`/sub-protocol
- first-frame: the `auth`/`subscribe`/`join`/`init` the client sends
- message-side: the action/field schema → IDOR/action/spoof/injection

## `/socket.io` `/socket.io/?EIO=4&transport=websocket` — Socket.IO

- the `0/1/2/3/4` envelope — `40` connect (the auth payload), `42`
  event (the real message), `43` ack
- probe the `42["event",data]` shape, not bare JSON
- `framing-protocols.md` — the envelope map

## `/sockjs` `/sockjs/info` `/sockjs/websocket` — SockJS

- `o`/`a[...]`/`h`/`c[...]` — the data array wraps the JSON
- a `/info` GET first — the transport set the server accepts

## `/graphql` `/graphql-ws` `graphql-transport-ws` — GraphQL-over-WS

- `Sec-WebSocket-Protocol: graphql-ws`/`graphql-transport-ws`
- `{"type":"connection_init","payload":{"authToken":...}}` — the auth
- `{"type":"subscribe","payload":{"query":"subscription{...}"}}` — the
  subscription; a `web-graphql` query inside the frame
- `subscription{user(id:N)}` → a subscription-IDOR + `web-graphql`

## `/stomp` `/ws/stomp` — STOMP

- `CONNECT`/`SUBSCRIBE`/`SEND`/`MESSAGE`/`DISCONNECT`
- `SUBSCRIBE destination:/user/<other>/queue` → a queue-IDOR
- `SEND destination:/app/<privileged>` → an action-gap

## MQTT-over-WS `/mqtt` `/ws/mqtt`

- `CONNECT`/`SUBSCRIBE`/`PUBLISH` binary frames
- `SUBSCRIBE #`/`+`/another's topic → a topic-IDOR
- `PUBLISH` to a restricted topic → a write-gap

## The admin/internal/debug channel

`/admin-ws` `/internal` `/debug` `/metrics-ws` `/console` — a privileged
channel the schema accepts; often an unauth or weakly-authed socket.

## The endpoint-verb boundary

The same logic under multiple paths — `/ws`, `/ws/`, `/api/ws`,
`/socket.io`, `/sockjs` — each a separate cell; a per-endpoint check or
authz may differ.

## The endpoint record

`endpoint: <path>: <handshake|message|framing>: <verdict>` — per socket
per layer per channel; the coverage matrix tracks each.
