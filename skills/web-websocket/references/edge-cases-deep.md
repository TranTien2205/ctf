# Edge cases (deep) — the cases that break the standard model

## The auth-in-first-frame socket

```text
101
<- {"auth": "send your token"}
-> {"type":"auth","token":"eyJ..."}
<- {"action":"me","data":...}
```

The socket opens unauth then demands a frame token — the `unauth` cell
is a `101`+auth-required, not a data channel. Probe the auth frame; a
forgeable/`null` token is the gap.

## The socket that accepts but silently drops

```text
101
-> {"action":"x"}       -> (nothing)
-> {"action":"admin"}   -> (nothing)
```

A `101`+silent-drop — the upgrade succeeds, frames are ignored. Record
`gap`; the channel may process internally (a write-only socket) — check
the STATE it produced, not a reply.

## The broadcast-blast finding

```json
{"action":"broadcast","text":"x"} -> goes to EVERY connected socket
```

A `broadcast`/`announce`/`emit-all` action reaches every socket — a
cross-client write; the flag may ride on another victim's socket.

## The reconnect/session-boundary gap

```text
socket-1 authed -> socket-1 drops -> socket-2 reconnects
socket-2 resumes with the LAST authed context? or a fresh context?
```

A session-resumption gap — a socket that re-binds the old identity
without re-auth. Probe a reconnect with a different/no credential.

## The concurrent-socket race

```text
socket-A {"action":"transfer"}  |  socket-B {"action":"balance"}
```

Two sockets, one account — a `web-race-condition` on the socket's
per-connection state. The budget/serial check applies.

## The permessage-deflate/compression gap

A `Sec-WebSocket-Extensions: permessage-deflate` — a compressed frame
the content-filter never sees (it inspects uncompressed bytes). The
compression is itself an evasion + a zlib-BREACH oracle.

## The `Upgrade` that needs an HTTP-hop

```text
GET /ws  -> 404
GET /api/ws -> 101
GET /ws  with the right Host/path/Upgrade -> 101
```

The endpoint path matters — `/ws` vs `/api/ws` vs `/socket.io/` vs
`/ws/socket.io` — the bundle names the real path.

## The one-way socket (subscribe-only)

```text
-> (the client never sends — only receives)
<- {"event":"update",...}
```

A subscribe-only channel — no action surface; the checks are the
subscription/membership (a channel-IDOR), not the actions.

## The unidirectional finding — a frame the client never sees

```text
-> {"action":"x"}   -> (server processes it)
<- a notification on ANOTHER socket/HTTP
```

The reply lands on a different channel — the frame's effect is visible
in a notification/HTTP poll, not the WS reply.

## The `masked`-bit/server-sent-frames edge

The client's frames are masked; the server's are not — a proxy/parser
that mishandles the mask/opcode — `web-parser-differential`-shaped.

## The multi-frame/fragmented message

A `fin=0` continuation-frame split — a fragmented message the per-frame
validator only sees part of — an injection split across fragments.

## The edge-case record

`edge: <endpoint>: <the deviation> -> <the verdict>` — each named case
recorded; a nonstandard socket is NOT `uniform`-safe — it is unmeasured.
