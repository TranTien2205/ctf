# Detection — how to know a WebSocket surface is present

## The endpoint signals

```bash
# the bundle
grep -riE 'wss?://|new WebSocket|io\.connect|new SockJS|Stomp\.over|
stompClient|Pusher\(|Ably\.Realtime|createClient|graphql-ws|mqtt\.connect' /tmp/bundle
# the traffic
the DevTools 'WS'/'Frames' tab / a proxy — an 'Upgrade: websocket' + '101'
```

A `new WebSocket`/`wss?://`/`socket.io`/`SockJS`/`stomp`/`pusher`/`ably`/
`graphql-ws`/`mqtt` is a high-confidence ws signal; a `live`/`realtime`/
`chat`/`presence`/`feed`/`collab`/`dashboard`/`lobby` UI word is a
medium-confidence lead.

## The handshake capture

```bash
curl -i -N \
  -H 'Connection: Upgrade' -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' \
  -H 'Sec-WebSocket-Key: '$(head -c16 /dev/urandom | base64) \
  "$BASE/ws"
```

Read: `101`/`401`/`403`/`400`/`426`; the `Sec-WebSocket-Accept`/
`Sec-WebSocket-Protocol`/`Sec-WebSocket-Extensions`/`Set-Cookie`/`X-`
on the reply.

## The first-frame check

```bash
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'
```

A `101` = the channel opened; the first reply — a `hello`/an auth-demand/
a data frame/a drop — reads the auth model.

## The schema signals — the field/action names

```bash
grep -riE '"(action|type|event|cmd|method|op|id|room|channel|user_id|
role|from|to|token|q|filter|file|url|data|subscribe|join|destination|topic)"' /tmp/bundle
```

The bundle's field names are the real schema — the dispatch key
(`action`/`type`/`event`/`cmd`), the object fields (`id`/`doc`/`room`/
`channel`/`user_id`), the auth fields (`token`/`auth`/`session_id`),
the sink fields (`q`/`filter`/`file`/`url`/`data`/`obj`).

## The auth-model signals

- `Cookie:`/`Authorization:`/`?token=` on the upgrade — the binding
- `{"type":"auth"}`/`40{"token"}`/`connection_init`/`CONNECT` — a
  first-frame auth
- `?token=`/`?jwt=`/`?key=`/`?auth=`/`?session=` on the URL — a
  credential-in-URL
- a `101` with no credentials — an unauth channel

## The detection-verdict ladder

- **surface** — the channel exists (a `101`, a live feature)
- **candidate** — a foreign-`Origin` accept, a no-auth `101`, a `?token=`
- **oracle** — a frame the server sent that crosses a boundary
- **uniform** — a measured rejection — a closed cell
- **weak-negative** — a guessed-name rejection — a re-probe
- **gap** — an unresponsive cell — not a verdict

## The detection record

`detect: <endpoint>: <the signal>: <the confidence>` — each signal +
its confidence; the oracle-verdict needs a cross-boundary reply.
