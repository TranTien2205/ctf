# Edge cases — the cases that break the standard model

## The auth-in-first-frame socket

```text
101
<- {"auth": "send your token"}
-> {"type":"auth","token":"eyJ..."}
<- {"action":"me","data":...}
```

The socket opens unauth then demands a frame token — the `unauth` cell
is a `101`+auth-required, not a data channel. Probe the auth frame —
a forgeable/`null`/empty token is the gap.

## The socket that accepts but drops

```text
101
-> {"action":"x"}       -> (nothing)
-> {"action":"admin"}   -> (nothing)
```

A `101`+silent-drop — the upgrade succeeds, frames are ignored. Record
`gap` — the channel may process frames internally (a write-only socket)
— check the STATE it produced, not a reply.

## The broadcast-blast

```json
{"action":"broadcast","text":"x"} -> reaches EVERY connected socket
```

A `broadcast`/`announce`/`emit-all`/`send_all` reaches every socket —
a cross-client write; the flag may ride another victim's socket, or the
write itself is the finding.

## The reconnect/session-boundary gap

```text
socket-1 authed -> drops -> socket-2 reconnects
socket-2 resumes the LAST authed context? or a fresh one?
```

A session-resumption gap — a socket re-binds the old identity without
re-auth. Probe a reconnect with a different/no credential.

## The concurrent-socket race

```text
socket-A {"action":"transfer"}  |  socket-B {"action":"balance"}
```

Two sockets, one account — a `web-race-condition` on the socket's
per-connection state — the budget/serial check applies.

## The permessage-deflate/compression gap

A `Sec-WebSocket-Extensions: permessage-deflate` — a compressed frame
the content-filter never sees (it inspects uncompressed bytes) — an
evasion + a zlib-BREACH oracle.

## The `Upgrade` path variance

```text
GET /ws       -> 404
GET /api/ws   -> 101
GET /ws       with the right Host/path -> 101
GET /socket.io/?EIO=4&transport=websocket -> 0-open + frames
```

The endpoint path matters — `/ws`/`/api/ws`/`/socket.io/`/`/ws/socket.io`
— the bundle names the real path.

## The subscribe-only socket

```text
-> (the client never sends — only receives)
<- {"event":"update",...}
```

A subscribe-only channel — no action surface; the checks are the
subscription/membership (a channel-IDOR), not the actions.

## The unidirectional finding — the reply on another channel

```text
-> {"action":"x"}   -> (server processes it)
<- a notification on ANOTHER socket/HTTP-poll
```

The reply lands on a different channel — the frame's effect is visible
in a notification/HTTP-poll, not the WS reply.

## The `masked`/opcode mishandling

The client's frames are masked; the server's are not — a proxy/parser
that mishandles the mask/opcode — `web-parser-differential`-shaped.

## The fragment-split message

A `fin=0` continuation-frame split — a fragmented message the per-frame
validator only sees part of — an injection split across fragments.

## The transport-switch

The same app on `/ws` AND `/socket.io/` AND `/sockjs/` — a check on one
transport absent on another — a transport-IDOR/differential.

## The edge-record

`edge: <endpoint>: <the deviation> -> <the verdict>` — each named case
recorded; a nonstandard socket is NOT `uniform`-safe — it is unmeasured.
