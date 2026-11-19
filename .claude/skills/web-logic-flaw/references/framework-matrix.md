# Framework matrix — where each stack's logic flaws live

## Express / Node

| Mechanism | Where it lives | The idiom |
|---|---|---|
| mass assignment | `Model.create(req.body)`, `Object.assign`, spread | merge-all binders |
| workflow skip | middleware chains missing a `requireStep` guard | route-level checks |
| boundary | `Number` coercion, `parseInt` without radix | `qty` as `"number"` |
| replay | no idempotency middleware | absent `used` marker |
| transform | WASM/native boundaries, `Buffer` indexing | `mem[off + id*S]` |
| trust | `req.body.total` recomputed never | carried values |

Mongoose `strict` schema drops unknown fields by default (the allowlist
that saves merge-all) — check `strict: false` and `timestamps` plugins
that add writable fields.

## Flask / Django / Python

| Mechanism | Where it lives | The idiom |
|---|---|---|
| mass assignment | `Model(**request.json)`, `setattr` loops | kwargs merge |
| workflow skip | `session['step']` reads — signed but readable | cookie session |
| boundary | `int()`/`float()` coercion, `Decimal` vs float | NaN polarity |
| replay | no dedup on `@app.route` | absent marker |
| trust | `request.form.get('total')` trusted | carried fields |

Django `ModelForm`/`Meta.fields` is a real allowlist — the falsifier
lives there; admin/API write paths often bypass it. Flask's signed
cookie session is readable — `step` values in it are forgeable only
with the key, but `request.args`/`request.form` steps forge directly.

## Rails

| Mechanism | Where it lives | The idiom |
|---|---|---|
| mass assignment | `params[:user]` without `permit` | old/unguarded create |
| workflow skip | `before_action` chains missing a step guard | skipped filter |
| boundary | `to_i` — `"NaN"`, `"abc"` → `0` silently | coercion floor |
| replay | non-atomic `find` + `update` | check-then-set |
| trust | hidden fields, `params` carried totals | carried values |

`params.require.permit` is the allowlist — but `params[:user]` mass-
assigns everything when `permit` is skipped, and `.to_i` coercion makes
`"0x10"` → `0` (a floor, not a rejection — the falsifier reads
differently: silent `0`, not `400`).

## Laravel / PHP

| Mechanism | Where it lives | The idiom |
|---|---|---|
| mass assignment | `Model::create($request->all())` sans `$fillable` | unguarded fill |
| boundary | loose `==` comparisons, `intval()` coercion | `0=="string"` |
| replay | no dedup on route | absent marker |
| trust | `$request->input('total')` | carried fields |

`$fillable`/`$guarded` is the whole story — absent `$fillable`, every
column binds. PHP's `==` coercion (`"0x10" == 16` true historically,
`0 == "abc"` true pre-8.0) makes boundary values land differently than
typed stacks.

## Spring / Java

| Mechanism | Where it lives | The idiom |
|---|---|---|
| mass assignment | `@ModelAttribute`/`@RequestBody` binding | field binders |
| boundary | `int`/`long` overflow, `Integer.parseInt` | silent wrap |
| workflow skip | `@PostMapping` order not enforced | controller steps |
| trust | hidden fields + `@RequestParam` carried | carried values |

Primitive `int` parameters silently wrap on `Integer.parseInt`
overflow-error → `NumberFormatException` → `400` actually; but
`setQty(int)` via binder coercion has per-converter behavior — test the
wrap boundary empirically.

## ASP.NET

| Mechanism | Where it lives | The idiom |
|---|---|---|
| mass assignment | model binding `[FromBody]` incl. `IsAdmin` props | binder merge |
| boundary | `int` overflow — checked/unchecked contexts | `int.MaxValue+1` |
| trust | ViewBag/hidden fields | carried values |

`[Bind(Include=...)]` is the allowlist; its absence binds every public
setter — including `IsAdmin` properties convention carries.

## Go (net/http, gin, echo)

| Mechanism | Where it lives | The idiom |
|---|---|---|
| mass assignment | `json.Unmarshal` into wide structs | `ShouldBindJSON` |
| boundary | `int64`/`uint64` wraps, `strconv` errors | explicit parse |
| workflow skip | handler-per-route, no framework flow | route checks |

Go's explicit typing means `json:"qty" int` rejects `0.1` at unmarshal
— but `interface{}`/`json.RawMessage` params reopen the coercion
surface.

## Cross-stack summary

| Stack | Default binder posture | Default coercion | The usual first probe |
|---|---|---|---|
| Express | merge-all | loose (`Number`, `parseInt`) | `role=admin` at register |
| Flask/Django | kwargs-merge / form-allowlist | `int()` strict-ish | kwargs vs ModelForm path |
| Rails | strong params | `to_i` floors to 0 | unguarded `params[:x]` |
| Laravel | `$fillable`-gated | loose `==` | missing `$fillable` |
| Spring | binder incl. all setters | typed, some wrap | extra bean properties |
| ASP.NET | binder incl. all props | typed | `IsAdmin` conventions |
| Go | unmarshal into declared | strict types | `interface{}` params |
