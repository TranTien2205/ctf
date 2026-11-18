# The boundary — PP vs the classes it gets confused with

`web-prototype-pollution` sits between mass-assignment, nosqli,
deserialization, and config-injection. The tests that separate
them — because the wrong class burns a budget on the wrong probes.

---

## 1. PP vs mass-assignment — own-prop vs shared-root

```js
// mass-assignment: the write lands on YOUR object
{"isAdmin": true}                    → obj.isAdmin === true (own)
// PP: the write lands on the SHARED root
{"__proto__": {"isAdmin": true}}     → Object.prototype.isAdmin
                                        ({}).isAdmin === true
```

The discriminator: the fresh-object oracle. `({}).isAdmin` —
mass-assignment never touches a NEW object; PP does. And the
ledger calls them different bug classes — the confusable-pair
field in `knowledge/bug-classes.json` lists them adjacent because
the request shape is identical modulo the `__proto__` wrapper.

Test: send `{"isAdmin":true}` — if it works, mass-assignment; if
the same intent needs `__proto__`, PP.

## 2. PP vs nosqli — the operator boundary

```js
// nosqli: the value is an OPERATOR DOCUMENT reaching a query
{"username": {"$ne": null}}          → a query filter object
// PP: the value is a KEY PATH reaching a merge/setter
{"__proto__": {"x": 1}}              → a merge into a live object
{"$rename": {"a": "__proto__.m"}}    → the path-OPERATOR boundary —
                                       $-ops on PATHS, not values
```

`$rename`/`$set` on `__proto__.x` paths is where they overlap — a
nosqli carrier carrying a PP path. The discriminator: the nosqli
operator injects into the QUERY's semantics (`$ne`/`$gt`/`$where`);
the PP write changes the OBJECT GRAPH's shared state. A `$rename`
to `__proto__.x` is PP; a `$ne:null` is nosqli.

## 3. PP vs deserialization — object-shape vs code-shape

```python
# deserialization: the blob IS code/objects — pickle/marshal/serialize
pickle.loads(attacker_blob)          → executes on unpack
# PP: the blob is PLAIN data — JSON/qs — merged into a live object
merge(cfg, json.loads(attacker_json))  → writes keys; no code on unpack
```

The blob types decide: a `pickle`/`serialize`/`ObjectInputStream`/
`yaml.load` carrier is deserialization; a `JSON`/`qs`/`form` carrier
merged into live objects is PP. The payoffs differ too — deser
execs ON load; PP execs when a later read hits the polluted name.

## 4. PP vs config-injection / business-logic

```js
// config-injection: the app reads YOUR config value directly
{"settings": {"debug": true}}         → cfg.debug === true (own)
// PP: the app reads an UNDECLARED property that falls back to
// your prototype write
{"settings": {"__proto__": {"debug": true}}}  → ({}).debug === true
```

The overlap: both can set `debug`. The distinguisher is WHERE the
write lands and WHO reads it — config-injection is a deliberate
option the app accepts; PP is an undeclared fallback the app never
intended to read from you.

## 5. PP vs SSTI — which writes the template's input

```js
// SSTI: the template STRING is attacker-controlled
render("{{" + attacker + "}}")          → the payload is template syntax
// PP->template: the template OPTIONS are attacker-inherited
render("{{name}}", opts)                → opts.outputFunctionName is
                                          yours via the proto chain
```

Both reach template-engine code-exec — the carrier differs. SSTI
injects into the template source; PP injects into the options object
the compiler reads. The same `outputFunctionName` gadget can be
reached either way — PP is the route when the template string is
fixed but the options object merges attacker data.

## 6. PP vs client-side clobbering — the injection type

```js
// PP client-side: a JSON merge in the browser writes Object.prototype
merge(cfg, JSON.parse(location.hash.slice(1)))
// clobbering: injected HTML puts an element where a lookup expects a value
<form name=cfg><input name=api value=...>
```

Same "hijack a lookup" family; different injection — JSON-object
merge vs named-element shadowing. `dom-clobbering-deep.md` covers
the twin; the classifier routes by whether the attacker controls a
merged OBJECT (PP) or injected MARKUP (clobber).

## 7. PP vs Python class-pollution — same class, different graph

```python
# Python's shared roots are many — a class, __globals__, builtins —
# the vocabulary differs but the class is the same:
setattr(obj.__class__, 'x', v)         # class pollution
func.__globals__['SECRET'] = 'x'       # module-global pollution
```

In-tree both live under `web-prototype-pollution` — the class card
covers both because the mechanism (write-to-shared-root → fallback-
read) is identical.

## 8. PP vs prototype-CHIAN injection (different thing)

`Object.setPrototypeOf(obj, evil)` — replacing an object's prototype
rather than writing to the shared one. A related primitive but not
the class: the pollution write changes the ROOT's properties;
setPrototypeOf changes ONE object's parent. The merge-shape `{"a":
{"__proto__": evil}}` where the merge assigns `a.__proto__ = evil`
IS setPrototypeOf on `a` — a distinct write that gives `a` a custom
proto — still PP-family if `evil`'s properties get read through `a`.

## 9. The routing decisions

```text
the write is to MY object's own property        → web-mass-assignment
the write is to a shared root via a key path    → web-prototype-pollution
the blob is code/objects (pickle/serialize)     → web-deserialization
the operator injects into a QUERY filter        → web-nosqli
the injected thing is markup/named elements     → dom-clobber / xss
the template SOURCE is attacker-controlled      → web-ssti
the template OPTIONS inherit attacker data      → web-prototype-pollution
```

## 10. The confusable-class ledger note

```bash
python3 tools/state.py <chal> --hypothesis \
  "pp-vs-massassign: fresh-object oracle decides — ({}) reads the write?"
```
