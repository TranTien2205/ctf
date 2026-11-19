# Lead grammar — the observation → class grammar

## The lead-vocabulary — the observation words

```
observed            -> the class lead
'websocket'|'ws'    -> web-websocket
'chat'|'live'|'realtime'|'notification'|'presence' -> web-websocket
'socket.io'|'sockjs'|'stomp'|'pusher'|'ably'|'mqtt' -> web-websocket
'101'|'upgrade'|'sec-websocket' -> web-websocket
'graphql-ws'|'subscription' -> web-websocket + web-graphql
'?token='|'?jwt='  -> web-auth-session + web-websocket
'binary'|'protobuf' -> web-websocket + proto_decode
```

## The handshake leads — the class grammar

```
'101'+foreign-Origin            -> cswsh-candidate
'101'+cookie-binding            -> a bound channel
'101'+no-auth+data              -> unauth-channel
'101'+no-auth+drop-all          -> a closed channel (a gap)
'?token='/'?jwt='/'?key='        -> credential-in-URL
'403'+foreign-Origin+all-bypasses -> uniform: origin
'Sec-WebSocket-Protocol:<alt>'   -> a sub-protocol surface
```

## The message leads — the class grammar

```
'{"action":"read","id":"<other>"}'+another's-object -> message-idor
'{"action":"<privileged>"}'+a-reply              -> action-dispatch
'{"from":"<other>"}'+acts-as-other              -> identity-spoof
'{"role":"admin"}'+accepted                     -> self-grant
'{"<field>":"<payload>"}'+the-eval/read         -> injection (payload class)
'{"action":"subscribe","<other-channel>"}'+feed -> subscription-idor
'{"action":"broadcast"}'+cross-client           -> a write-blast
```

## The framing leads — the transport grammar

```
'{"action":...}' bare            -> raw ws
'42["e",{...}]'                  -> socket.io
'a["{...}"]'                     -> sockjs
'CONNECT'/'SEND'/'SUBSCRIBE'     -> stomp
'{"type":"subscribe",...}'        -> graphql-ws
'SUBSCRIBE'/'PUBLISH'/'#'         -> mqtt
'\x0a\x05...' binary             -> protobuf -> proto_decode
'0{sid...}'/'40'/'42'            -> socket.io packet-types
```

## The reply leads — the verdict grammar

```
'<other-object-json>'            -> oracle: idor
'{"flag"/"admin"/privileged}'    -> oracle: dispatch
'49'/'evaluated'                 -> oracle: inject
'a pushed feed'                  -> oracle: subscribe-idor
'forbidden'/'unauthorized'       -> uniform
'unknown action'/'invalid field' -> weak-neg
'not found'                      -> weak-neg
'malformed'/'bad request'        -> framing-error
'pong'/'ok'/'echo'               -> surface
'silence/drop'                   -> gap
'500'/crash                      -> candidate-differential
```

## The grammar-rule

The lead-grammar is the classifier's input — the observed literals map
to the class + the confidence; a `web-websocket` observation routes to
this skill; a `graphql`/`deserialize`/`sqli` literal inside a frame
routes the PAYLOAD to its own class.
