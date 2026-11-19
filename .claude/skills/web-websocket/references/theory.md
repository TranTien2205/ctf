# Theory — the protocol model, in one page

## The two phases

```text
phase 1: the HTTP-upgrade handshake — GET + Upgrade:websocket + 101 —
         carries the auth (Cookie/?token=/Authorization) + the Origin +
         the sub-protocol negotiation — a one-shot checkpoint
phase 2: the frame stream — bidirectional, fin/opcode/masked/len/payload —
         the app's messages — the per-frame dispatch
```

## The gap model — the two surfaces

```text
handshake-side:  the Origin check (CSWSH) / the auth presence (unauth) /
                 the credential carrier (token-in-URL) / the sub-protocol
message-side:    the per-frame authorize(user, action, fields) — routinely
                 missing -> the IDOR/dispatch/spoof/inject
```

## The asymmetry — the twin-API

```text
HTTP:   authorize(user, method, path)      -> per-request
WS:     dispatch(msg.action, msg.fields)   -> per-frame, where
        authorize(user, action, fields) is optional
```

The same object is `403` over HTTP, `200` over WS — the WS authz is the
unenforced twin.

## The CSWSH chain — the four legs

```text
leg1: foreign-Origin accepted (the server does not check Origin)
leg2: cookie-binding (the socket binds the victim session-cookie)
leg3: the cookie travels (SameSite=Lax/None)
leg4: the channel carries data/actions (a read/write surface)
```

All four -> the attacker page reads/writes the victim's live socket.

## The SameSite caveat

`SameSite=Strict` -> the browser blocks the cookie cross-site — a
BROWSER defense on the chain; the server-side `Origin`-acceptance is
the gap it masks. `Lax`/`None` -> the cookie travels.

## The verdicts — the reply vocabulary

```text
a cross-boundary reply  -> oracle (the proof)
a measured rejection    -> uniform (a closed cell)
a guessed-name reject   -> weak-negative (a re-probe)
a drop/silence          -> a gap (unmeasured)
a pong/ok/echo/101      -> surface (not a finding)
```

## The record

`theory: <the model> -> <the gap it produces> -> <the oracle>` — the
model names the gap; the oracle measures it.
