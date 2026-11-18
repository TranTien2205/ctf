# V8 / JS-engine semantics — the write mechanics, precisely

What actually happens at the engine level when `dest.__proto__ = x`
runs inside a merge — and which spellings hit the setter vs which
write a literal key.

---

## 1. The `__proto__` accessor — a setter on Object.prototype

```js
Object.getOwnPropertyDescriptor(Object.prototype, '__proto__')
// { get: f, set: f, enumerable: false, configurable: true }
```

`__proto__` is NOT a normal property — it's an accessor pair living
on `Object.prototype`. Every plain object inherits it. Reads go
through the getter; writes through the setter. The setter calls
`SetPrototype` — it REPLACES the object's prototype with the value.

## 2. Which writes hit the setter

```js
dest.__proto__ = x            // setter — pollution/reproto
dest["__proto__"] = x         // setter — bracket form same
dest.__proto__                // getter — reads the proto
Object.setPrototypeOf(dest,x) // the explicit form
Reflect.set(dest,'__proto__',x)// through Reflect — setter
Reflect.setPrototypeOf(dest,x)// the explicit reflect
with(dest){__proto__ = x}     // scope-assign — setter
```

## 3. Which writes DON'T hit the setter

```js
Object.defineProperty(dest,'__proto__',{value:x})
// creates an OWN property named '__proto__' — the setter bypassed;
// dest keeps its real proto; dest.__proto__ still reads the REAL
// proto, but dest has an own-key '__proto__' that's just a key.

Object.getOwnPropertyDescriptor(dest,'__proto__')
// after defineProperty — an own descriptor, not the accessor

Object.assign(dest, {__proto__: x})
// assign uses [[Get]] on src — src.__proto__ READS the proto of
// the LITERAL — wait: the literal {"__proto__":x} — the __proto__
// key on the LITERAL is ALSO the setter — the literal's proto
// becomes x. Then assign copies... nothing (proto isn't own).
// NET: assign(dest, {__proto__:x}) does NOTHING useful — the src
// literal's proto got set to x, and its own-keys are empty!

// the JSON.parse difference:
JSON.parse('{"__proto__":{"m":1}}')
// JSON.parse builds the object via a different path — the
// '__proto__' key is an OWN property with the object value —
// NOT the setter! A parsed object's __proto__ key is literal.
// THIS is why the merge payload works: JSON.parse produces
// {__proto__: {m:1}} as OWN data; merge then does
//   dest["__proto__"] = {m:1}   → setter → reproto dest
// the setter-fire happens at the MERGE's assignment, not parse.
```

The critical detail: `JSON.parse` creates a LITERAL own-key
`__proto__`; a hand-written `{"__proto__":x}` literal calls the
setter on the literal itself. That's why PP payloads work — the
parse preserves the key as data, and the merge's own assignment
`dest[k] = v` on `k="__proto__"` fires the setter on DEST.

## 4. `constructor` — a read-chain, not a setter

```js
dest.constructor              // === Object (via proto) — READ
dest.constructor.prototype    // === Object.prototype — READ
dest.constructor = x          // writes an OWN prop 'constructor'
                              // — shadows, doesn't retype
```

`{"constructor":{"prototype":{"m":1}}}` works differently: the
merge does `dest.constructor` (a READ — gets `Object`), then
`dest.constructor.prototype` (a READ — gets `Object.prototype`),
then `dest.constructor.prototype.m = 1` (a WRITE onto the shared
root). No setter involved — just a READ chain ending in a write.

## 5. `Object.create(null)` — the null-proto object

```js
const o = Object.create(null)
o.__proto__                   // undefined — no accessor inherited!
o.__proto__ = x               // own-key write (no setter exists)
o.constructor                 // undefined — no proto
```

A null-proto object has NO `__proto__` accessor — writes to it are
literal own-keys. A merge INTO a null-proto object is immune; a
merge whose SOURCE contains `__proto__` still writes the setter on
the (non-null) TARGET — the source's keys copy regardless.

## 6. `Object.freeze`/`seal`/`preventExtensions` on the target

```js
Object.freeze(dest)
dest.x = 1                    // silently fails (sloppy) / TypeError (strict)
dest.__proto__ = x            // the SETTER still fires? freeze blocks
                              // own-writes; the __proto__ setter is a
                              // proto-set — freeze blocks proto-
                              // changes? Object.freeze prevents
                              // [[SetPrototypeOf]]? — YES, frozen
                              // objects can't have their proto changed.
```

`Object.freeze` on the merge TARGET blocks the proto-swap; but the
write to `Object.prototype` ITSELF (via `constructor.prototype.x`)
happens on the shared root — freeze the TARGET doesn't protect the
ROOT unless `Object.prototype` is also frozen.

## 7. `Object.seal`/`preventExtensions` differences

```js
Object.seal(dest)             // no new props, existing writable
Object.preventExtensions(dest)// no new props, existing rewritable
// both block NEW own-keys; neither blocks proto-changes the way
// freeze does? — preventExtensions DOES block [[SetPrototypeOf]]?
// No: preventExtensions prevents ADDING properties but allows
// proto changes? Actually ES spec: [[PreventExtensions]] sets
// [[Extensible]]=false; [[SetPrototypeOf]] checks extensible —
// a non-extensible object CANNOT change its proto.
// → seal/preventExtensions DO block dest.__proto__=x
// → but constructor.prototype.x writes to the ROOT — unaffected
```

## 8. The `in`/`has`/`delete` semantics

```js
'x' in obj                    // chain-check — polluted visible
obj.hasOwnProperty('x')       // own-only — polluted invisible
delete obj.__proto__          // can't delete the accessor —
                              // it's on Object.prototype not obj
delete Object.prototype.x     // deletes YOUR polluted prop —
                              // the cleanup primitive
```

`delete Object.prototype.ppmarker` — the cleanup: a polluted own
property on the root can be deleted; the accessor `__proto__`
itself can't (it's on the root, non-enumerable).

## 9. Strict-mode vs sloppy differences

```js
// sloppy: silent fails on frozen/non-writable
// strict: TypeError on the same
// merges rarely run strict; a TypeError on write is a parse-level
// signal — "Cannot assign to read only property" means the write
// hit a non-writable own prop — a falsifier for that name
```

## 10. The `JSON.parse`/`structuredClone`/`postMessage` clones

```js
structuredClone(o)            // own enumerable data — proto NOT cloned
o2 = JSON.parse(JSON.stringify(o))  // same — the clone is clean
postMessage(o)                // structured-clone — same
```

Pollution never crosses a clone — the clone has a fresh proto —
but the write to the SHARED root persists; the CLONE's `({}).x`
read still sees it.

## 11. The `class`/`extends` proto shapes

```js
class C extends Base {}
C.prototype                   // C's prototype — a shared root!
C.__proto__                   // === Base — the class's own proto
new C().__proto__             // === C.prototype
new C().constructor           // === C
```

A merge that reaches `C.prototype` via `instance.constructor.prototype`
writes on C's proto — every `new C()` inherits. Class-attr pollution.

## 12. The `Proxy` interaction

```js
new Proxy({}, {set: (t,k,v)=>{t[k]=v}})   // the set-trap forwards
                                          // to the target — k=
                                          // '__proto__' hits the
                                          // TARGET's setter — PP
                                          // still lands!
```

A proxy-wrapped merge target doesn't protect — the trap forwards
`__proto__` writes through to the target's setter unless the trap
explicitly filters the key.
