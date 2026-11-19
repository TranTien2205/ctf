# Glossary — the terms, one line each

## The protocol

- **WebSocket** — an HTTP-upgrade + a bidirectional frame stream; `ws://`/`wss://`
- **the upgrade** — `GET` + `Upgrade:websocket` + `101` — the handshake
- **frame** — the transport unit: `fin`/`opcode`/`masked`/`len`/`payload`
- **opcode** — `0x0` cont / `0x1` text / `0x2` binary / `0x8` close /
  `0x9` ping / `0xA` pong
- **`Sec-WebSocket-*`** — the handshake headers — `Key`/`Accept`/
  `Version`/`Protocol`/`Extensions`
- **envelope** — the transport's wrapper — `42[...]`/`a[...]`/STOMP/etc.

## The auth

- **handshake auth** — the Cookie/`Authorization`/`?token=` at the `101`
- **first-frame auth** — `{"type":"auth"}`/`40{"token"}`/`connection_init`/`CONNECT`
- **binding** — the socket's identity = the handshake's credential
- **resume** — a `session_id`/`reconnect`/`seq`/`lastEventId` re-attach
- **token-in-URL** — a `?token=`/`?jwt=`/`?key=` credential-in-URI
- **per-message authz** — the `authorize(user, action, fields)` in the
  frame-dispatch — the missing check

## The gaps

- **CSWSH** — Cross-Site WebSocket Hijacking — the four-leg chain
- **unauth channel** — a `101`+data, no credentials
- **message-IDOR** — a `{"action":"read","id":"<other>"}` cross-principal read
- **membership-IDOR** — a `join`/`subscribe`/`watch`/`listen`/`follow`
- **action-dispatch gap** — a privileged `action`/`type`/`event`/`cmd`
- **role-self-grant** — a `role`/`perm`/`is_admin`/`scope` bound
- **identity-spoof** — a `from`/`user_id`/`sender`/`user` trusted
- **injection-in-frame** — a `q`/`file`/`url`/`xml`/`data`/`obj` to a sink
- **write-side gap** — a `transfer`/`set`/`broadcast`/`delete`/`create`
- **subscription-IDOR** — another's feed/topic/queue
- **resumption gap** — a `session_id`/`resume`/`reconnect`/`seq`
- **broadcast-blast** — a `broadcast`/`emit-all`/`send_all`
- **namespace-membership** — a `/<ns>`/`room`/`channel`/`topic`

## The transports

- **raw WS** — the bare `{"action":"x"}`
- **Socket.IO** — `0`/`40`/`41`/`42`/`43`/`44`/`45` packets + `/ns` +
  `EIO`/`transport`/`sid`
- **SockJS** — `/info` + `o`/`a[...]`/`h`/`c[...]` + fallbacks
- **STOMP** — `CONNECT`/`SEND`/`SUBSCRIBE`/`MESSAGE` + `destination:`
- **graphql-ws** — `connection_init`/`subscribe`/`next`/`error`/`complete`
- **MQTT** — `CONNECT`/`SUBSCRIBE`/`PUBLISH` + `#`/`+` topics
- **protobuf** — a binary field-stream — `proto_decode`
- **permessage-deflate** — the compression extension

## The evidence

- **oracle** — a boundary-crossing reply — the proof
- **uniform** — a measured rejection — a closed cell
- **weak-negative** — a guessed-name rejection — a re-probe
- **gap** — an unresponsive cell — not a verdict
- **surface** — a `101`/`pong`/`ok` — not a finding
- **candidate** — a potential — a `500`/crash/a foreign-`Origin`-accept
- **catalogue** — the class has no local solve

## The boundaries

- **principal** — user-to-user (the IDOR)
- **role** — user-to-privileged (the dispatch/self-grant)
- **identity** — self-to-other (the spoof)
- **sink** — field-to-sink (the injection)
- **channel** — socket-scope (the membership/subscription)
