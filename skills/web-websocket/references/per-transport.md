# Per-transport — raw WS, Socket.IO, SockJS, STOMP, MQTT, graphql-ws

## Raw WebSocket — `ws://`/`wss://`, no envelope

- probe: `{"action":"x","field":"y"}` bare JSON/text
- `ws_probe.py url --message '{"action":"x"}'` — the direct frame
- the simplest; the schema is the app's own JSON

## Socket.IO — the `42["event",data]` envelope

- handshake: `/socket.io/?EIO=4&transport=websocket`
- probe shape: `42["action",{"field":"y"}]` — the event + the data
- the `40{"token"}` connect carries the auth
- `0`/`2`/`3`/`40`/`41`/`42`/`43`/`44`/`45` prefix semantics
- `framing-protocols.md` — the envelope

## SockJS — the HTTP-multiplexed wrapper

- `GET /info` → the transport set; `/websocket`/`/xhr`/`/eventsource`
- the `a["..."]` data-array carries the JSON; `o`/`h`/`c` control
- probe the wrapped `a["{...}"]`, not bare

## STOMP — the command/destination protocol

- `CONNECT accept-version:1.2` → `SUBSCRIBE`/`SEND`/`MESSAGE`
- the `destination:` header routes — `/topic/x`/`/queue/x`/`/user/x`
- a `SUBSCRIBE destination:/user/<other>/` → a queue-IDOR
- a `SEND destination:/app/<admin>` → an action-gap

## MQTT-over-WS — the pub/sub binary

- `CONNECT`/`SUBSCRIBE`/`PUBLISH`/`SUBACK`/`PUBACK`
- `SUBSCRIBE #`/`+`/`/another` → a topic-IDOR
- `PUBLISH` to a restricted topic → a write-gap
- `willTopic`/`clientId` the client sets — a spoof/enum surface

## `graphql-ws`/`graphql-transport-ws` — subscriptions

- `Sec-WebSocket-Protocol: graphql-ws`
- `{"type":"connection_init","payload":{"authToken"}}` — the auth frame
- `{"type":"subscribe","payload":{"query":"subscription{...}"}}`
- a `subscription{user(id:N){...}}` → a subscription-IDOR + `web-graphql`
- a `query`/`mutation` over WS → the full `web-graphql` surface in a frame

## Binary/protobuf — `proto_decode`

- a binary frame → `proto_decode.py`; the flag in a numbered field
- a serialized object → `web-deserialization`
- a custom/binary format → hex-inspect for a magic/length/field structure

## The transport-to-protocol map

| Transport | The envelope | The probe shape |
|---|---|---|
| raw WS | none | `{"action":"x"}` |
| Socket.IO | `42["e",d]` | `42["action",{...}]` |
| SockJS | `a["..."]` | `a["{\"action\":\"x\"}"]` |
| STOMP | command+headers | `SEND destination:/app/x` |
| MQTT | binary | `SUBSCRIBE`/`PUBLISH` topic |
| graphql-ws | `{"type":...}` | `{"type":"subscribe",...}` |

The transport names the envelope — send the envelope's shape, not bare JSON.
