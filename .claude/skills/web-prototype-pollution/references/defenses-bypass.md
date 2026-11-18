# Defenses and their bypasses — what blocks the write and what doesn't

The real-world guard inventory, and which bypass each guard leaves.

---

## 1. The guards at the WRITE (merge-side)

| Guard | What it does | The bypass |
|---|---|---|
| `Object.keys(src)` + filter `__proto__`/`constructor`/`prototype` | name-blacklist | `constructor.prototype` if only `__proto__` blocked; escaped spellings `\u005f`; nested keys deeper than the filter's check |
| `src.hasOwnProperty(k)` skip | only own enumerable copied | **doesn't help** — `__proto__` in `{"__proto__":x}` IS an own property of src — the guard passes it through! |
| `if (k === '__proto__') continue` | single-name block | `constructor.prototype`, `proto`, `prototype`-under-function, `__class__` in py |
| `Object.freeze(Object.prototype)` | frozen root | `Object.seal`/`preventExtensions` stop own-adds; freeze blocks writes to the ROOT — bypass via a class-instance prototype (`C.prototype`) or a non-frozen intermediate |
| `Object.create(null)` target | null-proto object | the merge target is immune — but the SOURCE's `__proto__` still assigns into the target's (nonexistent) proto — dead end; look for a DIFFERENT merge target |
| `Object.seal(target)`/`preventExtensions` | no new own keys | proto reads still work — pollute a name that ALREADY exists as an own key the sink reads; or hit a different object |
| `defineProperty` merge | accessor-defined writes | `dest.__proto__` via `defineProperty` does NOT hit the setter — own literal key — PP dead; but `dest.constructor.prototype` still walks the READ chain to Object.prototype — the write lands there! |
| `structuredClone`/`JSON`-round-trip | own-props copy | PP invisible — the copy is clean; but the ORIGINAL object still carries the write if a read hits it before the copy |
| `Map`/`Set`/`WeakMap` stores | no proto chain | immune — look for the plain-object path elsewhere |

The most common guard mistake: `hasOwnProperty` on the SOURCE —
it filters "inherited keys of the source" which is the wrong
direction. `{"__proto__":{...}}` parses to an object where
`__proto__` is an OWN property — the guard lets it through.

## 2. The guards at the PARSE

| Guard | Bypass |
|---|---|
| `qs.allowPrototypes: true` (drop `__proto__` in qs) | `constructor[prototype]`, JSON body carrier, path-API, `proto` app-alias |
| `JSON.parse` + schema-validation stripping unknown keys | `__proto__` is a real key — passes unless the schema enumerates; nested keys often unvalidated |
| key-whitelist middleware | the merge reads the ORIGINAL body, not the whitelisted copy — or a nested object's keys aren't whitelisted |
| `express.json({strict:true})` | still parses `{"__proto__":x}` — strict is about top-level type |
| body-size limits | small marker payloads unaffected |

## 3. The guards at the READ (sink-side)

| Guard | Bypass |
|---|---|
| `hasOwnProperty` on the sink object | PP dead for that sink — find a different read |
| `Object.keys`/`entries`/`getOwnPropertyNames` iteration | same — PP invisible |
| `in`-check on the sink | PP VISIBLE — `in` walks the chain |
| `Map.get`/`Set.has` | immune |
| `structuredClone` before the read | invisible in the clone |
| the sink reads a CLASS-instance attr | the class's own field declaration is an own-prop — but an UNDECLARED attr read still inherits |
| the sink object's proto is `Object.create(null)` | immune for that object — but `constructor.prototype` write hits Object.prototype which the null-proto object doesn't inherit — wait, null-proto has NO proto — dead for it; find a different read object |

## 4. The guards at the FRAMEWORK

| Guard | Bypass |
|---|---|
| `lodash` 4.17.21+ patched merge | `constructor.prototype` alias survives on some code paths; `_.set`/`zipObjectDeep`/`template` still have paths; a DIFFERENT merge function (mergeDeep/defaultsDeep variants) may be unpatched |
| mongoose strict-schema | `$rename`/`$set` path operators still resolve `__proto__` on vulnerable driver versions |
| `express 5` hardened qs | JSON body carrier unaffected |
| `Object.freeze(Object.prototype)` in a security module | freeze the root — but `Array.prototype`, `Function.prototype`, class prototypes are separate roots — pollute those |
| Deno/Bun different object model | `__proto__` semantics similar; check the runtime |

## 5. The "the filter only checked the first key" pattern

```js
// the classic half-guard
function clean(o) {
  for (const k of Object.keys(o)) {
    if (k === '__proto__') delete o[k];
    // no recursion — nested __proto__ survives!
  }
}
clean({a: {__proto__: {m: 1}}})   // 'a' is fine — the nest lives
{"a": {"__proto__": {"m": 1}}}    // → merge walks into a, writes m
```

A non-recursive cleaner misses any `__proto__` deeper than level 1 —
always probe `{"a":{"__proto__":{...}}}` when flat `{"__proto__":...}`
rejects.

## 6. The "key renamed before merge" pattern

```js
// middleware that renames reserved keys
body.__proto__ = body.safe__proto__;  // a broken fix — the ASSIGNMENT
                                      // itself hits the setter!
```

An app that "sanitizes" by MOVING `__proto__` to another key often
pollutes itself doing it — the read `body.__proto__` returns the
proto (not an own key), and the assignment `body.x = body.__proto__`
reads the proto object.

## 7. The "deep-freeze" guard

```js
deepFreeze(Object.prototype)   // freezes root + all nested
// bypass: a DIFFERENT root — Array.prototype, Function.prototype,
// a class's prototype, a Map's prototype — freeze only covers what
// it was applied to
{"a": {"__proto__": ...}}        // still lands if a DIFFERENT merge
                                 // target's proto isn't frozen
```

## 8. The "immutable options" pattern

```js
const opts = Object.freeze({x:1});
const merged = Object.assign({}, opts, req.body);   // merged is fresh
// bypass: the FRESH object still has Object.prototype — pollute a
// name it doesn't define; the freeze blocked own-writes to opts,
// not proto reads on the merged copy
```

## 9. The "schema validation" guard

```js
ajv.validate(schema, body)  // strips unknown props when
                            // additionalProperties:false
// bypass: __proto__ is a real own key — passes as 'additional';
// nested objects often additionalProperties:true — nest inside
// an allowed container key
{"profile": {"__proto__": {"m": 1}}}   // 'profile' allowed, the
                                      // __proto__ inside unvalidated
```

## 10. The "the guard is on the wrong layer" family

```text
WAF checks for '__proto__' in the URL    → use the JSON body
WAF checks the body string               → Unicode-escape the key
app checks keys before parse             → check ordering vs parse
app checks keys after parse, before merge → depth-1 only, nest it
app checks the merge target              → the check sees dest, not src
```

Each guard is a layer; the bypass is finding the layer it doesn't
cover. The probe cost is one request per hypothesis.

## 11. When nothing bypasses — the honest falsifier

```text
- the merge is frozen-sealed-null-proto AND
- every sink reads own-only AND
- every carrier is schema-stripped AND
- every key alias is name-blocked recursively
→ record refutes on each arm; park; the site is not exploitable
```

A guarded site is a falsifiable result — not a failure to keep
trying. The budget rule: after ~5 refuted arms across distinct
mechanism layers, park.
