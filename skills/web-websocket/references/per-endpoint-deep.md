# Per endpoint (deep) — the check order per endpoint shape

## `/ws`/`/socket`/`/realtime` — the raw WebSocket

```text
1. handshake: origin/binding/token/subproto
2. framing:   raw — send the bundle's {"action"} shape
3. message:   idor/action/spoof/inject
```

## `/socket.io/` — Socket.IO

```text
1. handshake: origin/binding/?auth=/?token=
2. the 0-open frame -> the sid/pingInterval/upgrade
3. framing:   40-connect / 42-event / namespace
4. message:   42["event",{...}] — the event-name is the dispatch;
             /admin namespace / join-room / the event payload's fields
```

## `/sockjs/` — SockJS

```text
1. GET /info -> {"websocket":true,"origins":["*:*"]}   <- the origins
2. handshake -> the /info origins + the websocket transport
3. framing:   a["..."] — the array + the inner string
4. message:   the inner JSON's action/fields
```

## `/stomp`/`/websocket`+STOMP — STOMP

```text
1. Sec-WebSocket-Protocol: v12.stomp / v11.stomp
2. CONNECT frame -> the login/passcode auth
3. message:   SEND destination:/app/x ; SUBSCRIBE destination:/user/<x>
4. the /topic//queue//user/ destination-IDOR
```

## `/graphql`/`/subscriptions` — graphql-ws

```text
1. Sec-WebSocket-Protocol: graphql-transport-ws / graphql-ws
2. connection_init -> the authToken
3. message:   subscribe/start -> a GraphQL subscription/query
4. the field-level authz on the subscription -> web-graphql
```

## `/mqtt` — MQTT-over-WS

```text
1. Sec-WebSocket-Protocol: mqtt / mqttv3.1
2. CONNECT clientId/keepalive
3. message:   SUBSCRIBE {#,+,/another/topic} ; PUBLISH {topic,payload}
4. the topic-IDOR / the wildcard-read
```

## `/api/ws`/`/v1/ws` — the API-namespaced socket

```text
1. the API version in the path -> a versioned auth
2. the same handshake/message cells
3. a ?version=/?api= — a versioned surface
```

## The endpoint-record

`endpoint: <path>: <framing>: <auth>: <the oracle cells>` — each
endpoint's framing + auth + the cells it answered; the coverage matrix
is per-endpoint.

## The per-endpoint boundary

- a `/socket.io/` and a `/ws` on the same host are TWO endpoints — each
  gets its own handshake/message pass
- a `/ws` that proxies to an internal socket — the proxy's headers
  (`X-Forwarded-*`) — `web-parser-differential`/`web-host-header`
- a `/ws` that 404s is not a ws endpoint — the bundle names the real path
