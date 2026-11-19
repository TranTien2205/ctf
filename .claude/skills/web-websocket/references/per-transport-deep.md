# Per transport (deep) — the check order per transport

## Raw WebSocket — `ws://`/`wss://`, no envelope

- the full handshake matrix (origin/binding/token/subproto)
- the `{"action":"x"}` shape directly
- the per-frame field set

## Socket.IO — the event envelope

- the `0`-open reply names the sid/upgrade
- `40-connect`/`40{"auth"}`/`40{"token"}` for auth
- `42["event",{...}]` for the dispatch — the event-name + the payload
- `41`/`43`/`44`/`45` — disconnect/ack/error/binary
- the `/<ns>` namespace + the `join`/`leave`/`room` membership
- the `EIO=3`/`EIO=4`/`transport=websocket`/`polling` URL params —
  the engine.io version + the transport

## SockJS — the HTTP multiplex

- `GET /info` first — `{"websocket":true,"origins":[...]}` — the origins
  array is itself an Origin-check read
- the `/<server>/<session>/<transport>` URL shape — a session-binding
- the `o`/`a[...]`/`h`/`c[...]` envelope
- the transport fallbacks — `websocket`/`xhr_streaming`/`xhr_polling`/
  `eventsource`/`htmlfile`/`iframe` — a fallback may bypass a ws-only
  check

## STOMP — the command protocol

- `Sec-WebSocket-Protocol: v10.stomp`/`v11.stomp`/`v12.stomp`
- `CONNECT` + `login:`/`passcode:`/`host:` — the auth
- `SEND destination:`/`SUBSCRIBE id: destination:`/`UNSUBSCRIBE`/
  `ACK`/`NACK`/`BEGIN`/`COMMIT`/`ABORT`/`DISCONNECT`
- the `destination:` route — `/topic/`/`/queue/`/`/app/`/`/user/`/
  `/exchange/` — the destination-IDOR

## `graphql-transport-ws`/`graphql-ws` — the subscription protocol

- `connection_init` + `payload:{authToken}` — the auth
- `subscribe`/`start` + `payload:{query}` — the GraphQL surface
- `next`/`data`/`error`/`complete`/`connection_ack`
- a `subscription`/`query`/`mutation` inside the frame — the whole
  `web-graphql` set over WS

## MQTT-over-WS — the binary pub/sub

- `Sec-WebSocket-Protocol: mqtt`/`mqttv3.1`/`mqttv5`
- `CONNECT` clientId/keepalive/username/password — the auth
- `SUBSCRIBE`/`PUBLISH`/`UNSUBSCRIBE`/`PINGREQ`/`DISCONNECT`
- the `topic` filter — `#`/`+`/a literal — the topic-IDOR/wildcard

## The binary/protobuf transport

- `proto_decode.py frame.bin` — the field-stream
- a `delimited`/length-prefixed stream → split the frames first
- a `field N` carrying the flag/secret — the numbered-field read
- a `varint`/`fixed64`/`fixed32`/`len`-delimited wire-type

## The per-transport record

`transport: <type>: <the auth>: <the envelope>: <the oracle cells>` —
the transport determines the send-shape; the envelope is a precondition
for every message-side check.

## The transport-switch check

The same app may speak raw-WS AND SockJS AND Socket.IO on different
endpoints — each transport is its own pass; a check enforced on one
transport may be absent on another (a transport-IDOR).
