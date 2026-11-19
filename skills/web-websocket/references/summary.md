# Summary — the class in one page

## The model

A WebSocket = HTTP-upgrade + a bidirectional frame stream. The upgrade
is the one-shot auth/`Origin` checkpoint; the frames are the app's API —
the per-frame authz is routinely missing.

## The gaps

```text
handshake:  foreign-Origin (CSWSH) / unauth / token-in-URL / sub-protocol
message:    object-IDOR / membership-IDOR / action-dispatch / self-grant
            / identity-spoof / injection / write-side / subscription-IDOR
session:    resumption / fragment-split / compression / transport-switch
```

## The pass

```text
1. bundle_miner + grep -> the endpoint + framing + schema
2. handshake cells     -> origin/binding/unauth/token/subproto/samesite
3. framing             -> the envelope
4. message cells       -> idor/action/spoof/inject/subscribe — 1 field/conn
5. verdict + route     -> the oracle reply -> the flag-closing class
```

## The discipline

- `oracle` = a cross-boundary reply — the verbatim bytes
- `uniform` = a measured rejection — a closed cell
- `weak-neg`/`gap` = a re-probe / unmeasured — not a verdict
- `surface` = a `101`/`pong`/`ok` — never a finding
- one field per connection — the async reply is unattributed otherwise
- the envelope before the payload — the framing is a precondition
- CSWSH needs all four legs — the `101` is leg-1 only

## The tools

```bash
python3 tools/web/ws_probe.py "$WS/ws" --message '<json>' \
    [--origin '<o>'] [--headers 'H: v'] [--selftest]
python3 tools/proto_decode.py frame.bin
python3 tools/web/bundle_miner.py "$BASE" --out /tmp/bundle
```

## The honest state

`web-websocket` is a catalogue class — no local card. The corpus is
standard published guidance; a confirmed local chain is the FIRST
verification, filed via `classify_solve.py`.

## The last word

The socket is the transport — the finding is the cross-boundary frame.
