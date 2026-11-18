# Theory — why the object-filter is injectable

## The model — the driver takes an object, not a string

```javascript
User.findOne({username: req.body.user})
```

`req.body.user` — if it's a STRING `"admin"` → `findOne({username: "admin"})` —
an equality-filter. If it's an OBJECT `{$ne: null}` →
`findOne({username: {$ne: null}})` — an operator-filter — the driver's
type-coercion is the bug — `detection.md`.

## The query-language — the operators inside values

```javascript
{field: value}              — equality
{field: {$op: value}}       — operator-filter
{$op: [clauses]}            — logical
```

Mongo's query-language puts operators inside the VALUE — a
`{"field": {"$ne": null}}` — the value IS the filter — the injection
is structural — `operators.md`.

## The carrier — how the object survives

```javascript
req.body.user = {$ne: null}    — JSON body
req.body.user = {$ne: "x"}     — qs's user[$ne]=x
req.query.filter.user = ...    — qs's filter[user][$ne]=x
```

The object's path to `find()` — `injection-points.md`.

## The scalar-vs-object — the type-confusion

```javascript
req.body.user = "admin"      → findOne({username: "admin"})    — equality
req.body.user = {$ne: null}  → findOne({username: {$ne: null}}) — operator
```

The driver accepts either — no type-check — `detection.md`.

## The `$`-operator — the injection's marker

`$ne`, `$gt`, `$regex`, `$where`, `$expr`, `$exists`, `$in`, `$or`,
`$and`, `$not`, `$type`, `$size`, `$all`, `$elemMatch`, `$mod`,
`$text`, `$search`, `$comment` — `operators.md`.

## The `findOne`/`find` — the first-doc

`findOne` returns the FIRST match — the `$ne` lands on the first doc —
`mongo-specific.md`.

## The `aggregate` — the pipeline-array

`aggregate` takes an ARRAY of stages — `[{"$unionWith": "x"}]` —
`aggregation.md`.

## The update-operators — `$set`/`$unset`/`$inc`

`updateOne`/`updateMany`/`findOneAndUpdate` — the write-operators —
`update-injection.md`.

## The `enableJs` — the `$where` capability

`$where`/`$function`/`$accumulator`/`mapReduce` need `enableJs` —
`operators-js.md`.

## The `qs`-parser — the `user[$ne]=x` carrier

`qs.parse("user[$ne]=x")` → `{user: {$ne: "x"}}` — the qs-carrier —
`injection-points.md`.
