# Reporting — the report shape for each finding

## The finding-report template

```
title:    WebSocket <the-gap>: <the endpoint>
endpoint: <the ws path>
framing:  <raw|socket.io|sockjs|stomp|graphql-ws|mqtt|protobuf>
auth:     <cookie|token|bearer|none>
severity: <the impact>

the handshake:
  Origin:   <the observed Origin-handling>
  binding:  <the auth-binding>
  samesite: <the cookie SameSite>

the probe:    <the verbatim frame/header>
the reply:    <the verbatim reply — the cross-boundary bytes>
the verdict:  <oracle|uniform|weak-negative|gap>
the route:    <the flag-closing class>

the impact:   <the cross-principal data/state — what the frame crossed>
the boundary: <the rule the reply broke>
```

## The CSWSH report

```
title:    Cross-Site WebSocket Hijacking — wss://x/chat
evidence:
  leg1: Origin:https://evil -> 101            (the foreign-Origin accept)
  leg2: Cookie:session -> {"user":"victim"}   (the cookie binds)
  leg3: Set-Cookie: SameSite=Lax              (the cookie travels)
  leg4: {"action":"history"} -> the victim DMs (the data read)
impact:   an attacker page reads/writes the victim's live socket
route:    web-websocket (CSWSH) -> the victim's channel
```

## The message-IDOR report

```
title:    WebSocket message-IDOR — wss://x/doc
control:  {"action":"open","doc":"my-doc"} -> {"doc":"my-doc",...}
evidence: {"action":"open","doc":"admin-doc"} -> {"doc":"admin-doc",
          "flag":"..."}                        <- verbatim
impact:   any socket user reads any doc
route:    web-websocket -> web-idor
```

## The action-dispatch report

```
title:    WebSocket privileged-action — wss://x/ws
evidence: {"action":"admin"} -> {"admin":true,"flag":"...","users":[...]}
impact:   any socket user reaches the admin handler
route:    web-websocket -> the privileged action
```

## The unauth-channel report

```
title:    Unauthenticated WebSocket channel — wss://x/ws
evidence: no-credential 101 + {"action":"dump"} -> {"users":[...],"flag":...}
impact:   the channel needs no credentials; the data flows
route:    web-websocket (unauth) -> the data
```

## The injection report

```
title:    WebSocket injection — wss://x/ws (the q field reaches SQL)
control:  {"action":"search","q":"x"} -> {"results":[...]}
evidence: {"action":"search","q":"' UNION SELECT flag--"} -> {"rows":[
          {"flag":"..."}]}                                   <- verbatim
impact:   the q field reaches the datastore query
route:    web-websocket (carrier) -> web-sqli (the extraction)
```

## The token-in-URL report

```
title:    Credential in WebSocket URL — wss://x/ws?token=eyJ...
evidence: the ws URL carries ?token=<jwt> — logged to server/proxy/
          browser-history/Referer
impact:   the session/JWT leaks
route:    web-auth-session + web-info-disclosure
```

## The negative-report

```
title:    WebSocket <cell>: uniform rejection — wss://x/ws
evidence: {"action":"read","id":"admin"} -> {"error":"forbidden"}
          + id=2,3 / room=admin / channel=internal -> forbidden
verdict:  the object-scope check is enforced — the idor cell is closed
```

## The coverage-report

```
         origin  binding  unauth  idor  action  spoof  inject
/ws      uniform oracle   -       oracle uniform uniform uniform
/socket.io -     -        oracle  -      oracle  -       -
```

The matrix is the report's coverage section — the measured cells + the
verdicts.
