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
