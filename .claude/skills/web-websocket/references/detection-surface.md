# Detection surface — the per-surface detection order

## The endpoint surface

```text
the ws endpoint paths to try:
  /ws  /socket  /realtime  /live  /stream  /events
  /socket.io/  /sockjs/  /stomp  /mqtt  /graphql  /subscriptions
  /api/ws  /v1/ws  /api/realtime  /api/socket  /ws/v1
  /ws/socket.io  /socket.io/ws  /chat  /notify  /feed
```

The bundle names the real one — a `404`/non-ws path is a wrong path,
not a closed surface.

## The transport surface — the client libraries

```text
raw WebSocket   -> new WebSocket() / onmessage / send
Socket.IO       -> io() / socket.emit / socket.on
SockJS          -> new SockJS() / onmessage / send
STOMP           -> Stomp.over() / stompClient.subscribe/send
Pusher          -> new Pusher() / channel.bind / channel.trigger
Ably            -> new Ably.Realtime() / channel.subscribe/publish
graphql-ws      -> createClient() / subscribe / connection_init
MQTT            -> mqtt.connect() / client.subscribe/publish
```

## The handshake surface — the headers + params

```text
the headers:   Connection: Upgrade  Upgrade: websocket
               Sec-WebSocket-Version: 13
               Sec-WebSocket-Key: <b64>
               Sec-WebSocket-Protocol: <the-sub>
               Sec-WebSocket-Extensions: permessage-deflate
               Origin: <the-origin>  Cookie: <the-session>
               Authorization: <the-bearer>  X-<custom>
the params:    ?token=  ?jwt=  ?auth=  ?key=  ?api_key=  ?session=
               ?EIO=  ?transport=  ?sid=  ?t=  ?version=
```

## The schema surface — the field/action names

```text
the dispatch:    action type event cmd command method op verb kind do
                 fn handler route call name
the identity:    from sender user_id uid user principal subject
                 role perm is_admin debug internal scope level tier
the object:      id doc document room channel conversation thread
                 topic account org tenant object item record resource
                 project file note message ticket order invoice
the query:       q search query filter where order sort field column
the sink:        file path filename url fetch webhook callback image
                 xml data import parse svg host cmd exec command target
                 obj config set merge key value
the auth:        token auth jwt session key session_id resume reconnect
                 seq offset lastEventId reconnect
the membership:  subscribe join watch listen follow room channel topic
                 destination namespace
```

## The reply surface — the reply shapes

```text
a data frame      -> {"id":..,"data":..} / 42["ev",{..}] / a[..] /
                     MESSAGE / next / PUBLISH / binary
an error frame    -> {"error":".."} / 44 / c[..] / ERROR / error
a control frame   -> ping/pong/0/1/2/3/40/41/h / CONNECTED / CONNACK /
                     connection_ack / open
an echo           -> pong / ok / {"status":"ok"} / the sent-data back
```

## The auth surface — the binding points

```text
the handshake:    Cookie / Authorization / ?token= / Sec-WebSocket-
                  Protocol / X-<custom> / the sub-protocol selection
the first-frame:  {"type":"auth"} / {"type":"connection_init"} /
                  40{"token"} / CONNECT login:passcode / {"action":"auth"}
the resume:       session_id / resume / reconnect / seq / offset /
                  lastEventId
```

## The per-surface detection record

`surface: <endpoint|transport|handshake|schema|reply|auth>: <the
observed>` — each surface's observed values; the unobserved surfaces are
the pending cells.
