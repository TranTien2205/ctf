# Common questions — the FAQ

## "The socket opened (101) — is that the bug?"

No. The `101` is the handshake — the channel exists. The finding is a
frame that read another's data or changed state. A `101` + empty
`pong` is surface evidence. `common-mistakes.md` leads with this.

## "How is this different from CSRF?"

CSRF fires a one-shot forged request — the attacker cannot read the
response. CSWSH opens a bidirectional socket with the victim's cookies —
the attacker page reads the victim's live channel AND writes into it.
`class-boundary.md`.

## "The foreign Origin is accepted — CSWSH?"

Only if the socket also binds to the victim's session cookie AND that
cookie travels (`SameSite`) AND the channel carries data/actions. A
`101` under a foreign `Origin` alone is the Origin-check gap — a
necessary but not sufficient condition. `cswsh.md`.

## "The socket asks for a token — how do I probe?"

A `?token=`/`Authorization`/`connection_init`/`40{"token"}` — the auth
moves to the frame. If the token is one you control (your own session),
probe the message-side; if it is the victim's, CSWSH needs the
cookie-binding, not the token.

## "The reply is binary — what is it?"

Likely protobuf — `proto_decode.py frame.bin`. Or a serialized object
(`web-deserialization`), or a wrapped SockJS/Socket.IO envelope —
unwrap first. `framing-protocols.md`.

## "How do I enumerate the message schema?"

The client bundle — `bundle_miner` + `grep` for `action`/`type`/`event`/
`emit`/`send`/`on`/`id`/`room`. The observed frames on a real session
are the ground truth; the bundle fills in the rest.

## "Can I send two payloads on one socket?"

No — the reply is unattributable. One field per connection; a fresh
socket per mutation. `common-mistakes.md`.

## "The HTTP API blocks /api/objects/victim — is the WS closed?"

No — the WS authz is a separate, weaker implementation. Measure the
`{"action":"read","id":"victim"}` FRAME, not the HTTP twin. The
message-side is where the HTTP app's checks often do not reach.

## "A `?token=` in the ws URL — a finding?"

Yes — credential-in-URL: it leaks to server/proxy logs, browser
history, `Referer`. `web-auth-session`/`web-info-disclosure`, not this
class's oracle — but record it.

## "Is a Socket.IO `40`/`42` envelope the same as `{"action"}`?"

No — `42["event",{data}]` is the envelope; send that shape, not bare
JSON. `framing-protocols.md`.

## "The socket silently drops my frames — bug or no?"

Neither — a closed channel. Record `uniform: no reply`; it is not an
oracle and not a confirmed-safe state. `negative-results.md`.
