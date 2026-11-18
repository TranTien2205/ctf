# Common mistakes — why the NoSQLi doesn't work

## The scalar-vs-object — `{"user": "x"}` vs `{"user": {"$ne": null}}`

The injection needs the OBJECT — a scalar-string is just a value —
the JSON `{"$ne": null}` or the qs `user[$ne]=x` is the object —
`injection-points.md`.

## The `Content-Type` — `application/json` required for `{"$ne": null}`

`{"$ne": null}` needs `application/json` — a `form-urlencoded` request
with `{"$ne": null}` is just a string — the carrier determines the
object — `injection-points.md`.

## The `user[$ne]` needs `qs` — not a raw-Express parser

`user[$ne]=x` needs `qs` (Express's `extended` parser) — `body-parser`'s
`simple` or a raw `querystring` parser doesn't nest — `injection-points.md`.

## The `bcrypt.compare` type-error — the object-pass throws

```javascript
bcrypt.compare(req.body.pass, user.hash)   — req.body.pass = {$ne: null} → throws
```

`bcrypt.compare` on an OBJECT throws — the bypass is blocked by the
type-check — `auth-bypass.md` — use `{"user": "admin", "pass": "x"}` +
a different vector, or a `{$regex}` on a non-hashed field.

## The `sanitizeFilter` — the `$`-strip

`mongoose.sanitizeFilter` strips `$`-keys — the operators are removed —
`filter-bypass.md` — the nested-depth or `.`-key carriers.

## The `enableJs` off — `$where` dead

`$where`/`$function`/`$accumulator`/`mapReduce` need `enableJs` — Atlas
and most modern configs disable it — use `$expr` — `operators-js.md`.

## The `findOne` first-doc — not always `admin`

`findOne({user: {$ne: null}})` returns the FIRST doc — the sort-order
determines which — `{"user": "admin", "pass": {"$ne": null}}` targets
the known user — `auth-bypass.md`.

## The `updateMany` blast-radius — `$ne` updates ALL

`updateMany({user: {$ne: null}}, ...)` — every doc — `evidence-rules.md`
— record the count first.

## The `__proto__` confusion — that's `web-prototype-pollution`

`a[__proto__][x]=y` — the `__proto__`/`constructor`/`prototype` keys are
POLLUTION, not NoSQLi — `skills/web-prototype-pollution/` — different class.

## The string-injection confusion — that's `web-sqli`

`' OR 1=1 --` inside a string — SQLi — `skills/web-sqli/` — the NoSQLi is
the object-filter, the SQLi is the string-query — `detection.md`.

## The timeout ≠ the desync

A timeout is `inconclusive` — a real object-filter produces a
DIFFERENT result — `evidence-rules.md`.

## The `200` on a non-auth endpoint ≠ injection

A `200` on `/search` is normal — the differential is the object-vs-scalar
— `detection.md`.

## The `--selftest` not run

`nosqli_probe.py --selftest` — `tooling.md`.
