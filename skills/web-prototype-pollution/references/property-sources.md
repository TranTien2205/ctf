# Property sources — where the polluted name gets read from

The write is only half the equation. The other half: WHICH object
does the app read the property from — and is that object one your
pollution reaches?

---

## 1. The lookup objects

```js
// object-typed reads — a plain object inherits Object.prototype
opts.x          // plain {} — inherits your pollution
config.x        // if config is a plain merged object
merged.x        // the merge target itself — inherits too
data.x          // a request-body object — inherits
ctx.x           // a context object — inherits
res.locals.x    // express render locals — plain object
app.locals.x    // app-level object — plain object
```

Any `x.y` read where `x` is a `Object.getPrototypeOf(x) ===
Object.prototype` object sees your pollution. That's MOST objects.

## 2. The reads that DON'T see it

```js
opts.hasOwnProperty('x')        // own-only — proto invisible
'x' in opts                     // SEES proto — not a guard
Object.keys(opts)               // own-enumerable only — proto invisible
Object.getOwnPropertyNames(opts)// own only
JSON.stringify(opts)            // own-enumerable only — proto invisible
Object.entries(opts)            // own only
opts.x                          // SEES proto — the vulnerable read
opts['x']                       // SEES proto — bracket form same
Reflect.get(opts, 'x')          // SEES proto
opts?.x                         // SEES proto — optional chain same
```

The distinction: `in`/`[]`/`.x`/`Reflect.get`/`?.` all walk the
chain; `hasOwnProperty`/`keys`/`getOwnPropertyNames`/`entries`/
`stringify`/`for..in`-filtered don't. A sink reading through the
first group inherits your write; through the second, it doesn't.

## 3. `Map`/`Set`/class-instance reads

```js
map.get('x')            // a Map — PP invisible, own store
set.has('x')            // a Set — PP invisible
new Map([[...]]).get()  // same
class C { x } c.x       // own property if defined — PP invisible
                        // UNDEFINED class field — PP visible!
Object.create(null).x   // NO prototype — PP invisible
Object.freeze(obj).x    // frozen target still READS proto — visible
```

`Object.create(null)` objects are immune — they have no prototype.
Map/Set lookups bypass the prototype chain entirely. A class field
explicitly defined (`x = 1` in the class body) is an OWN property —
pollution invisible; an UNDECLARED field read (`c.x` with no `x`
declared) falls through to the proto — visible.

## 4. The `for..in` quirk

```js
for (const k in obj) {...}        // walks INHERITED enumerable too!
for (const k in obj) { if (obj.hasOwnProperty(k)) {...} }  // filtered
```

`for..in` WITHOUT a hasOwnProperty guard ENUMERATES your polluted
property — a later loop can copy it into an own-property slot or
process it as data. That's a secondary carrier: PP the enumerable
prop, the app's own `for..in` merges it somewhere reachable.

## 5. `Object.assign`/`spread` don't copy proto

```js
const c = Object.assign({}, polluted);  // copies OWN props only
const c = {...polluted};                // own props only
const c = {...{}, ...pollutedProto};    // proto props not copied
```

Spread/`assign` read the source's OWN enumerable — a polluted
`Object.prototype.x` is NOT copied into a fresh `c`. But `c.x` still
resolves through c's own prototype — the write survives via the
chain, not the copy.

## 6. `Object.getPrototypeOf`/`instanceof` reads

```js
obj instanceof C          // walks obj's proto chain — PP visible in 'instanceof' checks
obj.__proto__             // the accessor — reads the proto itself
Object.getPrototypeOf(obj)// same
obj.constructor           // inherited — pollute 'constructor' and
                          // every object's constructor lies
```

`obj.constructor` is the subtle one — pollute `constructor` on
`Object.prototype` and EVERY object's `.constructor` reads your
value — a confused-identity primitive.

## 7. `structuredClone`/`JSON` drops proto

```js
structuredClone(obj)      // own props only — PP invisible
JSON.parse(JSON.stringify(o)) // own enumerable — invisible
postMessage(obj)          // structured-clone — invisible
localStorage JSON         // own only — invisible
```

## 8. The "options object" defaults pattern

```js
// THE vulnerable grammar
function f(opts) { return opts.x || default; }
const o = Object.assign({}, defaults, req.body);
const o = {...defaults, ...req.body};
const o = merge({}, defaults, req.body);       // merge itself is the write
const o = _.defaultsDeep({}, req.body, defaults);
```

`Object.assign`/spread put `req.body`'s OWN keys on `o` — they
don't trigger PP through the copy. `merge`/`defaultsDeep` DO walk
into `req.body`'s nested objects and write through `__proto__` —
the copy-path is safe, the merge-path is the bug.

## 9. The proxy/`with` edge

```js
with (opts) { x }         // 'with' walks the object then the chain —
                          // x could read the polluted prop!
new Proxy(obj, {get})     // a get-trap reads props — trap sees proto
```

`with(opts){...}` resolves `x` against `opts` first — a polluted
`opts` proto makes `x` resolve to your value before the scope chain.

## 10. The fallback grammar that pays

```js
opts.x || def             // falsy-check — pollute truthy
opts.x ?? def             // nullish — pollute anything non-null
'x' in opts ? opts.x : d  // 'in' sees proto — pollute
opts.hasOwnProperty('x') ? ... // own-only — PP dead
typeof opts.x === 'undefined' ? d : opts.x  // reads chain — works
opts.x === undefined ? d : opts.x           // same
```

`||` and `??` and `=== undefined` all read the CHAIN — the sink's
check doesn't have to check own-ness to be vulnerable; it just has
to read `.x`.

## 11. Which writes land as OWN vs inherited

```js
// the merge assigns dest[k] = src[k]:
//   k='__proto__' → hits the __proto__ SETTER — rewrites the proto
//   k='x'         → own property on dest (not pollution!)
//   k='constructor' → walks into dest.constructor = Function → then
//     the merge continues into constructor.prototype — PP via alias
```

The KEY distinction for the readback: a polluted `x` is read from
`Object.prototype`; an own-assigned `x` is read from `dest` — the
fresh-object readback (`({}).x`) is what separates them.
