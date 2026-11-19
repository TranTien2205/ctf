# Extended corpus — the remaining named payloads and shapes

## The Socket.IO engine.io URL payload-set

```
/socket.io/?EIO=4&transport=websocket            the v4 ws transport
/socket.io/?EIO=4&transport=polling               the v4 polling
/socket.io/?EIO=3&transport=websocket             the v3 ws
/socket.io/?EIO=3&transport=polling               the v3 polling
/socket.io/?EIO=4&transport=websocket&sid=<sid>   the resumed session
/socket.io/?EIO=4&transport=websocket&t=<ts>      the cache-buster
/socket.io/admin?EIO=4&transport=websocket         the /admin namespace
/socket.io/internal?EIO=4&transport=websocket      the /internal ns
```

## The SockJS URL/envelope payload-set

```
/sockjs/info                                     the info — origins
/sockjs/<srv>/<sess>/websocket                    the ws transport
/sockjs/<srv>/<sess>/xhr_streaming                the xhr-streaming fallback
/sockjs/<srv>/<sess>/xhr_polling                  the xhr-polling fallback
/sockjs/<srv>/<sess>/eventsource                  the eventsource fallback
/sockjs/<srv>/<sess>/htmlfile                     the htmlfile fallback
a["{\"action\":\"x\"}"]                            the data array
a["msg1","msg2"]                                   the batch
```

## The STOMP destination payload-set

```
SEND destination:/app/x                 an app action
SEND destination:/app/admin             an admin action
SUBSCRIBE destination:/topic/x          a topic read
SUBSCRIBE destination:/topic/internal   an internal topic
SUBSCRIBE destination:/queue/x          a queue read
SUBSCRIBE destination:/user/x/queue     a user queue
SUBSCRIBE destination:/user/admin/queue another's queue
SUBSCRIBE destination:/exchange/x       an exchange
SUBSCRIBE destination:/topic/*          a wildcard topic
SUBSCRIBE destination:/topic/>          a wildcard (activemq-style)
```

## The graphql-ws payload-set

```json
{"type":"connection_init","payload":{"authToken":"<x>"}}
{"type":"connection_init","payload":{"authorization":"Bearer <x>"}}
{"type":"subscribe","id":"1","payload":{"query":"subscription{flag}"}}
{"type":"subscribe","id":"1","payload":{"query":"subscription{user(id:1){secret}}}"}}
{"type":"subscribe","id":"1","payload":{"query":"subscription{messages{user{id,flag}}}}"}}
{"type":"start","id":"1","payload":{"query":"query{user(id:1){secret}}"}}     (legacy graphql-ws)
{"type":"subscribe","id":"1","payload":{"query":"mutation{admin{flag}}"}}     (a mutation)
{"type":"subscribe","id":"1","payload":{"query":"{__schema{types{name}}}"}}  (introspection)
```

## The MQTT topic payload-set

```
SUBSCRIBE {topic:"#", qos:0}              the all-topics wildcard
SUBSCRIBE {topic:"+", qos:0}              the single-level wildcard
SUBSCRIBE {topic:"device/+/status", qos:0} a multi-level filter
SUBSCRIBE {topic:"internal/#", qos:0}      an internal subtree
SUBSCRIBE {topic:"user/<other>/+", qos:0}  another's subtree
PUBLISH {topic:"internal/x", payload:...}  a restricted-topic write
PUBLISH {topic:"$SYS/x", payload:...}      the $SYS system topic
```

## The sub-protocol payload-set

```
Sec-WebSocket-Protocol: json
Sec-WebSocket-Protocol: graphql-ws
Sec-WebSocket-Protocol: graphql-transport-ws
Sec-WebSocket-Protocol: stomp
Sec-WebSocket-Protocol: v10.stomp
Sec-WebSocket-Protocol: v11.stomp
Sec-WebSocket-Protocol: v12.stomp
Sec-WebSocket-Protocol: mqtt
Sec-WebSocket-Protocol: mqttv3.1
Sec-WebSocket-Protocol: wamp.2.json
Sec-WebSocket-Protocol: ocpp1.6
Sec-WebSocket-Protocol: chat
Sec-WebSocket-Protocol: superchat
```

## The auth-frame payload-set (the first-frame tokens)

```json
{"type":"auth","token":"<x>"}
{"type":"auth","token":null}
{"type":"auth","token":""}
{"type":"login","user":"admin","pass":"x"}
{"type":"connection_init","payload":{"token":"<x>"}}
{"auth":"<x>"}                            {"token":"<x>"}
{"action":"auth","token":"<x>"}           {"action":"login","token":"<x>"}
40{"token":"<x>"}                         40{"auth":"<x>"}
CONNECT\nlogin:admin\npasscode:x\n\n^@
```

## The reconnect/resume payload-set

```json
{"type":"resume","session_id":"<old>"}
{"reconnect":true,"session_id":"<old>"}
{"action":"resume","token":"<old-token>"}
{"lastEventId":"-1"}                       {"lastEventId":"0"}
{"seq":0}                                  {"offset":0}
{"fromSeq":0}                              {"fromOffset":0}
{"action":"history","from":0,"to":1000}
/socket.io/?EIO=4&transport=websocket&sid=<old-sid>
```

## The history/backlog payload-set

```json
{"action":"history","room":"x"}
{"action":"history","room":"<other>","limit":1000}
{"action":"backlog","channel":"<other>"}
{"action":"replay","from":0,"to":1000}
{"action":"fetch","since":"<old-ts>"}
{"action":"read","id":"<x>","include_history":true}
{"action":"scroll","channel":"<other>","offset":0}
```

## The write-side payload-set

```json
{"action":"broadcast","text":"x"}          {"action":"announce","msg":"x"}
{"action":"emit-all","data":{...}}          {"action":"send_all","data":{...}}
{"action":"set","key":"x","value":"y"}      {"action":"config","key":"x","value":"y"}
{"action":"transfer","from":"<x>","to":"me","amount":N}
{"action":"update","id":"<other>","field":"x"}
{"action":"delete","id":"<other>"}          {"action":"remove","id":"<other>"}
{"action":"create","obj":{...}}             {"action":"insert","doc":{...}}
```
