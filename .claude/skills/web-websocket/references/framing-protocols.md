# Framing protocols — the envelopes, decoded

## Raw WebSocket — the bare JSON

```text
send:    {"action":"x"}
reply:   {"result":...} / {"data":...}
the shape: a bare text frame — the app's schema is the payload
```

## Socket.IO — the packet-type envelope

```text
0   open     -> the handshake reply {sid, upgrades, pingInterval}
2   ping     -> server->client; the client replies 3
3   pong
4   message  -> the app data
40  connect  -> {"token":...} / {"auth":...}
41  disconnect
42  event    -> ["event-name",{data}]   <- the real message
43  ack      -> [ackId,{data}]
44  error    -> {"message":"..."}
45  binary-event -> ["event",{data},<binary>]

the URL:     /socket.io/?EIO=3|4&transport=websocket|polling[&sid=<sid>]
the send:    42["x",{...}]
the ns:      /<ns> — /admin /internal — a namespace
```

## SockJS — the HTTP-multiplexed wrapper

```text
GET /info    -> {"websocket":true,"origins":["*:*"],...}   <- the origins
o            -> open
a["..."]     -> the data array — the inner JSON-string is the message
a["m1","m2"] -> a batch
h            -> heartbeat
c[code,"r"]  -> close
the URL:     /sockjs/<srv>/<sess>/<transport>
             the transports: websocket/xhr_streaming/xhr_polling/
                             eventsource/htmlfile/iframe
the send:    a["{\"action\":\"x\"}"]
```

## STOMP — the command protocol

```text
CONNECT
accept-version:1.2
host:/
login:<u>
passcode:<p>
<blank>
^@                       -> the CONNECT frame

SEND
destination:/app/x
<blank>
{"action":"x"}
^@                       -> send to /app/x

SUBSCRIBE
id:sub-0
destination:/user/<other>/queue
^@                       -> subscribe to another's queue

MESSAGE                   -> a pushed message
destination:/<x>
{...}

the destinations: /topic/ /queue/ /app/ /user/ /exchange/
the subproto:     Sec-WebSocket-Protocol: v10.stomp|v11.stomp|v12.stomp
```

## graphql-ws / graphql-transport-ws — the protocol

```json
{"type":"connection_init","payload":{"authToken":"<x>"}}   <- the auth
{"type":"subscribe","id":"1","payload":{"query":"subscription{...}"}}
{"type":"start","id":"1","payload":{"query":"subscription{...}"}}   (legacy)
{"type":"next","id":"1","payload":{"data":{...}}}          <- the data
{"type":"complete","id":"1"}
{"type":"connection_ack"}
{"type":"error","id":"1","payload":[...]}
the subproto: graphql-transport-ws / graphql-ws
the surface:  the whole web-graphql inside a frame
```

## MQTT-over-WS — the binary pub/sub

```text
CONNECT clientId/x keepalive [username] [password]
CONNACK
SUBSCRIBE {packetId, topics:[{topic:"x", qos:0}]}
SUBACK
PUBLISH {topic:"x", payload:...}
PUBACK
PINGREQ / DISCONNECT

the topics:  # (all) / + (one-level) / a literal / $SYS
the subproto: Sec-WebSocket-Protocol: mqtt / mqttv3.1 / mqttv5
```

## Binary/protobuf — the field-stream

```bash
python3 tools/proto_decode.py frame.bin
python3 tools/proto_decode.py --hex "0a0568656c6c6f"
```

A binary field-stream — `field N` keys + `varint`/`fixed64`/`fixed32`/
`len`-delimited wire-types; `proto_decode.py` walks them without a `.proto`.

## The envelope-before-payload rule — the discipline

```text
the framing is a PRECONDITION for the message-side cells.
a bare {"action":"x"} into a Socket.IO channel -> a framing error,
NOT a clean negative.
the send-shape:
  raw        -> {"action":"x"}
  socket.io  -> 42["x",{...}]
  sockjs     -> a["{\"action\":\"x\"}"]
  stomp      -> SEND destination:/app/x <blank> {..} ^@
  graphql-ws -> {"type":"subscribe",...}
  mqtt       -> SUBSCRIBE {topic} / PUBLISH {topic,payload}
  protobuf   -> a binary frame
```

## The framing-record

`framing: <endpoint>: <the transport>: <the send-shape>: <the auth-frame>`
— the framing decides the send-shape; the auth-frame decides the
credential placement.
