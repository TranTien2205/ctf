# Recon order — the bounded intake, in order

## Step 1 — the front-end bundle (the schema source)

```bash
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle
# or the web-source-map skill — the .map recovery
```

The bundle carries the endpoint, the client library, the action set,
the field names, the auth mechanism — the real schema.

## Step 2 — the endpoint signals

```bash
grep -riE 'wss?://[^"'\'' ]*|new WebSocket|io\.connect|new SockJS|
Stomp\.over|stompClient|Pusher\(|Ably\.Realtime|createClient|
graphql-ws|graphql-transport-ws|mqtt' /tmp/bundle
```

Outputs: the ws endpoint(s), the client library, the framing.

## Step 3 — the schema signals

```bash
grep -riE '\.(send|emit|publish|call|invoke)\(|\.on\(|\.subscribe\(|ws\.send|socket\.emit' /tmp/bundle | head -30
grep -riE '"(action|type|event|cmd|method|op|id|room|channel|user_id|role|from|to|token|q|filter|file|path|url|data|subscribe|join|destination|topic)"' /tmp/bundle | head -40
```

Outputs: the action/field set — the dispatch key, the object fields,
the auth fields.

## Step 4 — the auth signals

```bash
grep -riE '(cookie|session|authorization|bearer|token|jwt|auth|api[-_]?key|sec-websocket-protocol|\?token=|\?auth=|\?key=)' /tmp/bundle | head -30
curl -sI "$BASE/login" | grep -i 'set-cookie'   # the SameSite read
```

Outputs: the handshake auth mechanism + the cookie's SameSite.

## Step 5 — the live-feature signals

```bash
curl -s "$BASE" | grep -iE 'chat|live|realtime|notification|presence|
comment|feed|dashboard|metric|doc|collab|lobby|game'
```

Outputs: a live-feature that names the socket — the channel's purpose.

## Step 6 — the first handshake capture

```bash
curl -i -N \
  -H 'Connection: Upgrade' -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' \
  -H 'Sec-WebSocket-Key: '$(head -c16 /dev/urandom|base64) \
  "$BASE/ws"
```

Outputs: the `101`/`401`/`403`, the `Sec-WebSocket-Accept`, the accepted
sub-protocol.

## The recon-order record

```
recon:
  endpoint: <the ws path(s)>
  library:  <raw|socket.io|sockjs|stomp|pusher|ably|graphql-ws>
  auth:     <cookie|token|bearer|none> + <samesite>
  schema:   <the action/field set>
  subproto: <the client-requested protocol>
```

The recon ends when the endpoint + the framing + the auth + the schema
are known — the detection-checklist's `cells` seed.

## The order-discipline

- the bundle FIRST — the schema is in the JS, not guessed
- the SameSite read — before any CSWSH claim
- the first handshake — the `101`/`401`/`403` baseline
- ~3-6 commands — the bounded recon; the cells decide the probes
