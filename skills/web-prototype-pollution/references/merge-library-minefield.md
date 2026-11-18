# Merge-library minefield — per-library vulnerability map

Every JS merge helper has its own `__proto__` history. This file maps
library → vulnerable versions → the exact payload shape → the fix, so
a lockfile or a vendored bundle tells you immediately which payload
to send.

---

## 1. The big ones

| Library | Vulnerable range | Payload | Fix |
|---|---|---|---|
| `lodash` `_.merge`, `_.defaultsDeep`, `_.mergeWith` | < 4.17.21 | `{"__proto__":{"x":1}}` or `{"constructor":{"prototype":{"x":1}}}` | skips `__proto__`,`constructor`,`prototype` segments |
| `lodash` `_.zipObjectDeep`, `_.set`, `_.setWith` | < 4.17.16 | `_.set(obj,"__proto__.x",1)` via API | same |
| `merge` (npm `merge`) | < 2.1.1 | `merge(a, {"__proto__":{...}})` | segment blacklist |
| `merge-deep` | < 3.0.3 | same | same |
| `deep-extend` | < 0.6.0 | same | same |
| `defaults-deep` | < 0.2.4 | same | same |
| `merge-options` | < 3.0.4 | same | same |
| `extend` (npm, port of jQuery extend) | unpatched in old pins | `extend(true, {}, {"__proto__":{...}})` | still shipped in vendored code |
| `jquery` `$.extend(true,...)` | < 3.4.0 | `$.extend(true,{},JSON.parse(x))` | `__proto__` key filtered |
| `node-extend` | < 0.2.1 | same | abandoned — still everywhere |
| `mout` `deepFillIn`/`deepMixIn` | < 1.2.3 | same | blacklist |
| `just-extend` | < 4.0.2 | same | patched |
| `dset` | < 3.1.4 | `dset(obj,"__proto__.x",v)` | segment check |
| `object-path` | < 0.11.8 | `set(obj,"__proto__.x",v)` | same |
| `object-path-set` | < 1.1.3 | same | same |
| `set-value` | < 3.0.1 | same | same |
| `union-value` | < 1.0.1 | same | same |
| `assign-deep` | < 0.4.8 | same | same |
| `deep-object-diff` | detail-depend | same class | — |
| `js-data` merges | historical | same class | — |
| `dot-object` | < 2.1.5 | `object.__proto__.x` path | same |
| `plain-object-merge` | < 1.0.1 | same | same |
| `immer` (drafts) | < 9.0.6 | `draft.__proto__.x` | own-property only |
| `electron-store`/`conf` | version-dependent | `set("__proto__.x",v)` | — |
| `safe-obj`, `striing`, `pathval`, `deep-set` | various old | same class | check version |
| `minimist` (argv) | < 1.2.6 | `--__proto__.x=1` parse → proto KEY | filtered |
| `yargs-parser` | < 18.1.2 | same | filtered |
| `ini` parser | < 1.3.6 | `[__proto__]\nx=1` | filtered |
| `ajv` merge in old drafts | version-dependent | `__proto__` in schema | — |
| `typeorm`/`sequelize` update helpers | instance-dependent | `instance.update({__proto__:...})` | per-version |
| `mongoose` `doc.set` | version-dependent | `doc.set("__proto__.x",1)` | strict mode |
| `amanda`, `tv4` validators | schema merges | `__proto__` in schema | — |

## 2. The version-check shortcut

```bash
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
```

`gadget_lookup` is the version-aware recall — it reads the real
pinned versions and names the vulnerable merge before you write a
payload. A `package-lock`/`yarn.lock`/`pnpm-lock.yaml` in the handout
is the ground truth; `npm ls`-style ranges are not.

## 3. Reading the library off the bundle

When source isn't supplied, the minified merge is still findable —
`tools/web/bundle_miner.py` recovers sources; the merge helpers carry
fingerprint strings:

```js
// lodash merge
"Func.prototype")                       // the mergeWith path
// merge npm
"descriptor(s)" in source
// jquery extend signature
typeof copy === "object" || jQuery.isFunction(copy)
// deepmerge — the SAFE one (its option tests appear in source)
"isMergeableObject"
```

The `deepmerge`/`Object.assign`/`{...}` trio are NOT sinks — they copy
own enumerable properties only and drop `__proto__` keys as data.
Finding them means this merge site is closed; move carrier, not
payload.

## 4. The wrapper-level difference

The SAME library behaves differently per call:

```js
_.merge(a, b)                    — recursive, the sink
_.extend(a, b) / _.assign(a, b)  — SHALLOW, __proto__ lands as data
_.defaultsDeep(a, b)             — recursive with "first wins" — sink
_.cloneDeep(x)                   — copies own props — safe path
_.set(o, p, v)                   — path-setter — sink for dotted paths
_.zipObjectDeep(paths, vals)     — path bulk-set — sink
```

`_.extend`/`_.assign`/`Object.assign` are the common false positives:
the response echoes `__proto__` (it is an own-property of the merged
object now) but NOTHING inherits from it. The fresh-object readback
kills the false positive in one request.

## 5. Nested-lib chains

The merge function the app uses is often itself a wrapper:

- `nconf`/`config` loaders wrap `merge`/`lodash`
- `mongoose` `doc.set` wraps its own deep-set
- `express`/`body-parser` qs parsing builds the nested object the
  merge consumes — `app.set('query parser', 'extended')` enables it
- `helmet`/`cors`/session middleware merge option objects — the
  pollution lands inside a MIDDLEWARE options object, reachable when
  the middleware is re-initialized

## 6. The vendored copy trap

`node_modules` pins lie when the app vendors/bundles: a webpack
bundle, a `vendor.js`, a copied `utils/merge.js` in `lib/`. The
vendored copy ignores the lockfile's version. Find it by the
fingerprint strings, or by the fact the merge exists at all —
`grep -rn "function merge" lib/ utils/` in white-box.

## 7. The `for..in` no-guard idiom

The most common hand-rolled sink:

```js
for (var k in src) dest[k] = src[k]              // copies __proto__ as key
for (var k in src) { if (src.hasOwnProperty(k)) dest[k] = src[k] }
//    ^ hasOwnProperty DOESN'T stop __proto__ — it IS an own prop of src
for (const k of Object.keys(src)) dest[k] = src[k]  // safe — __proto__ not enumerable-own
```

`hasOwnProperty` on the SOURCE does not save it — `__proto__` appears
as an own property of the parsed `src` object (JSON.parse creates it
as an own property, not the prototype link). The discrimination is on
the DESTINATION: `dest[k]` where `k === '__proto__'` triggers the
setter.

## 8. The `JSON.parse` nuance that changes everything

`JSON.parse('{"__proto__":1}')` creates an object whose OWN property
`__proto__` is `1` — the setter does NOT fire on parse. The pollution
fires only when a merge later ASSIGNS that key to another object via
`dest.__proto__ = x` (the setter) or `dest["__proto__"] = x` (the
bracket-write, which also hits the setter on plain objects).

Consequence: `JSON.parse` is never the sink; the merge downstream of
it is. A challenge that parses but never merges is closed — find the
merge or move on.

## 9. The Map/Set/null-prototype defenses

- `new Map()` + `map.set(k,v)` — no prototype; `__proto__` is just a
  map key.
- `Object.create(null)` targets — same.
- `Object.freeze(Object.prototype)` — the write throws (strict) or
  no-ops.
- `Object.preventExtensions` on the target.
- `schema`-validated input (ajv/zod/joi) that drops unknown keys —
  `__proto__` is unknown and dropped.

Each is a REAL denial — record which one the response showed.
