# Mechanism (deep) — the formal gap model

## The upgrade handshake — the one-shot auth

```text
the client: GET /ws + Upgrade:websocket + Sec-WebSocket-Key +
            [Cookie | Authorization | ?token=] + Origin
the server: checks [Origin? | auth? | subproto?] -> 101 | 401/403/400
the result: the socket's identity = the handshake's credential — a
            one-shot binding that persists for the socket's life
```

The handshake is the ONLY auth checkpoint — a message carries no
credentials. The gap surface: the `Origin` check (CSWSH), the auth
presence (unauth), the credential carrier (token-in-URL), the
sub-protocol (a weaker-authed protocol).

## The frame-dispatch — the per-message authz

```python
async for msg in websocket:
    action = msg.get('action')
    handler = HANDLERS.get(action)
    if handler:
        await handler(msg)      # <-- the authorize(user, action, fields)
                                #     is what's missing here
```

The gap-surface — the four message-side mechanisms:

```text
the object-IDOR:    handler(msg) reads msg['id'] -> no owner check
the action gap:     HANDLERS['admin'] runs -> no role check
the spoof:          msg['from']/msg['role'] trusted -> the handshake's
                    identity is not the frame's
the injection:      handler(msg) -> a sink(query/template/path/cmd/
                    deser/fetch) consumes msg['<field>']
```

## The trust-asymmetry — the formal statement

```text
HTTP:   authorize(user, request.method, request.path)  — per-request
WS:     dispatch(msg.action, msg.fields)               — per-frame,
        where authorize(user, msg.action, msg.fields) is optional
```

The asymmetry: the same resource, the same scope, a different
enforcement point — and the WS enforcement point is routinely missing.

## The gap classes — the formal set

| Gap | The violation | The oracle |
|---|---|---|
| foreign-Origin | `Origin` not checked at `101` | `101` on a foreign `Origin` |
| unauth-channel | no credential required | `101`+data, no auth |
| token-in-URL | a credential in the URI | `?token=` on the URL |
| object-IDOR | `authorize(user, obj)` not run | another's object |
| membership-IDOR | `authorize(user, channel)` not run | another's feed |
| action-dispatch | `authorize(user, action)` not run | a privileged reply |
| self-grant | `authorize(user, role)` not run | the grant accepted |
| spoof | `msg.identity` trusted over `session` | acts-as-other |
| injection | `msg.field` -> a sink | the eval/read |
| write-side | `authorize(user, action, state)` not run | a state-change |
| subscription-IDOR | `authorize(user, feed)` not run | another's pushed feed |
| resumption | `resume(session_id)` trusts the id | a stale/foreign context |

## The read-side/write-side formalization

```text
read-side:   the reply carries another's data -> a confidentiality gap
write-side:  the frame changes another's state -> an integrity gap
```

Both cross the principal/role boundary — the read-side is the leak, the
write-side is the impact.

## The SameSite formalization

```text
SameSite=Strict:  the browser never sends the cookie cross-site -> CSWSH
                  cannot complete (the browser leg fails) — the server
                  gap remains but is not browser-exploitable
SameSite=Lax:     sends on top-level navigation; a sub-resource
                  new WebSocket is browser-dependent -> TEST it
SameSite=None:    sends always -> CSWSH exploitable
no SameSite:      Lax default
```

The SameSite is a browser defense on the CSWSH chain — the server-side
`Origin` acceptance is the gap the browser defense masks.

## The mechanism-to-verb map

| Verb | The mechanism |
|---|---|
| `read`/`get`/`open`/`load`/`fetch`/`history`/`list`/`dump`/`export` | the read-side object-IDOR |
| `send`/`transfer`/`set`/`broadcast`/`update`/`grant`/`reset`/`delete`/`create`/`emit-all` | the write-side gap |
| `join`/`subscribe`/`watch`/`listen`/`follow`/`unsubscribe` | the membership-IDOR |
| `admin`/`debug`/`internal`/`system`/`eval`/`exec`/`flag`/`config`/`su`/`impersonate`/`login_as` | the dispatch gap |
| `auth`/`login`/`init`/`resume`/`reconnect`/`connection_init`/`CONNECT` | the auth/resumption |

## The mechanism-record

`mechanism: <the gap>: <the violation>: <the oracle>` — the formal model
names the violation; the oracle is the measured reply.
