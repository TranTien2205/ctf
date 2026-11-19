# Summary (deep) — the whole class in one page

## The model

A WebSocket is an HTTP-upgrade handshake + a bidirectional frame stream.
The handshake is the one-shot auth/`Origin` checkpoint; the frames are
the app's API — and the per-frame authz is routinely missing.

## The four gap classes

```text
handshake-side:
  foreign-Origin  -> CSWSH (the four-leg chain) / the Origin-gap
  unauth          -> an open channel
  token-in-URL    -> a credential-leak
  sub-protocol    -> an alternate/weaker-authed protocol
  first-frame auth -> a forgeable/stale/null token

message-side:
  object-IDOR        -> {"action":"read","id":"<other>"} -> another's obj
  membership-IDOR    -> {"action":"join"/"subscribe","<other-ch>"}
  action-dispatch    -> {"action":"<privileged>"} -> a privileged reply
  role-self-grant    -> {"action":"x","role":"admin"}
  identity-spoof     -> {"from":"<other>","action":"x"}
  injection          -> {"<sink-field>":"<payload>"} -> the payload class
  write-side gap     -> {"action":"transfer"/"set"/"broadcast"/"delete"}
  subscription-IDOR  -> another's feed/topic/queue
  session-resumption -> a stale/foreign context
```

## The check order — the pass

```text
1. bundle_miner + grep -> the endpoint + the framing + the schema
2. the handshake cells -> origin/binding/unauth/token/subproto/samesite
3. the framing         -> raw/42[...]/a[...]/STOMP/{"type":}/binary
4. the message cells   -> idor/action/spoof/inject/subscribe
5. the boundary        -> one field per connection -> the oracle
6. the route           -> the flag-closing class
```

## The evidence discipline

- `oracle` — a cross-boundary reply — the verbatim bytes are the proof
- `uniform` — a measured rejection — the cell is closed
- `weak-negative` — a guessed-name rejection — re-probe the real schema
- `gap` — an unresponsive cell — not a verdict
- `surface` — a `101`/`pong`/`ok` — never a finding
- the `post-probe` gate asserts `--evidence` ⊂ `--response` — checked

## The falsifier — the original, kept

"a `403`/`forbidden`/`unknown action`/`dropped` on EVERY mutated frame +
a `403`/`close` on EVERY foreign `Origin` + the `101` requires a real
credential — the channel is closed; the class is `uniform`."

## The one-field-per-connection rule

The channel is async — a reply is unattributed to a frame. A fresh
socket per mutation; the reply is attributable.

## The boundary rules — the confusables

- a frame-field injection → the PAYLOAD's class
- an HTTP object-gap → `web-idor`, not this class
- a token's forge → `web-auth-session`
- a one-shot forged request → `web-csrf` (not CSWSH)
- a `graphql-ws` subscription → the QUERY is `web-graphql`

## The tools

```bash
python3 tools/web/ws_probe.py "$WS/ws" --message '<json>' \
    [--origin '<o>'] [--headers 'H: v'] [--timeout N] [--selftest]
python3 tools/proto_decode.py frame.bin [--hex "..."]
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle
```

## The honest state

`web-websocket` is a catalogue class — no local card. The corpus is
standard published guidance; a confirmed local chain is the FIRST
verification, filed via `classify_solve.py`.

## The last word

The socket is the transport — the finding is the cross-boundary frame.
A `101` opens the channel; the flag rides a frame — another's object,
an internal feed, a privileged action's reply, an injected extraction.
The depth is the per-field per-mechanism pass, one mutation at a time,
recorded verbatim.
