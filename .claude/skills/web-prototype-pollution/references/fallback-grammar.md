# The fallback grammar — the read-shapes pollution hijacks

Pollution only matters where a read falls back to your value. This
is the grammar of reads that inherit — and the names each one tends
to read.

---

## 1. `opts.x || def` — the falsy fallback

```js
const url = opts.url || "/api";
const tpl = opts.template || "default";
const lvl = user.level || "guest";
```

`||` reads `.x` through the chain — a polluted `x` returns your
truthy value. Write a FALSY value (`""`, `0`, `false`, `null`) and
the default still wins — the write must land a truthy value.

Names in the wild: `url`, `uri`, `host`, `hostname`, `path`, `api`,
`endpoint`, `callback`, `webhook`, `src`, `href`, `link`, `image`,
`avatar`, `icon`, `css`, `style`, `script`, `template`, `layout`,
`theme`, `engine`, `view`, `views`, `root`, `dir`, `dest`, `file`,
`filename`, `name`, `title`, `label`, `key`, `secret`, `token`,
`secret_key`, `signing`, `debug`, `verbose`, `level`, `role`,
`is_admin`, `isAdmin`, `admin`, `owner`, `tenant`, `mode`, `env`,
`config`, `options`, `opts`, `settings`, `prefs`, `defaults`.

## 2. `opts.x ?? def` — the nullish fallback

```js
const n = opts.n ?? 10;
```

`??` fires only on `null`/`undefined` — a polluted `x` wins even
with `0`, `false`, `""` — a broader write surface than `||`. A
polluted falsy-but-non-null value hijacks `??` where `||` wouldn't.

## 3. `'x' in obj ? obj.x : def` — the membership fallback

```js
if ('isAdmin' in user) return user.isAdmin;
```

`in` walks the chain — polluted `isAdmin` makes the test true AND
the read return your value. The `in`-guard looks defensive but is
not — it checks existence, not ownership.

## 4. `hasOwnProperty`/`Object.keys` — the own-only reads

```js
if (opts.hasOwnProperty('x')) opts.x   // PP DEAD
for (const k of Object.keys(opts))     // PP DEAD
JSON.stringify(opts)                   // PP invisible in output
```

The own-only reads — your pollution never enters. When every read
in the codebase is own-only, the write is cosmetic: falsifier.

## 5. `typeof x === 'undefined'` / `x === undefined`

```js
const v = typeof opts.v === 'undefined' ? def : opts.v;
const v = opts.v === void 0 ? def : opts.v;
```

Chain-reads — pollution visible. `undefined` comparisons let ANY
value through including falsy — broader than `||`.

## 6. Destructuring — the subtle grammar

```js
const { x = def } = opts;              // default on undefined —
                                       // chain-read, PP works
const { x } = opts;                    // reads chain — PP works
const { x: local = def } = opts;       // same
function f({ x = def }) {}             // param destructuring — same
```

Destructuring reads through the chain — a polluted `x` fills the
binding. The `= def` only fires on `undefined`.

## 7. `Reflect.get`/`Proxy`/`get`-traps

```js
Reflect.get(opts, 'x')                  // chain-read — PP works
new Proxy(obj, {get: (t,k)=>t[k]})     // trap reads chain — works
Object.getOwnPropertyDescriptor(...)   // own-only — dead
Reflect.getOwnPropertyDescriptor(...)  // own-only — dead
```

## 8. `for..in` unfiltered

```js
for (const k in obj) { use(obj[k]) }   // ENUMERATES inherited —
                                       // your polluted key ITERATES
for (const k in obj) {                 // and its value gets read
  copy[k] = obj[k]                     // → copied into an own slot!
}
```

An unfiltered `for..in` both SEES your property and may COPY it —
the secondary carrier that turns a hidden write into an own prop.

## 9. The `with` statement

```js
with (config) { render(x) }            // 'x' resolves config.x first —
                                       // then the proto chain
```

`with` is rare in modern code but shows in templates/legacy —
pollution fills unbound identifiers.

## 10. Getter/descriptor reads

```js
Object.getOwnPropertyDescriptor(proto, 'x')?.get?.call(obj)
// reads the DESCRIPTOR's getter — if a polluted prop becomes a
// getter-like value the call site decides; rare
```

## 11. The read-position table — which sink reads which grammar

| Sink | Grammar | PP |
|---|---|---|
| `opts.x \|\| def` | falsy | yes |
| `opts.x ?? def` | nullish | yes |
| `'x' in o ? o.x` | membership | yes |
| `o.x === undefined` | undefined-check | yes |
| `{x = d} = o` | destructure | yes |
| `for..in` unfiltered | enumerate | yes |
| `with(o){x}` | scope | yes |
| `Reflect.get(o,'x')` | chain | yes |
| `o.hasOwnProperty('x')` | own | no |
| `Object.keys(o)` | own | no |
| `JSON.stringify(o)` | own | no |
| `Object.entries` | own | no |
| `Map.get` | store | no |
| `Object.create(null).x` | no proto | no |

## 12. The "which names do reads read" method

For a white-box handout:

```bash
# every fallback read, one grep:
grep -rnoE '[a-zA-Z_.]+\.(x|[a-zA-Z_]+)\s*(\|\||\?\?|===?\s*undefined|typeof)' . \
  --include='*.js' | grep -v node_modules | head -200
# then extract the PROPERTY NAMES — that's your pollution target list
```

Each `name.prop || def` is a candidate — the `prop` name is what to
write. The write surface is bounded by the read vocabulary.
