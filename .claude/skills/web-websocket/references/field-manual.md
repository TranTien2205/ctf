# Field manual — the operational lessons

## The bundle is the schema

The client bundle knows the endpoint, the client lib (the framing), the
action set, and the field names. `bundle_miner` it FIRST — a guessed
schema is a weak probe; the bundle's `ws.send`/`socket.emit` is the
exact shape.

## A `101` is never the finding

The single most common false-positive: "the socket opened". A `101`
means the channel exists — nothing is authorized yet. The finding is a
frame the server sent that it should not have — victim data, a
privileged action's reply — or a state a frame changed. No reply-data /
no state-change = no finding.

## The handshake is the cheap win

Before any frame work, the handshake answers: is `Origin` enforced
(CSWSH)? is the socket cookie-bound? is there a `?token=`? These three
are one `ws_probe` each — the cheapest, highest-value checks.

## The message-side is where the flags are

Once the channel is open, the per-frame authz is the gold: the
`{"action":"read","id":"<other>"}` message-IDOR (another's object), the
hidden `{"action":"admin"}` (the privileged dispatch), the
`{"from":"<victim>"}` (the identity spoof). The HTTP app would `403`
these; the frame often does not.

## One field per connection — always

The channel is async — a reply arrives unattributed to a specific
frame. Two payloads on one socket = an unanswerable "which caused it".
Fresh socket, one mutated field, read the reply.

## The envelope before the payload

A bare `{"action":"x"}` into a Socket.IO `42`-envelope channel reads as
a clean negative — it is a framing error. `42["x",{...}]`, `a["..."]`,
`SEND destination:` — send the envelope's shape.

## CSWSH needs all four

Foreign-`Origin`-accepted AND cookie-binding AND the cookie travels
(SameSite) AND a data/action channel. Miss one and it is not CSWSH —
it is a foreign-`Origin` acceptance (a weaker finding) or a
`SameSite`-blocked dead end.

## The token-in-URL is its own finding

`?token=` leaks to logs/history/referer regardless of the channel's
authz — report it (`web-auth-session`); do not fold it into CSWSH.

## The "accepts but drops" gray zone

A `101` that silently drops unauth frames is neither a finding nor a
confirmed-safe state — record `uniform: no reply`, note it may process
frames internally, and move on.
