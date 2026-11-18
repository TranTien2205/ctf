# SSTI detection — prove evaluation, then name the engine

Two questions, in order:

```text
1. does the value get EVALUATED as a template?   → arithmetic marker
2. WHICH engine evaluated it?                     → discrimination probes
```

Never skip step 1 — injecting engine payloads without proving
template-eval wastes the probe budget on a value that was never
rendered.

---

## 1. The arithmetic marker — first probe

```text
{{7*7}}        → 49? template-eval confirmed
${7*7}         → 49? EL/Twig-variant/FreeMarker
<%= 7*7 %>     → 49? ERB/EJS/JSP
#{7*7}         → 49? Thymeleaf/Ruby/OGNL
*{7*7}         → 49? Thymeleaf
{{= 7*7}}      → 49? some engines
```

Where the output lands: reflected in the response body, an email
subject, a PDF, an error page — anywhere the value is rendered.

The falsifier: `{{7*7}}` renders literally → no template eval on
this input. Move on — the class is closed for this field (record
the negative).

---

## 2. The engine-discrimination tree

Different engines share `{{}}` syntax but differ in details. The
classic discrimination probe set — inject each, read the output:

| Probe | Jinja2 | Twig | Nunjucks | Mako | Smarty | FreeMarker | Velocity | Thymeleaf |
|---|---|---|---|---|---|---|---|---|
| `{{7*7}}` | 49 | 49 | 49 | err | err | err | err | err |
| `${7*7}` | err/lit | err/lit | err/lit | 49 | err/lit | 49 | lit | err |
| `{{7*'7'}}` | 7777777 | 49 | 49 | — | — | — | — | — |
| `{%7*7%}` | err | err | err | — | — | — | — | — |
| `#{7*7}` | lit | lit | lit | — | — | — | — | 49? |
| `*{7*7}` | lit | lit | lit | — | — | — | — | 49 |
| `a{*comment*}z` | az | a{*}z | — | — | — | — | — | — |
| `{{'a'+'b'}}` | ab | err | ab | — | — | — | — | — |
| `{{'a'~'b'}}` | ab | ab | — | — | — | — | — | — |
| `{{7/0}}` | err inf? | err | err | — | — | — | — | — |
| `{{7**7}}` | 823543 | 823543? | err | — | — | — | — | — |

The most reliable single discriminator: `{{7*'7'}}`:
- Jinja2: `"7"*7` → `7777777` (string multiply)
- Twig: `7*'7'` → `49` (numeric coercion)
- Nunjucks: `7*'7'` → `49` (JS semantics)

`a{*comment*}z` → `az` distinguishes Jinja2 (comments `{* *}`) —
Twig uses `{# #}` → `a{#x#}z` → `az` instead.

---

## 3. The error-leak path — errors name the engine

```text
{{nonexistent}}
{{7/0}}
{{x.y.z}}
{{'a'+1}}            -- type error
{{break}}            -- keyword misuse
```

Errors often carry the engine name in the trace:

```text
jinja2.exceptions.UndefinedError     → Jinja2
twig\Error\Syntax                    → Twig (PHP)
freemarker.core.InvalidReferenceException → FreeMarker
org.apache.velocity...               → Velocity
org.thymeleaf.exceptions...          → Thymeleaf
Smarty: ...                          → Smarty
mako.exceptions...                   → Mako
Tornado/uncaught                     → Tornado
```

Error pages leak the engine faster than payload-matching — always
send one malformed probe per input.

---

## 4. The context map — where the value renders

```text
reflection in response body      → standard
inside an email template          → send yourself an email
inside a PDF/report               → generated doc — render via tool
inside an error page              → trigger an error with the value
inside an export/invoice          → downloadable artifact
inside a notification             → push/email — second-order
```

Second-order SSTI: input stored, rendered LATER in a different
context (invoice PDF, admin report) — the marker must appear in
the artifact, not the original response.

---

## 5. The sandbox question — eval vs code-exec

