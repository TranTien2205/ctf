# Denied conditions — when the NoSQLi can't work

## The value is stringified — `String(req.body.user)`

```javascript
User.findOne({username: String(req.body.user)})
```

`String(req.body.user)` — `{$ne: null}` → `"[object Object]"` — a
literal string — the object is stringified — `denies`.

## The `typeof` check — `typeof req.body.user !== 'string'`

```javascript
if (typeof req.body.user !== 'string') return 400;
```

A type-check — the object is rejected — `denies`.

## The `sanitizeFilter` — the `$`-strip

```javascript
const filter = sanitizeFilter(req.body)
```

`sanitizeFilter` strips `$`-keys — the object becomes scalar —
`filter-bypass.md` — denies the `$`-path, try `.`-key or nested-depth.

## The `express-mongo-sanitize` — `$` + `.` stripped

```javascript
app.use(mongoSanitize())
```

Strips `$`-keys AND `.`-keys — the `.`-key carriers die too — a
deeper-block — `filter-bypass.md`.

## The whitelist — only named operators

```javascript
const allowed = ['$eq', '$in'];
const filter = pick(req.body, allowed);
```

The whitelist — `denies` the non-`$eq`/`$in` operators — `operators.md`
— the full list; the bypass is an operator the whitelist missed.

## The `qs` `extended: false` — the flat parser

```javascript
app.use(express.urlencoded({extended: false}))
```

`extended: false` → `querystring` parser — `user[$ne]=x` stays a
literal string-key — no nesting — `denies` the qs-carrier.

## The `qs` `depth`/`parameterLimit` — the depth-cap

`qs`'s `depth` (default 5) / `parameterLimit` (default 1000) — a deeper
nest is dropped — `injection-points.md`.

## The `qs` `allowPrototypes: false` — the proto-block

`qs` blocks `__proto__`/`constructor`/`prototype` by default —
`filter-bypass.md` — that's `web-prototype-pollution`, not here.

## The `enableJs: false` — the `$where`/`$function`/`$accumulator` dead

`MongoServerError: $where is not allowed` — `enableJs` off — denies
the JS-paths; `$expr` still works — `operators-js.md`.

## The `Content-Type` rejection — `application/json` not parsed

The app only accepts `form-urlencoded` — `{"$ne": null}` is a string —
`injection-points.md` — the carrier decides.

## The `findOne` vs `find` — the cardinality

`find` returns all — `findOne` returns first — a `find` + `$ne`
returns every doc — `mongo-specific.md`.

## The `bcrypt.compare` type-error — the pass-object throws

`bcrypt.compare({$ne: null}, hash)` throws — the bypass is blocked —
`auth-bypass.md` — use a different vector or a non-hashed field.

## The `unionWith`/`$lookup` — the collection must exist

`$unionWith: "flag"` — the collection must exist — `aggregation.md` —
a non-existent collection returns empty, not error — `inconclusive`.

## The `$out`/`$merge` — write-permission

`$out`/`$merge` need write-permission — a read-only role denies them —
`update-injection.md`.

## The `$where` — `this` is the document

`$where`'s `this` is the doc — `this.field` — a missing field →
`undefined` — `operators-js.md`.
