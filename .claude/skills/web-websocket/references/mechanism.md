# Mechanism — the gap the channel produces

## The model

```text
[the client's page] --HTTP-upgrade--> [the WS server] --frames--> [app]
        ^                                                    ^
        | 1. the upgrade carries the auth+Origin             | 2. the frames carry
        |    — the CSWSH + the binding live here             |    actions+fields —
        |                                                    |    the IDOR/dispatch/
        |                                                    |    spoof/inject live here
```

The channel has TWO trust surfaces — the handshake (the one-shot auth +
the `Origin` check) and the message-side (the per-frame dispatch). The
gaps live on both.

## The handshake-side gap — the channel-open

- **no `Origin` check** — the server accepts a foreign-origin socket —
  the browser attaches the victim's cookie → CSWSH
- **no auth** — a `101` with no credentials → an unauth channel
- **a `?token=`/`?jwt=`** — a credential-in-URL leak
- **a first-frame auth** — the token in a frame, forgeable/stale

## The message-side gap — the frame-dispatch

```python
async for msg in websocket:
    handler = HANDLERS.get(msg['action'])   # no role check on the action
    if handler: await handler(msg)          # no scope check on the fields
```

- **an object field** — `{"action":"read","id":"<other>"}` — a per-object
  scope check that does not run → message-IDOR
- **a dispatch field** — `{"action":"admin"}` — a role check that does
  not run → a privileged action
- **an identity field** — `{"from":"<victim>"}` — a `from`/`role`/`user_id`
  the server trusts → a spoof/self-grant
- **a sink field** — `{"q":"<sqli>"}` — a field reaching a sink → inject

## The asymmetry — the twin-API gap

The HTTP app's `authorize(request.user, request.path)` is a per-request
check; the WS's `dispatch(action, fields)` is a per-FRAME check that is
rarely written. The same object is `403` over HTTP and `200` over WS.

## The read/write split

- **read-side** — a frame returning another's data — `read`/`get`/
  `history`/`subscribe`/`open`/`dump`/`list`
- **write-side** — a frame changing state — `send`/`transfer`/`set`/
  `broadcast`/`grant`/`delete`/`create`

A read-side gap is the leak; a write-side gap is the impact.

## The mechanism-to-skill map

| The gap | The flag-closing skill |
|---|---|
| CSWSH | `web-websocket`/`web-csrf` |
| unauth channel | `web-websocket`/`web-info-disclosure` |
| message-IDOR | `web-idor` |
| action-dispatch | `web-auth-session`/`web-logic-flaw` |
| self-grant/spoof | `web-mass-assignment`/`web-auth-session` |
| inject | the payload class |
| token-URL | `web-auth-session`/`web-info-disclosure` |
| subscribe-IDOR | `web-idor` |
| graphql-WS | `web-graphql` |

## The mechanism-record

`mechanism: <the gap>: <the check>: <the boundary it crosses>` — the
gap is named; the check measures it; the boundary is what it crosses.