```text
{{7*7}}=49 confirms template-eval — NOT code-exec.
Code-exec needs the sandbox escape: {{''.__class__.__mro__...}}
  → check engine file for the RCE chain
Some engines have NO code-exec (logic-less Mustache, some
  sandboxed Twig configs) — the finding may be read-only or DoS.
```

---

## 6. The detection probe set — the full first-wave

```text
{{7*7}}          -- jinja/twig/nunjucks family
${7*7}           -- freemarker/mako/el
<%= 7*7 %>       -- erb/ejs
#{7*7}           -- thymeleaf/ognl
*{7*7}           -- thymeleaf
{{7*'7'}}        -- jinja2 vs twig discriminator
{{7**7}}         -- jinja2 pow
a{*x*}z          -- jinja2 comment
a{#x#}z          -- twig/jinja comment
${'a'.getClass()} -- freemarker/velocity class-reflector
{{7/0}}          -- error leak
{{#x}}{{/x}}     -- mustache/handlebars section
{{>x}}           -- mustache partial
```

---

## 7. Rendering-context discrimination — one value, two renders

```text
?q={{7*7}} → "49" in response → direct-render SSTI
?q={{7*7}} → literal in response BUT 49 in the invoice-PDF
  → second-order — the marker lands in a later render
```

Always check EVERY render-path for the input — profile fields,
emails, PDFs, admin views. The render context for an email
template differs from a page template (different sandbox config!).

---

## 8. Quick engine-by-stack heuristic

```text
Python (Flask/Django-ish)   → Jinja2 first guess; Mako, Tornado
PHP                         → Twig (Symfony), Smarty, Blade(escapes), Latte
Java                        → FreeMarker, Velocity, Thymeleaf, Pebble
Node.js                     → Nunjucks, EJS, Pug/Jade, Handlebars, doT
Ruby                        → ERB, Slim, Haml, Liquid
Go                          → text/template (limited — no user expr eval normally)
.NET                        → Razor (compiled — rarely SSTI-able), Scriban, Fluid
```

Stack-detection is a HINT not a fact — confirm with the
discrimination probes. A Node app can run Jinja via a lib.


---

## Detection appendix — the response-analysis details

### What "evaluated" actually looks like

```text
REQUEST:  ?name={{7*7}}
RESPONSE: "Hello 49"           → {{7*7}} evaluated — CONFIRMED
RESPONSE: "Hello {{7*7}}"      → literal echo — not eval'd
RESPONSE: "Hello 7777777"      → wait — that's '7'*7 — check
                                  whether you sent '7'*7 (str-mul)
RESPONSE: "Hello 7*7"          → delimiters stripped — filter ate {{ }}
RESPONSE: 500                  → engine parsed and errored —
                                  still evidence of eval-path
RESPONSE: "Hello "             → swallowed — engine consumed it
                                  but expr-result suppressed? or
                                  input-blocked? probe with {{1}}
```

### The input-consumed test — silent-eval tell

```text
?name={{1}}     → "Hello "     → the {{1}} was EVALUATED to
                                 nothing-renderable? or filtered?
?name=1         → "Hello 1"    → plain text passes → delimiters
                                 are the trigger → SSTI still
                                 possible — the {{}} was CONSUMED
                                 by the parser — the result was ''
                                 → try {{1+1}} → "Hello 2"? → works
```

`{{1}}` rendering as `''` isn't a failure — the engine ate it —
the result just happened to be empty — `{{1+1}}` distinguishes.

### The pre-filter signatures — before the engine

```text
{{7*7}} → "illegal input"      → input-filter — before engine —
                                  encode/mutate — sanitizer_fuzz
{{7*7}} → "invalid characters"  → same — the {{}} rejected
{{7*7}} → 400                 → request-validation — maybe not
                                 templated at all
{{7*7}} → "Hello {{7"          → delimiter-eaten — the }s removed —
                                  try %7B%7B7*7%7D%7D encoded
{{7*7}} → "Hello {7*7}"        → ONE brace eaten — single-strip —
                                  try {{{{7*7}}}} nesting
```

