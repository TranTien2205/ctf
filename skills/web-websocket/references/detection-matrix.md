# Detection matrix — the observable to the channel to the verdict

## The handshake matrix

| Observable | Check | A `101`+ | A `403`/`401`/drop |
|---|---|---|---|
| foreign `Origin` | Origin-enforce | CSWSH-candidate | check exists |
| `Cookie: session=` | auth-binding | binds the session | unauth'd |
| no cookie/token | unauth-open | unauth channel | authed |
| `?token=`/`?jwt=` | token-in-URL | credential-leak | — |
| `Sec-WebSocket-Protocol` | sub-protocol | alt-protocol | only intended |
| `Authorization`/custom | header-auth | header-binding | — |

## The message matrix — per field

| Field | Mutation | Oracle reply | Uniform reply |
|---|---|---|---|
| `id`/`doc`/`object` | `id:"victim"` | another's object | `forbidden`/`404` |
| `room`/`channel` | `room:"admin"` | the restricted feed | `forbidden` |
| `user_id`/`org`/`tenant` | `user_id:2` | another's record | `forbidden` |
| `to`/`target` | `to:"admin"` | a write to admin | `forbidden` |
| `action`/`type`/`cmd` | `action:"admin"` | a privileged reply | `unknown`/`forbidden` |
| `role`/`perm`/`is_admin` | `role:"admin"` | a self-grant accepted | ignored/`forbidden` |
| `from`/`sender` | `from:"victim"` | sent as victim | overwritten |
| `q`/`search`/`filter` | `q:"' OR 1=1"` | injected rows | raw/error |
| `name`/`text`/`tpl` | `name:"{{7*7}}"` | `49` evaluated | `{{7*7}}` raw |
| `file`/`path` | `file:"/flag"` | the file | `forbidden`/`404` |
| `url`/`fetch` | `url":"http://..."` | a server fetch | `forbidden` |
| `data`/`obj`/`xml` | `<ser/xxe>` | the eval/read | `parse-error` |
| `__proto__`/`constructor` | `__proto__.x` | a polluted obj | stripped |

## The framing matrix

| Transport | The envelope | A correct shape |
|---|---|---|
| raw WS | none | `{"action":"x"}` |
| Socket.IO | `42["e",d]` | `42["x",{...}]` |
| SockJS | `a["..."]` | `a["{\"x\":...}"]` |
| STOMP | `SEND dest:` | `SEND destination:/app/x` |
| graphql-ws | `{"type":"subscribe"}` | `{"type":"subscribe",...}` |
| MQTT | binary | `SUBSCRIBE`/`PUBLISH` |
| protobuf | binary | `proto_decode.py` |

## The verdict matrix

| Reply | Verdict |
|---|---|
| another's object/data | `oracle` — the cross-principal read |
| a privileged action's reply | `oracle` — the dispatch gap |
| `49`/`7*7` evaluated | `oracle` — the injection (payload class) |
| `{"error":"forbidden"}`/`"unauthorized"` | `uniform` — a real rejection |
| `{"error":"unknown action"}` | `weak-negative` — a guessed name |
| `pong`/`ok`/echo | `surface` — not a finding |
| silence/drop | `gap` — not a verdict |
| `500`/crash | `candidate` — a parser/branch |

## The coverage matrix

```
         origin  binding  token  subproto  idor  action  spoof  inject
/ws
/socket.io
/api/ws
```

Every cell `oracle`/`uniform`/`unmeasured`. A socket is closed only
when every cell is `uniform`.
