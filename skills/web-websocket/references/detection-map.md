# Detection map — the observable → the check → the file

## The endpoint-signal map

| The observed | The check | The file |
|---|---|---|
| `new WebSocket("wss?://")` in the bundle | the endpoint is ws | `detection.md`/`detection-deep.md` |
| `Upgrade: websocket`/`101`/`Sec-WebSocket-*` | the traffic is ws | `detection-deep.md` |
| `io(`/`io.connect`/`socket.io`/`EIO=` | Socket.IO | `framing-protocols-deep.md` |
| `new SockJS`/`SockJS(`/`/info`/`a[...]` | SockJS | `framing-protocols-deep.md` |
| `Stomp.over`/`stompClient`/`CONNECT`/`SEND` | STOMP | `per-transport-deep.md` |
| `new Pusher`/`pusher-js`/`channel.bind` | Pusher | `per-transport-deep.md` |
| `new Ably.Realtime`/`ably`/`channel.subscribe` | Ably | `per-transport-deep.md` |
| `createClient`/`graphql-ws`/`graphql-transport-ws` | graphql-ws | `per-transport-deep.md`/`web-graphql` |
| `mqtt.connect`/`SUBSCRIBE`/`PUBLISH`/`#`/`+` | MQTT | `per-transport-deep.md` |
| a live chat/feed/doc/metric/lobby/notif UI | a probable ws | `per-surface.md` |

## The handshake-signal map

| The observed | The check | The file |
|---|---|---|
| `Cookie:`/`session`/`sid` on the upgrade | the cookie-binding | `handshake-side-deep.md`/`cswsh-deep.md` |
| `Authorization:`/`Bearer`/`token` | the bearer-binding | `handshake-side-deep.md` |
| `?token=`/`?jwt=`/`?key=`/`?auth=`/`?session=`/`?api_key=` | a credential-in-URL | `handshake-side-deep.md` |
| `Sec-WebSocket-Protocol: <x>` | a sub-protocol | `handshake-side-deep.md`/`per-transport-deep.md` |
| `Origin:` on the upgrade | the CSWSH surface | `cswsh-deep.md` |
| `{"type":"auth"}`/`40{"token"}`/`connection_init`/`CONNECT` | a first-frame auth | `handshake-side-deep.md` |
| `session_id`/`resume`/`reconnect`/`seq`/`lastEventId` | a resumption | `edge-cases-deep.md` |
| `Set-Cookie: SameSite=<x>` | the cookie-travels leg | `cswsh-deep.md` |

## The schema-signal map

| The observed | The check | The file |
|---|---|---|
| `"action":`/`"type":`/`"event":`/`"cmd":`/`"method":`/`"op":` | a dispatch field | `action-dispatch-deep.md` |
| `"id":`/`"doc":`/`"object":`/`"item":`/`"record":`/`"file":` | an object field | `message-idor-deep.md` |
| `"room":`/`"channel":`/`"conversation":`/`"topic":`/`"destination":`/`"namespace":` | a membership field | `message-idor-deep.md`/`per-channel.md` |
| `"user_id":`/`"uid":`/`"account":`/`"org":`/`"tenant":` | a principal field | `message-idor-deep.md` |
| `"from":`/`"sender":`/`"user":`/`"author":`/`"actor":` | an identity field | `message-side-deep.md` |
| `"role":`/`"perm":`/`"is_admin":`/`"scope":`/`"level":`/`"debug":`/`"internal":` | a grant field | `action-dispatch-deep.md` |
| `"q":`/`"search":`/`"query":`/`"filter":`/`"where":`/`"order":`/`"sort":` | a query field | `injection-in-frames-deep.md` |
| `"file":`/`"path":`/`"url":`/`"data":`/`"xml":`/`"host":`/`"cmd":`/`"obj":`/`"config":` | a sink field | `injection-in-frames-deep.md` |
| `"token":`/`"auth":`/`"jwt":`/`"session":`/`"session_id":`/`"resume":` | an auth/resume field | `handshake-side-deep.md`/`edge-cases-deep.md` |
| `"subscribe":`/`"join":`/`"watch":`/`"listen":`/`"follow":`/`"feed":` | a subscription field | `message-idor-deep.md`/`per-channel.md` |
| `"to":`/`"target":`/`"recipient":`/`"for_user":` | a write-routing field | `message-side-deep.md` |
| `"__proto__":`/`"constructor":`/`"prototype":` | a pollution field | `web-prototype-pollution` |

## The reply-signal map

| The reply | The verdict | The file |
|---|---|---|
| `{"id":"<other>","data":...}` | a message-IDOR | `message-idor-deep.md`/`web-idor` |
| `{"flag":...}`/`{"admin":...}`/`{"config":...}` | a dispatch gap | `action-dispatch-deep.md` |
| `{"role":"admin"}` accepted | a self-grant | `web-mass-assignment` |
| the frame acts-as-other | a spoof | `web-mass-assignment`/`web-auth-session` |
| `49`/`7*7` evaluated | an injection (ssti) | `web-ssti` |
| `' OR 1=1` returns rows | an injection (sqli) | `web-sqli` |
| `uid=0...`/`root:x:` | an injection (cmdi/lfi) | `web-command-injection`/`file-read-primitives` |
| a pushed feed | a subscription-IDOR | `web-idor` |
| a state-change | a write-side gap | `web-logic-flaw` |
| `{"error":"forbidden"}`/`"unauthorized"`/`403`/`1008` | `uniform` | `negative-results-deep.md` |
| `{"error":"unknown action"}`/`"invalid field"` | `weak-negative` | `negative-results-deep.md` |
| `{"error":"not found"}`/`"invalid"` | `weak-negative` | `negative-results-deep.md` |
| `{"error":"malformed"}`/`"bad request"` | a framing-error | `troubleshoot-deep.md` |
| silence/drop | a `gap` | `edge-cases-deep.md` |
| `500`/crash | a `candidate` differential | `troubleshoot-deep.md` |
| `pong`/`ok`/`echo`/`101`/`Set-Cookie` | `surface` | `negative-results-deep.md` |

## The class-route map

| The lead | The flag-closing class |
|---|---|
| CSWSH (the four legs) | `web-websocket`/`web-csrf` |
| an unauth channel | `web-websocket`/`web-info-disclosure` |
| a message-IDOR | `web-idor` |
| a dispatch gap | `web-auth-session`/`web-logic-flaw` |
| a self-grant/spoof | `web-mass-assignment`/`web-auth-session` |
| an injection | the payload's class |
| a token-in-URL | `web-auth-session`/`web-info-disclosure` |
| a subscription-IDOR | `web-idor` |
| a graphql-ws subscription | `web-graphql` |
| a protobuf field | `proto_decode` + the field class |

## The map-record

`map: <the observed> -> <the check> -> <the file>` — the observable maps
to the check + the depth file.