### The double-render trick — encoding-then-template

```text
?name=%257B%257B7*7%257D%257D
   → proxy decodes once → app gets {{7*7}} → renders 49
   — DOUBLE-url-encoding — when the app url-decodes AFTER the
     proxy already did → the payload survives one decode-layer
?name=%7B%7B7*7%7D%7D
   → single-encode — for apps that DON'T auto-decode the param
```

### The content-type discrimination

```text
GET ?name={{7*7}}           → literal
POST name={{7*7}}           → 49!
   → the app templates POST-body fields but not GET params —
     both reach the renderer but only body goes through
POST {"name":"{{7*7}}"}     → json-body → may also reach it
   → try content-type switching — the app may pull the field
     from any content-type it parses
```

### The header-render check — hidden injection points

```bash
curl -H 'User-Agent: {{7*7}}' TARGET/      → reflected? then check
                                            /log /admin /audit
curl -H 'X-Forwarded-For: {{7*7}}' TARGET/ → ip-logs render
curl -H 'Referer: http://x/{{7*7}}' TARGET/ → analytics-render
curl -H 'Cookie: s={{7*7}}' TARGET/        → cookie-render
```

User-Agent into a log-view = the classic stored-header SSTI —
the /log or /admin page renders it later.

### The deferred-render check — stored vs reflected

```text
POST profile.bio={{7*7}} → view /profile → literal?
   → the render may be at a DIFFERENT endpoint:
     /admin/users → renders the bio? 49?
     /invoice     → pdf-render? 49?
     the welcome-mail → 49 in the email body?
   → trigger every consumer of the stored field
```

### The engine-tells inside error-pages

```text
"jinja2.exceptions.TemplateSyntaxError"    → Jinja2
"jinja2.exceptions.UndefinedError"          → Jinja2
"Twig\Error\Syntax" / "Twig_Error_Syntax"   → Twig
"freemarker.core.ParseException"            → FreeMarker
"org.apache.velocity.exception"             → Velocity
"ognl.OgnlException"                        → OGNL
"org.springframework.expression.spel"       → SpEL
"ActionView::Template::Error"               → Rails/ERB
"ejs" / "nunjucks" / "handlebars" in stack   → that engine
"SmartyCompilerException"                    → Smarty
"django.template"                            → Django
"Slim::Parser" / "Temple"                    → Slim
"pug" / "jade"                              → Pug
"pebble"                                    → Pebble
"jinjava"                                   → Jinjava
"mako" / "MakoException"                    → Mako
"tornado"                                   → Tornado
"BeetlException"                            → Beetl
"Razor"/"cshtml"                            → Razor
"liquid"/"Liquid::"                          → Liquid
"ELException"/"JasperException"             → JSP/EL
"Microsoft JScript"/"VBScript"              → ASP-classic
"ColdFusion"                                → CFM
"groovy" / "GroovyRuntimeException"         → Groovy
"latte"/"Latte"                              → Latte
"volt"                                      → Volt
```

### The two-line discriminator cheatsheet

```text
Jinja2 vs Twig:     {{'a'+'b'}} → 'ab' = jinja, '0' = twig
Jinja2 vs Nunjucks: {{'a'.upper()}} → 'A' = jinja, err = nunjucks
                    {{range.constructor.name}} → 'Function' = nunjucks
EJS vs ERB:         <%= 'a'.upcase %> → 'A' = erb, err = ejs
                    <%= 'a'.toUpperCase() %> → 'A' = ejs, err = erb
                    <%= NaN %> → 'NaN' = ejs (ruby has no NaN literal)
Velocity vs FM:     ${x!''} → silences = FM; $x → quiet-empty = velocity
                    ${.version} → renders = FM
Slim vs Pug:        #{RUBY_VERSION} → version = slim; #{process} → pug
ERB vs JSP:         <%= RUBY_VERSION %> = erb; <%= request.getMethod() %> = jsp
Thymeleaf vs others: *{} only in th:* attrs — position is the tell
```
