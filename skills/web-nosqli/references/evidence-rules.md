# Evidence rules — what counts as a NoSQLi finding

## The bar — the object-filter reached the query

The clean proof: the OBJECT-shaped value (`{"$ne": null}`) produces a
DIFFERENT result than the scalar (`"x"`) — the object reached `find()`.

## The confirms grade — the required signal

- control-scalar fails + probe-object succeeds → the object-filter
  reached the query → `confirms`
- `{"user": {"$ne": null}, "pass": {"$ne": null}}` logs in → `confirms`
- `{"pass": {"$regex": "^a"}}` produces a true/false delta → `confirms`
- `{"flag": {"$regex": "^flag\\{"}}` matches → `confirms`

## The inconclusive grade — what does NOT prove NoSQLi

- a successful login with a normal scalar — a valid credential, not
  injection
- an error naming `CastError`/`BSONError` — the object reached the
  driver but may have been rejected — `inconclusive` until the object
  produces a DIFFERENT result
- a `200` on a non-auth endpoint — a normal response
- a 302 — a redirect
- a timeout — `inconclusive` unless 3x + absent-on-control

## The verbatim excerpt — the `--evidence` requirement

```bash
python3 tools/hooks.py post-probe <name> --request "..." \
  --verdict confirms --evidence-kind class --class web-nosqli \
  --hypothesis-id h1 --evidence "<the verbatim excerpt>" \
  --response "<the raw response bytes>"
```

`--evidence` must be a substring of `--response` — `evidence-rules.md`.

## The "which user" — the `findOne` first-doc

`findOne({user: {$ne: null}})` returns the FIRST doc — which user did
you get? — the response's user-field names it — `auth-bypass.md`.

## The auth-bypass ≠ admin — the first-doc may be a low-user

The first doc isn't always `admin` — it's whoever sorts first — the
`{"user": "admin", "pass": {"$ne": null}}` targets the known user —
`auth-bypass.md`.

## The mass-write — the `updateMany` + `$ne`

```javascript
db.users.updateMany({user: {$ne: null}}, {$set: {role: "admin"}})
```

A mass-update — the blast-radius — record the count BEFORE firing —
`update-injection.md`.

## The negative-results — the `denies` shapes

- `{"$ne": null}` returns the same as scalar → the value is stringified →
  denies
- `CastError`/`BSONError` without a differential → the object was
  rejected → denies
- `$where` returns `not allowed` → `enableJs` off → denies `$where`,
  not the class
- `sanitizeFilter` strips `$`-keys → the object is cleaned → denies
  the `$`-operator path, try the `.`-key or nested-depth

## The `find`-vs-`findOne` — the all-vs-first

`find({user: {$ne: null}})` returns ALL — `findOne` returns first —
the response's cardinality — `mongo-specific.md`.

## The chain card — the UnEarthly Shop

`knowledge/chains/*unearthly*` — the verified chain — the `$unionWith`
aggregation — `aggregation.md`.
