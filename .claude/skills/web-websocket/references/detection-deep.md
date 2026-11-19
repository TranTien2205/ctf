# Detection (deep) — the full signal inventory and the protocol

## The recon-depth signals — the complete list

| Signal | Where | Confidence |
|---|---|---|
| `new WebSocket("wss?://...")` | the bundle | high |
| `io(`/`socket.io`/`io.connect` | the bundle | high |
| `SockJS(`/`new SockJS` | the bundle | high |
| `stomp`/`Stomp.over`/`stompClient` | the bundle | high |
| `pusher`/`Pusher(`/`ably`/`Ably.Realtime` | the bundle | high |
| `graphql-ws`/`graphql-transport-ws`/`createClient` | the bundle | high |
| `Upgrade: websocket`/`101`/`Sec-WebSocket-*` | traffic | high |
| `?token=`/`?jwt=`/`?auth=`/`?key=`/`?session=` on the ws URL | the bundle/URL | high |
| a live feature (chat/presence/feed/notification) | the UI | medium |
| `ws://` in a config/env/`process.env` | the bundle/source-map | medium |

## The handshake capture — the full header set

```bash
curl -i -N \
  -H 'Connection: Upgrade' -H 'Upgrade: websocket' \
  -H 'Sec-WebSocket-Version: 13' \
  -H 'Sec-WebSocket-Key: '$(head -c16 /dev/urandom | base64) \
  -H 'Sec-WebSocket-Protocol: <the-sub-protocol>' \
  -H 'Origin: https://evil.example' \
  -H 'Cookie: session=x' \
  "$BASE/ws"
```

Read: the `101`/`403`/`401`, the `Sec-WebSocket-Accept`, the accepted
`Sec-WebSocket-Protocol`, the `Set-Cookie`/`X-` on the reply.

## The schema-recovery protocol — order

1. the bundle's `ws.send`/`socket.emit`/`stompClient.send` — the exact
   first frames + the action set
2. the bundle's `ws.onmessage`/`socket.on`/`stompClient.subscribe` —
   the expected reply shapes + the event set
3. the `Sec-WebSocket-Protocol` the client requests — the sub-protocol
4. a real-session capture (devtools `WS`/`Frames` or a proxy) — the
   ground-truth frames

## The detection-verdict ladder

- **surface** — a `101`/a live feature/a `ws://` URL — the channel exists
- **candidate** — a foreign-`Origin` accepted / a `101`+no-auth / a
  `?token=` — a check to verify
- **oracle** — a frame the server sent that crosses a boundary — the
  victim-data read, the privileged action reply, the injection echo
- **negative** — a measured `403`/`forbidden`/`unknown`/`dropped`/`raw`

## The per-layer detection

- handshake-side — `handshake-side.md`/`cswsh.md` — Origin/binding/
  token/sub-protocol
- message-side — `message-side.md`/`message-idor.md`/`action-dispatch.md`
  — IDOR/action/spoof/injection
- the framing — `framing-protocols.md` — read the envelope first

## The detection record

`detect: <endpoint>:<layer>:<signal>` — each observed signal + its
confidence; the oracle-verdict needs the cross-boundary frame, not the
handshake.
