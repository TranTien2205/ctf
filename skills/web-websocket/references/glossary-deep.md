# Glossary (deep) — every term, defined for this class

## The protocol terms

- **WebSocket** — a full-duplex TCP-carried protocol; an HTTP-upgrade
  handshake then a bidirectional frame stream; `ws://`/`wss://`.
- **the upgrade** — the `GET` + `Upgrade: websocket` + `101` — the
  HTTP-to-WS transition.
- **`101 Switching Protocols`** — the upgrade-accepted reply — the
  channel exists; NOT a finding.
- **frame** — the WS transport unit: `fin`/`opcode`/`masked`/`len`/
  `mask-key`/`payload`. `opcode`: `0x0` continuation, `0x1` text, `0x2`
  binary, `0x8` close, `0x9` ping, `0xA` pong.
- **`Sec-WebSocket-Key`** — the client nonce; the server's `Accept` is
  `sha1(key + magic)` — a handshake-verification, not an auth.
- **`Sec-WebSocket-Protocol`** — the sub-protocol negotiation — `json`/
  `graphql-ws`/`stomp`/`mqtt`/etc.
- **`Sec-WebSocket-Extensions`** — the extensions — `permessage-deflate`
  (compression), etc.
- **`masked`** — the client->server frames are XOR-masked; the server's
  are not — a wire-format detail, not an auth.

## The auth terms

- **handshake auth** — the cookie/`Authorization`/`?token=` read at the
  `101` — the socket's identity.
- **first-frame auth** — a `{"type":"auth"}`/`connection_init`/`40{"token"}`/
  `CONNECT` — the auth moved into a frame.
- **binding** — the socket's identity is bound to the handshake's
  credential — a `Cookie: session` binding makes the socket "the user".
- **resume/session-binding** — a `session_id`/`resume`/`reconnect`/`seq`
  re-attaches a prior context.
- **token-in-URL** — `?token=`/`?jwt=`/`?key=` on the ws URL — a
  credential-in-URI leak.
- **per-message authz** — the `authorize(user, action, field)` inside the
  frame-dispatch — the check that is routinely missing.

## The gap terms

- **CSWSH** — Cross-Site WebSocket Hijacking: a foreign-origin page
  opens the socket as the victim (the cookie travels) and reads/writes
  the channel — the four-leg chain.
- **unauth channel** — a `101`+data with no credentials — the open socket.
- **message-IDOR** — a `{"action":"read","id":"<other>"}` returning
  another's object — the per-frame object gap.
- **membership/subscription-IDOR** — a `subscribe`/`join`/`watch`/`listen`
  to another's feed/room/channel/topic.
- **action-dispatch gap** — a privileged `action`/`type`/`event`/`cmd`
  handler reachable without a role check.
- **role-self-grant** — a `role`/`perm`/`is_admin`/`scope` field the
  frame binds.
- **identity-spoof** — a `from`/`user_id`/`sender`/`user` field the
  frame claims — the server trusts it.
- **injection-in-frame** — a `q`/`file`/`xml`/`data`/`url`/`obj` field
  reaching a sink.
- **write-side gap** — a `transfer`/`set`/`broadcast`/`delete`/`create`
  frame that changes state.
- **session-resumption gap** — a reconnect resuming a stale identity.
- **broadcast-blast** — a `broadcast`/`emit-all`/`send_all` reaching
  every connected socket.

## The transport terms

- **raw WS** — the bare `{"action":"x"}` JSON frame.
- **Socket.IO** — the `0`/`1`/`2`/`3`/`40`/`41`/`42`/`43`/`44`/`45`
  packet-types + `42["event",{...}]` + `/ns` namespaces + `EIO`/
  `transport`/`sid` URL params.
- **SockJS** — the `/info` + `/<srv>/<sess>/<transport>` + `o`/`a[...]`/
  `h`/`c[...]` envelope + the fallback transports.
- **STOMP** — the `CONNECT`/`SEND`/`SUBSCRIBE`/`MESSAGE`/`ACK`/`NACK`
  command frames + the `destination:` routes (`/topic//queue//app//
  /user//exchange/`).
- **graphql-ws**/`graphql-transport-ws` — `connection_init`/`subscribe`/
  `next`/`error`/`complete` — GraphQL over WS.
- **MQTT-over-WS** — `CONNECT`/`SUBSCRIBE`/`PUBLISH`/`SUBACK`/`PUBACK`
  + `#`/`+` topic wildcards — binary pub/sub.
- **protobuf** — a binary field-stream — `proto_decode.py` reads the
  field-keys + wire-types.
- **permessage-deflate** — the compression extension — a compressed
  frame a filter may not inspect.

## The evidence terms

- **oracle** — a frame the server sent that crosses a boundary — the
  proof.
- **uniform** — a measured rejection — a closed cell.
- **weak-negative** — a rejection of a GUESSED name — a re-probe, not a
  closed cell.
- **gap** — an unresponsive/dropped frame — not a verdict.
- **surface** — a `101`/`pong`/`ok`/`echo` — not a finding.
- **candidate** — a potential — a `500`/crash/a foreign-`Origin`-accept.
- **catalogue** — the class has no local solve — this corpus is standard
  guidance.

## The boundary terms

- **the principal boundary** — user-to-user — the IDOR.
- **the role boundary** — user-to-privileged — the dispatch/self-grant.
- **the identity boundary** — self-to-other — the spoof.
- **the sink boundary** — field-to-sink — the injection.
- **the channel boundary** — socket-scope — the membership/subscription.
