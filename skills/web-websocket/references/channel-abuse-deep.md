# Channel abuse (deep) — the original reference, deepened

## The core model — the two trust surfaces

The channel is a `ws://`/`wss://` bidirectional pipe over an HTTP
upgrade — two trust surfaces: the handshake (the auth + the `Origin`
check) and the message-side (the per-frame dispatch). The gaps live
on both.

## The handshake-side checks — the original + deepened

```bash
# the Origin check
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'
# the bypass set when 403
for o in 'null' 'file://' 'https://target.evil.com' 'https://target.com.evil.com' \
         'https://sub.target.com' 'https://eviltarget.com'; do
  python3 tools/web/ws_probe.py "$WS/ws" --origin "$o" --message '{}'
done
# the binding matrix
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=victim' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Authorization: Bearer x' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws?token=eyJ" --message '{"action":"me"}'
# the no-auth open
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'
# the sub-protocols
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws' --message '{}'
# the SameSite read — the CSWSH precondition
curl -sI "$BASE/login" | grep -i 'set-cookie'
```

The handshake answers: is `Origin` enforced? is the socket cookie-bound?
is there a `?token=`? is a sub-protocol accepted? These are the cheap
checks — run them FIRST.

## The message-side checks — the original + deepened

The core mutations, one field per connection:

```json
{"action":"read","id":"<other>"}      the object-IDOR
{"action":"join","room":"<restricted>"} the membership-IDOR
{"action":"admin"}                     the dispatch gap
{"from":"<victim>","action":"x"}       the identity-spoof
{"action":"x","role":"admin"}          the role-self-grant
{"q":"<payload>"}                      the injection carrier
{"action":"transfer","to":"me"}        the write-side gap
{"action":"subscribe","channel":"<other>"} the subscription-IDOR
```

The deep files: `message-idor-deep.md`, `action-dispatch-deep.md`,
`injection-in-frames-deep.md`, `per-message-field-deep.md`.

## The schema-learn — the bundle is the ground truth

The client bundle knows the endpoint, the client library (the framing),
the action set, the field names, the auth mechanism. `bundle_miner` +
`grep` for `action`/`type`/`event`/`id`/`room`/`channel`/`token` — the
real schema before any payload.

## The one-field-per-connection rule — non-negotiable

The channel is async — a reply is unattributed to a specific frame.
Two payloads on one socket = "which caused it?" — unanswerable. A fresh
socket per mutation; the reply is then attributable. This is the single
most-violated rule in WS testing.

## The framing-before-payload rule

A bare `{"action":"x"}` into a Socket.IO channel is a framing error, not
a finding — send `42["x",{...}]`. `framing-protocols-deep.md` decodes
every envelope.

## The CSWSH four-leg chain — the original deepened

```
leg1: foreign-Origin accepted (a 101, verbatim)
leg2: the socket binds the victim session-cookie
leg3: the cookie is SameSite=Lax/None (it travels)
leg4: the channel carries data/actions
```

All four legs — the verbatim evidence per leg. A `SameSite=Strict`
cookie or a `?token=` binding kills the chain.

## The original falsifier — kept verbatim

"a `403`/`forbidden`/`unknown action`/`dropped` on EVERY mutated frame +
a `403`/`close` on EVERY foreign `Origin` + the `101` requires a real
credential — the channel is closed; the class is `uniform`."

The deepened kill-map: `falsifiers-deep.md` + `per-falsifier.md`.

## The record-shape — the original

```
channel: <the ws endpoint>
handshake: <origin|binding|token|subproto>: <the verdict>
frame:    <the mutated frame, verbatim>
reply:    <the verbatim reply>
verdict:  <oracle|uniform|weak-neg|gap>
route:    <the flag-closing class>
```
