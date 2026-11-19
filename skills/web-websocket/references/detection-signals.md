# Detection signals — every observable, its confidence, its class

## The endpoint signals — high-confidence ws

| Signal | The match | Confidence |
|---|---|---|
| `new WebSocket("wss?://...")` | the bundle | high — a ws endpoint |
| `Upgrade: websocket`/`101`/`Sec-WebSocket-*` | traffic | high |
| `io.connect`/`io(`/`socket.io`/`engine.io` | the bundle | high — Socket.IO |
| `SockJS(`/`new SockJS` | the bundle | high — SockJS |
| `Stomp.over`/`stompClient`/`stomp` | the bundle | high — STOMP |
| `Pusher(`/`pusher`/`Ably.Realtime`/`ably` | the bundle | high — a pub/sub |
| `createClient`/`graphql-ws`/`graphql-transport-ws` | the bundle | high — graphql-ws |
| `ws://`/`wss://` literal | the bundle/source-map | high |
| `?token=`/`?jwt=`/`?auth=`/`?key=`/`?session=` on a ws URL | the bundle | high — a credential |

## The live-feature signals — medium-confidence ws

| Signal | The match | Confidence |
|---|---|---|
| a live chat/DM/comment | the UI | medium |
| a presence/online/typing indicator | the UI | medium |
| a live notification/toast/feed | the UI | medium |
| a collaborative doc/editor | the UI | medium |
| a live dashboard/metrics/stock | the UI | medium |
| a game/lobby/lobby-state | the UI | medium |
| a typing/read-receipt | the UI | medium |

## The auth signals

| Signal | The match | Confidence |
|---|---|---|
| `Cookie:`/`session`/`sid` on the upgrade | the handshake | high — a binding |
| `Authorization:`/`Bearer`/`token` | the handshake | high |
| `?token=`/`?jwt=`/`?key=` | the URL | high — a URL-credential |
| `40{"token"}`/`{"type":"auth"}`/`connection_init` | the first frame | high — a frame-auth |
| no auth at all | the handshake | high — an unauth channel |

## The schema signals — the field names

| Signal | The match | Confidence |
|---|---|---|
| `"action":`/`"type":`/`"event":`/`"cmd":` | the bundle | high — a dispatch field |
| `"id":`/`"doc":`/`"room":`/`"channel":` | the bundle | high — an object field |
| `"user_id":`/`"from":`/`"to":`/`"sender":` | the bundle | high — an identity field |
| `"role":`/`"perm":`/`"is_admin":`/`"scope":` | the bundle | high — a grant field |
| `"q":`/`"filter":`/`"where":`/`"order":` | the bundle | high — a query field |
| `"file":`/`"path":`/`"url":`/`"data":` | the bundle | high — a sink field |
| `"token":`/`"auth":`/`"session_id":` | the bundle | high — an auth field |
| `"subscribe":`/`"join":`/`"watch":` | the bundle | high — a membership field |

## The reply-shape signals — the oracle vocabulary

| Reply | The signal | Confidence |
|---|---|---|
| `{"id":"<other>","data":...}` | another's object | oracle — IDOR |
| `{"flag":...}`/`{"admin":...}` | a privileged reply | oracle — dispatch |
| `49`/`7*7` evaluated | an eval | oracle — inject |
| `{"error":"forbidden"}`/`"unauthorized"` | a real rejection | uniform |
| `{"error":"unknown action"}` | a guessed name | weak-neg |
| `pong`/`ok`/`echo` | surface | not a finding |
| `101`/`Set-Cookie`/`Sec-WebSocket-Accept` | the handshake | surface |

## The class-route signals — the confusables

| Signal | The class |
|---|---|
| a `subscription`/`query` inside the frame | `web-graphql` |
| a serialized-object/`O:`/`rO0`/pickle frame | `web-deserialization` |
| a `?token=`/`?jwt=` | `web-auth-session`/`web-info-disclosure` |
| a `__proto__`/`constructor` key | `web-prototype-pollution` |
| a `{$ne}`/`{$where}`/`{$gt}` | `web-nosqli` |
| a `' OR`/`UNION`/`SLEEP` | `web-sqli` |

## The signal-record

`signal: <the observable>: <the confidence>: <the class/route>` — each
observable carries a confidence; the high-confidence ones drive the
first probes.
