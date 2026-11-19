# Per check — each check, its probe, its verdict, its record

## The handshake checks

| Check | Probe | The `oracle` reply | The `uniform` reply |
|---|---|---|---|
| Origin-enforce | `--origin 'https://evil'` | `101` | `403`/close on all bypasses |
| auth-binding | `Cookie:`/`Authorization:`/`?token=` | the bound identity | `anonymous`/no-cookie `401` |
| unauth-open | no credential | a `101`+data reply | a `401`/drop-all |
| token-in-URL | `?token=`/`?jwt=`/`?key=` on the URL | the credential in the URI | — |
| sub-protocol | `Sec-WebSocket-Protocol: x` | an alt-protocol accepted | `400`/close |
| the `SameSite` read | `Set-Cookie` on the HTTP login | `SameSite=Lax/None` | `SameSite=Strict` |

## The message checks — per mechanism

| Check | Probe | The `oracle` reply | The `uniform` reply |
|---|---|---|---|
| object-IDOR | `{"action":"read","id":"victim"}` | another's object | `forbidden`/`404` |
| membership-IDOR | `{"action":"join","room":"admin"}` | the restricted feed | `forbidden` |
| action-dispatch | `{"action":"admin"}` | a privileged reply | `forbidden`/`unknown` |
| role-self-grant | `{"action":"x","role":"admin"}` | the grant accepted | ignored/`forbidden` |
| identity-spoof | `{"from":"victim",...}` | acts as victim | the field ignored |
| injection | `{"q":"<payload>"}` | the eval/read | `raw`/error |
| write-side | `{"action":"transfer",...}` | a state-change | `forbidden` |
| subscription | `{"type":"subscribe",...}`/`SUBSCRIBE` | another's feed | `forbidden` |

## The check-order — cheapest-first

1. `origin`/`binding`/`unauth`/`token`/`subproto` — the handshake, ~6 probes
2. `idor`/`action`/`spoof`/`inject` — the message, ~12 probes
3. `subscription`/`write-side` — the state side, ~4 probes

## The check-record — verbatim

```
check: <endpoint>:<cell>
probe: <the exact frame/header>
reply: <the verbatim reply bytes>
verdict: oracle | uniform | weak-negative | gap
route:   <the flag-closing class if oracle>
```

## The check-coverage — the matrix

```
         origin  binding  unauth  token  subproto  idor  action  spoof  inject  sub
/ws
/socket.io
```

Every cell `oracle`/`uniform`/`unmeasured`. A check is `unmeasured`
until its probe ran — not `uniform`-by-default.
