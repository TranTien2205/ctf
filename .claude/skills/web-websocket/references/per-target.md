# Per target — each target shape, the ordered pass

## The SPA + realtime feature target

```text
the shape:  a React/Vue/Next SPA + a live feature (chat/feed/doc)
the order:  1. bundle_miner the JS -> the ws endpoint + the client lib
            2. the schema grep -> the action/field set
            3. the handshake cells -> origin/binding/token/subproto
            4. the message cells -> idor/action/spoof/inject
the trap:   the SPA's frontend JS carries the whole schema — grep it
            BEFORE any payload
```

## The bare socket target (no web UI)

```text
the shape:  a wss://x/ws endpoint, no HTML/bundle — a socket-only service
the order:  1. the handshake cells (the ONLY surface)
            2. the sub-protocol matrix — graphql-ws/stomp/mqtt/json
            3. a first-frame auth shape — {"type":"auth"}/40/CONNECT
            4. the message cells — the action/field set is GUESSED
               (no bundle) — probe the standard names + the doc hints
the trap:   no bundle -> the schema is guessed -> weak-negatives are
            LOUDER — a 'unknown action' is expected, not a defense
```

## The API + socket target

```text
the shape:  a REST/GraphQL API + a wss://x/ws channel
the order:  1. the API's object vocabulary -> the ws's id-space names
            2. the handshake cells
            3. the message cells — the idor/action reuse the API's names
the trap:   the HTTP API's authz is measured first — the WS twin is the
            UNENFORCED twin; the 403 on HTTP does NOT close the ws cell
```

## The graphql target

```text
the shape:  a /graphql + a /subscriptions (graphql-transport-ws)
the order:  1. the HTTP graphql introspection -> the schema
            2. the graphql-ws channel -> connection_init + subscribe
            3. a subscription-IDOR + a field-leak + a mutation-in-frame
the trap:   the channel is a graphql-ws — the QUERY is the payload; the
            whole web-graphql surface fits inside a frame
```

## The chat/collab target

```text
the shape:  a Socket.IO/SockJS chat or collab-edit app
the order:  1. the client lib -> the envelope (42[...]/a[...])
            2. the handshake cells
            3. the room/doc/history IDORs + the broadcast + the spoof
            4. the namespace/room membership
the trap:   the envelope — a bare {"action"} fails; send 42["x",{...}]
            or a["{...}"]
```

## The binary/IoT target

```text
the shape:  a binary ws feed / MQTT-over-WS / a protobuf socket
the order:  1. proto_decode.py the frames -> the field-stream
            2. the handshake cells (the binary auth may be a CONNECT)
            3. the SUBSCRIBE/topic/membership cells
            4. a field-mutation -> a numbered-field IDOR
the trap:   the frames are binary — proto_decode, not text-parsing
```

## The multi-transport target

```text
the shape:  a /ws AND a /socket.io/ AND a /sockjs/ on one host
the order:  1. each endpoint -> its own handshake+message pass
            2. a transport-switch differential — a check on one
               transport absent on another
the trap:   a 'uniform' on /ws does NOT close /socket.io — the cells
            are PER-ENDPOINT
```

## The per-target record

`target: <the shape>: <the ordered pass>: <the traps>` — the shape
names the order + the trap; the trap is the failure mode the shape
produces.
