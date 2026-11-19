# Detection catalogue — the full observable inventory, indexed

## The endpoint inventory

```text
the paths:    /ws /socket /realtime /live /stream /events /chat
              /socket.io/ /sockjs/ /stomp /mqtt /graphql /subscriptions
              /api/ws /v1/ws /api/realtime /api/socket /ws/v1 /ws/socket.io
              /socket.io/ws /notify /feed /push
the schemes:  ws:// wss://
the params:   ?token= ?jwt= ?auth= ?key= ?api_key= ?session=
              ?EIO= ?transport= ?sid= ?t= ?version= ?v=
```

## The client-library inventory

```text
raw:          new WebSocket, ws://, wss://, onmessage, send, close,
              readyState, CONNECTING/OPEN/CLOSING/CLOSED
socket.io:    io(, io.connect, socket.io-client, engine.io, socket.emit,
              socket.on, socket.on('connect'), EIO=, transport=, sid=,
              0/1/2/3/40/41/42/43/44/45 packet-types, /<ns> namespaces
sockjs:       new SockJS, sockjs-client, /info, /<srv>/<sess>/<transport>,
              o/a[...]/h/c[...], xhr_streaming/xhr_polling/eventsource/
              htmlfile/iframe fallbacks
stomp:        Stomp.over, stomp-websocket, stompClient, .connect/.send/
              .subscribe, CONNECT/SEND/SUBSCRIBE/MESSAGE/ACK/NACK,
              /topic//queue//app//user//exchange/ destinations
pusher:       new Pusher, pusher-js, channel.bind, channel.trigger,
              pusher:subscription_succeeded, cluster=, app key
ably:         new Ably.Realtime, ably, channel.subscribe, channel.publish,
              channel.presence, the Ably protocol frames
graphql-ws:   createClient, graphql-ws, graphql-transport-ws,
              connection_init/subscribe/next/error/complete,
              graphql-transport-ws protocol
mqtt:         mqtt.connect, mqtt.js, SUBSCRIBE/PUBLISH/CONNECT/CONNACK/
              SUBACK/PUBACK/PINGREQ, #/+ topic wildcards, QoS
```

## The handshake-header inventory

```text
the required:  Connection: Upgrade
               Upgrade: websocket
               Sec-WebSocket-Version: 13
               Sec-WebSocket-Key: <b64 nonce>
the auth:      Cookie / Authorization / ?token= / X-Api-Key / X-Auth-Token
the routing:   Host / Origin / Referer
the negotiate: Sec-WebSocket-Protocol (the sub-protocol)
               Sec-WebSocket-Extensions (permessage-deflate, etc.)
the reply:     101 Switching Protocols
               Upgrade: websocket
               Connection: Upgrade
               Sec-WebSocket-Accept: <sha1>
               Sec-WebSocket-Protocol: <the accepted sub>
               Set-Cookie / X-User / X-Role (a leaked identity)
```

## The frame-field inventory

```text
the dispatch:    action type event cmd command method op verb kind do
                 fn handler route call name sub cmd_ cmdName exec
the identity:    from sender user_id uid user principal subject actor
                 author owner creator account_id as_user impersonate
the role/grant:  role perm perms permission scope level tier rank
                 is_admin isAdmin admin debug internal privileged sudo
                 superuser staff moderator
the object:      id doc document room channel conversation thread
                 topic account org tenant object item record resource
                 project file note message ticket order invoice entity
                 target to recipient receiver for_user subject_id
the query:       q search query filter where order sort field column
                 select match criteria expression clause
the sink:        file path filename url fetch webhook callback image
                 xml data import parse svg host cmd exec command target
                 obj config set merge key value template tpl input text
                 content body msg message
the auth:        token auth jwt session key session_id resume reconnect
                 seq offset lastEventId api_key secret credential
the membership:  subscribe join watch listen follow room channel topic
                 destination namespace feed event_name
```

## The reply-shape inventory

```text
a data frame:    {"id":..,"data":..} / 42["ev",{..}] / a[..] / MESSAGE /
                 next / PUBLISH / a binary / a pushed feed
an error frame:  {"error":".."} / {"status":4xx} / 44 / c[code,"..."] /
                 ERROR frame / {"type":"error"}
a control frame: ping/pong / 0/1/2/3 / 40/41 / h / CONNECTED / CONNACK /
                 connection_ack / open / hello / welcome
an echo frame:   pong / ok / {"status":"ok"} / the sent-data back / ack
a push frame:    a server-initiated event — a notification/feed/update
```

## The auth-model inventory

```text
handshake-auth:  Cookie / Authorization / ?token= / X-<custom> /
                 Sec-WebSocket-Protocol-selected
frame-auth:      {"type":"auth"} / {"type":"connection_init"} /
                 40{"token"} / CONNECT login:passcode / {"action":"auth"} /
                 {"action":"login"}
resume-auth:     session_id / resume / reconnect / seq / offset /
                 lastEventId
no-auth:         a 101 with no credentials — the open channel
```

## The catalogue-record

`catalogue: <category>: <the observed values>` — each category's
inventory; the observed values seed the probes.
