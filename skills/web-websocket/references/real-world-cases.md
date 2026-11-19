# Real-world cases — the published bug history

## The canonical weakness

WebSocket security is a named OWASP-adjacent class — the
`Hacker101`/`PortSwigger`/`OWASP Web Security Testing Guide` cover
CSWSH + message-authz. CWE-346 (`Origin Validation Error`), CWE-441
(`Unintended Proxy/Intermediary` — the socket bypasses HTTP checks),
CWE-306 (`Missing Authentication`).

## The CSWSH precedents

- **the Slack/GitLab/bug-bounty CSWSH reports** — a live notifications/
  collab socket accepting a foreign `Origin` + cookie-binding → read
  the victim's DMs/notifications — the canonical CSWSH bounty shape
- **the `SameSite` caveat reports** — a `SameSite=Strict` cookie
  killing an otherwise-open CSWSH — the modern-browser defense that
  changed the exploitability
- **the `Origin: null`/`file:` bypass** — a check that allowed `null`/
  `file:` origins → CSWSH from a sandboxed/local page

## The message-side precedents

- **the message-IDOR reports** — a `{"action":"read","id":"<other>"}`
  /`{"doc":"<other>"}`/`{"channel":"<other>"}` returning another's data —
  the WS twin of HTTP IDOR, unenforced per-frame
- **the hidden-action reports** — an `admin`/`debug`/`internal` action
  in the schema the UI never shows — the dispatch with no role check
- **the injection-in-WS reports** — an SQLi/SSTI/CMDi payload in a frame
  field — the HTTP WAF never inspected the frame
- **the token-in-URL reports** — a `?token=`/`?jwt=` leaking to logs

## The protocol-specific precedents

- **Socket.IO** — a `40{token}`/event-envelope that exposed an
  internal/admin namespace; a `namespace`-IDOR
- **STOMP/RabbitMQ** — a `SUBSCRIBE` to another's `/user/` queue
- **MQTT** — a `SUBSCRIBE #`/`+` wildcard reading every topic
- **graphql-ws** — a `subscription{...}` without a field-level authz

## The CTF precedents

- a `wss://x/ws` chat app whose `history` frame leaks the flag
- a `{"action":"admin"}`/debug-action teaching challenge
- a `?token=`/`?jwt=` credential-in-URL challenge
- a binary/protobuf frame carrying the flag in a numbered field

## The pattern across the reports

Every published bug is one of: a handshake check left off (Origin/auth),
or a per-message control the HTTP app has that the WS path does not —
the socket is a second API whose validators were never written.
