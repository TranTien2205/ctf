# Operator notes — the field lessons the corpus earned

## The `101` trap is the dominant false-positive

Every thin WebSocket writeup shows a `101` and calls it the bug. The
`101` is the channel — the finding is a frame the server sent that it
should not have. A session that ends at the `101` ends at surface.

## The bundle is always the schema

The single highest-yield recon step is `bundle_miner` +
`grep (action|type|event|emit|send|on|id|room)`. The bundle carries the
endpoint, the client library (the framing), the action set, the field
names — the real schema. A guessed schema produces `unknown action`/
`invalid field` weak-negatives that read as a defended socket.

## The HTTP `403` is not the WS verdict

The `GET /api/objects/x -> 403` closes the HTTP IDOR cell — it says
NOTHING about the WS `{"action":"read","id":"x"}`. The WS authz is a
separate implementation, routinely weaker — measure the frame, not the
HTTP twin.

## One field per connection is non-negotiable

The socket is async; a reply does not name the frame that caused it.
Two payloads on one socket = an unanswerable "which did this". A fresh
socket per mutation; the reply is then attributable.

## The envelope is a precondition

A bare `{"action":"x"}` into a Socket.IO channel reads as a clean
negative — it is a framing error. The `42["x",{...}]`, `a["{...}"]`,
`SEND destination:`, `{"type":"subscribe"}` shape is required FIRST —
the envelope is the transport's syntax for the app's message.

## CSWSH is a four-legged chair

Foreign-`Origin` accepted AND cookie-binding AND the cookie travels
(`SameSite`) AND a data/action channel. The common trap: the `101`+
foreign-`Origin` is treated as CSWSH — it is the first leg only. A
`SameSite=Strict` cookie or a `?token=`-binding kills it.

## The token-in-URL is its own finding

`?token=`/`?jwt=`/`?key=`/`?auth=` leaks to server/proxy logs, browser
history, `Referer` — independent of the channel's authz. It is
`web-auth-session`/`web-info-disclosure`, not a CSWSH leg — do not
fold it in.

## The "accepts but drops" is a gray zone

A `101`+silent-drop is neither a finding nor a `uniform` — it is a
`gap`. The channel may process frames internally (a write-only socket).
Record it; check the STATE it produced, not a reply.

## The subscription is the other read

The corpus focuses on the action/IDOR frames; the `subscribe`/`join`/
`watch`/`SUBSCRIBE destination:`/`SUBSCRIBE #` is the OTHER read-side —
another's feed, the internal channel, the wildcard. A subscribe-only
socket has no action surface — the membership IS the check.

## The per-transport cell is per-endpoint

A `/socket.io/` and a `/ws` on the same host are TWO sockets — each
gets its own handshake/message pass. A check on one transport does not
transfer to the other.

## The flag is in the channel, not the socket

The socket is the transport; the flag rides a frame — another's object,
an internal feed, a privileged action's reply, an injected extraction.
The socket that opens is never the flag.
