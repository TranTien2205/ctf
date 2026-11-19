# Framing protocols (deep) — the envelopes, completely decoded

## Raw WebSocket — the no-envelope baseline

A bare text frame `{"action":"x"}` or a binary frame. The WS protocol
itself carries: `opcode` (text=1/binary=2/close=8/ping=9/pong=10),
`fin`, `masked`, `payload-len`. The app's schema is the payload.

## Socket.IO — the packet-type envelope, fully

```text
0  open     -> the handshake reply {sid, upgrades, pingInterval}
1  close
2  ping     -> server->client ; the client replies 3
3  pong
4  message  -> the app data
40 connect  -> {"token":...} the auth payload
41 disconnect
42 event    -> ["event-name",{data}]   <- the real message
43 ack      -> [ackId,{data}]
44 error    -> {"message":"..."}
45 binary-event -> ["event",{data},<binary>]
```

The `42["event",{...}]` is the dispatch — the event NAME is the action.
Probe: `42["admin",{}]`, `42["read",{"id":"x"}]`, `42["subscribe",
{"channel":"x"}]`. The `40{"token"}`/`40{"auth"}` connect carries the auth.

## Socket.IO namespace/room

```text
40/admin                            -> connect to the /admin namespace
42/admin,["event",{...}]             -> an event in /admin
42["join",{"room":"secret"}]         -> join a room
```

A `/admin`/`/internal` namespace or a `secret`-room — a namespace/room
membership IDOR.

## SockJS — the HTTP-multiplexed wrapper, fully

```text
GET /info                  -> {"websocket":true,"origins":["*:*"],...}
o                          -> open
a["{\"type\":\"x\"}"]      -> the data array carries the JSON-string
a["msg1","msg2"]           -> a batch
h                          -> heartbeat
c[code,"reason"]           -> close
```

The `a["..."]` array wraps a JSON-STRING — the inner string is the app
message. Probe `a["{\"action\":\"x\"}"]`.

## STOMP — the frame protocol, fully

```text
CONNECT
accept-version:1.2
host:/
login:user
passcode:pw
<blank>
^@                        -> the CONNECT frame (headers + blank + NUL)

CONNECTED                 -> the reply
version:1.2

SUBSCRIBE                 -> subscribe to a destination
id:sub-0
destination:/topic/x

SEND                      -> send to a destination
destination:/app/x
content-type:application/json
{"action":"x"}
^@

MESSAGE                   -> a pushed message
destination:/topic/x
{...}
```

The `destination:` header routes — `/topic/`/`/queue/`/`/app/`/`/user/`/
`/exchange/`. A `SUBSCRIBE destination:/user/<other>/queue` → a queue-
IDOR; `SEND destination:/app/admin` → an action-gap.

## `graphql-transport-ws` / `graphql-ws` — the protocol

```json
{"type":"connection_init","payload":{"authToken":"..."}}   -> the auth
{"type":"subscribe","id":"1","payload":{"query":"subscription{...}"}}
{"type":"start","id":"1","payload":{"query":"subscription{...}"}}   (legacy)
{"type":"next","id":"1","payload":{"data":{...}}}          -> the data
{"type":"complete","id":"1"}
{"type":"connection_ack"}
{"type":"error","id":"1","payload":[...]}
```

The `connection_init` carries the auth; `subscribe`/`start` carries the
GraphQL query — the whole `web-graphql` surface inside a frame.

## MQTT-over-WS — the binary pub/sub

```text
CONNECT clientId/x keepalive
CONNACK
SUBSCRIBE {packetId, topics:[{topic:"x", qos:0}]}   -> a topic-IDOR
SUBACK
PUBLISH {topic:"x", payload:...}                    -> a write-gap
PUBACK
```

`SUBSCRIBE` to `#`/`+`/`/another/topic` — the wildcard/`#` reads every
topic. `PUBLISH` to a restricted topic. Binary MQTT framing.

## Binary/protobuf — `proto_decode.py`

```bash
python3 tools/proto_decode.py frame.bin
python3 tools/proto_decode.py --hex "0a 05 68 65 6c 6c 6f"
```

Walks field keys + wire-types without the `.proto` — a `field N` holding
the flag/secret. A `delimited`/length-prefixed stream → split first.

## The envelope-vs-payload rule

The envelope is the transport's; the payload is the app's. A `42["x",
{...}]` the Socket.IO parser accepts but the inner-`x`-validator never
reaches — the ENVELOPE is parsed first; the payload's injection is the
app's. Read the envelope shape; then the payload.
