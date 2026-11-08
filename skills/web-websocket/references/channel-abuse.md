# WebSocket channel abuse

A WebSocket connection is a second application: its own handshake, its own
authorization model, its own message schema. HTTP-layer protections stop
applying the moment the protocol switches — that gap is the class.

## Handshake-side checks

The `Upgrade` request is still HTTP — check what it validates:

| Check | Probe |
|---|---|
| `Origin` enforced? | connect with `Origin: https://evil` — accepted = cross-site WS hijacking (CSWSH) |
| auth bound to the session? | connect with a victim's cookie via a page you control — does the socket inherit it? |
| token in the socket or the cookie? | if the URL carries `?token=`, the token leaks to logs/referers |

CSWSH is CSRF's realtime twin: a page on your origin opens a socket *with the
victim's cookies* and reads/writes as them.

## Message-side checks

After the upgrade, the server stops seeing HTTP — every per-request control
must be re-implemented per message. It usually is not:

```text
{"action":"read","id":"<own-object>"}
{"action":"read","id":"<other-object>"}     # IDOR per message
{"action":"admin", ...}                      # action dispatch without role check
{"action":"search","q":"<sqli/ssti payload>"}# injection in the message schema
```

The message schema is learned by reading the client bundle
(`../../web-source-map/SKILL.md`) or by diffing one observed frame against
mutations in each field.

## Fingerprinting the gap

1. Record the handshake request + the first frames on a normal session.
2. Mutate one field per connection — action, object id, role, payload.
3. Watch for a response the HTTP API would never have given: another user's
   object, an admin action, an error that leaks the schema.

## Falsifier

The handshake enforces `Origin`, every message re-checks auth and scope, and
mutated frames are rejected with a uniform error — the channel carries its
own authorization correctly.

## Traps

- A socket that accepts the connection and then silently drops unauthenticated
  frames is *not* an open channel — confirmation is a message that changed
  state or read another principal's data.
- Some stacks (Socket.IO, SockJS) wrap frames in their own envelope; send the
  envelope's shape, not bare JSON.
