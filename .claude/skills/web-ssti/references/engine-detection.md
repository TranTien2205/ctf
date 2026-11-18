# Engine fingerprinting — the complete matrix

`detection.md` covers the probe workflow. This file is the
reference table: every engine, its delimiters, its error
signature, its tell.

---

## 1. The syntax-family table

| Family | Delimiters | Engines |
|---|---|---|
| `{{}}` | `{{expr}}` `{%stmt%}` `{#c#}` | Jinja2, Twig, Nunjucks, Django-part, Handlebars?, Liquid?, Pebble |
| `${}` | `${expr}` | FreeMarker, Velocity, Jinjava?, Groovy, JSP-EL, JS-template |
| `#{}` | `#{expr}` | Slim, Pug?, OGNL?, SpEL?, JS-template |
| `<% %>` | `<%=expr%>` `<%code%>` | ERB, EJS, JSP, ASP, Jinja-uncommon |
| `{$}` | `{$x}` `{fn}` | Smarty, Latte, Volt |
| `@{}/@@` | `@{x}` `@code` | Razor, Thymeleaf-attrs |
| `*{}/__${}__` | `*{x}` `__${x}__` | Thymeleaf/SpEL preprocessing |

## 2. The arithmetic-discrimination matrix

| Probe | Jinja2 | Twig | Nunjucks | FreeMarker | Velocity | ERB | EJS | Thymeleaf |
|---|---|---|---|---|---|---|---|---|
| `{{7*7}}` | 49 | 49 | 49 | lit | lit | lit | lit | lit |
| `{{7*'7'}}` | 7777777 | 7 or 49? | 7777777 | lit | lit | lit | lit | lit |
| `{{'a'+'b'}}` | ab | 0 | ab | lit | lit | lit | lit | lit |
| `{{'a'~'b'}}` | ab | ab | ab | lit | lit | lit | lit | lit |
| `{{'a'.upper()}}` | A | err | err | lit | lit | lit | lit | lit |
| `{{'a'\|upper}}` | A | A | A | lit | lit | lit | lit | lit |
| `${7*7}` | lit | lit | lit | 49 | 49 | lit | lit | lit |
| `<%=7*7%>` | lit | lit | lit | lit | lit | 49 | 49 | lit |
| `*{7*7}` | lit | lit | lit | lit | lit | lit | lit | 49(in-attr) |
| `{{7*'7'}}` | — PHP coerces '7'→7 so Twig may give 49 or error | | | | | | | |

`'a'+'b'` → `ab` python-family vs `0` Twig (numeric +) — the
sharpest Jinja-vs-Twig tell. `'a'~'b'` → `ab` all-three `{{}}`.

## 3. The error-signature table

| Error text | Engine |
|---|---|
| `jinja2.exceptions.TemplateSyntaxError` | Jinja2 |
| `jinja2.exceptions.UndefinedError` | Jinja2 |
| `Twig\Error\Syntax` / `Twig_Error_Syntax` | Twig |
| `Twig\Error\Runtime` | Twig |
| `freemarker.core.ParseException` | FreeMarker |
| `freemarker.template.TemplateException` | FreeMarker |
| `org.apache.velocity.exception` | Velocity |
| `VelocityResourceException` / `ParseErrorException` | Velocity |
| `org.thymeleaf.exceptions` | Thymeleaf |
| `ognl.OgnlException` | OGNL |
| `org.springframework.expression.spel` | SpEL |
| `SyntaxError` + `ejs` in stack | EJS |
| `SyntaxError` + `nunjucks` | Nunjucks |
| `SyntaxError` + `handlebars` | Handlebars |
| `ActionView::Template::Error` | Rails/ERB |
| `ActionView` + `erb` | ERB |
| `Slim::Parser` / `Temple` | Slim |
| `Smarty` / `SmartyCompilerException` | Smarty |
| `GroovyRuntimeException` / `groovy.text` | Groovy |
| `JasperException` / `ELException` | JSP/EL |
| `Microsoft JScript`/`VBScript` | ASP-classic |
| `Razor` / `cscode`/`cshtml` | .NET Razor |
| `MakoException` / `mako.runtime` | Mako |
| `tornado` + `Template` | Tornado |
| `django.template` | Django |
| `pug` / `jade` in stack | Pug |
| `Liquid::` | Liquid |
| `pebble` | Pebble |
| `jinjava` | Jinjava |
| `doT`/`dust`/`ect` in stack | those JS engines |
| `VelocityViewServlet` | Velocity |
| `BeetlException` | Beetl |
| `org.apache.struts2` + `ognl` | Struts-OGNL |

## 4. The stack-leak probe — force the error

```text
{{'a}}       -- unterminated string → parser stack
{{ 7* }}     -- syntax error
{% for %}    -- bad statement
${'a}        -- freemarker-parse
<%=          -- unclosed ejs/erb → its stack
{'a'|        -- dangling filter
{{x.y.z.q.w}} -- deep-attr → undefined-chain → error WITH type info
```

An error page that names the engine+version+FILE PATH is three
findings in one — engine, version, AND filesystem layout.

## 5. The silent-detection table — no-error engines

Velocity often renders `${fake}` literally — silent fails:

```text
$x            → "$x" literal? or empty? or resolved?
#set($x=1)    → directive absorbed? → Velocity almost-certain
#foreach      → directive syntax → Velocity
$x.class      → Class-object render? → velocity-Java
```

FreeMarker silent-fails on `${undefined}` → renders ERROR or
empty depending on config — try `${.now}` (always-defined) instead.

## 6. The version-tell probes

| Engine | Version-tell |
|---|---|
| Jinja2 | `{{self._TemplateReference__context}}` — the internal name |
| Twig | `{{_self.env}}` — env obj exists v1-v2; constant() filters |
| FreeMarker | `${.version}` — the builtin! |
| Velocity | `$velocityCount` — deprecated-but-present var |
| Smarty | `{$smarty.version}` — direct |
| ERB | `<%=RUBY_VERSION%>` — ruby version |
| Nunjucks | `{{range(3)}}` + `{{cycler}}`/`{{joiner}}` — same helpers |
| Mako | `${self}` differs from Jinja — `self.body()`/`self.attr` |
| SpEL | `T(java.lang.Math)` — T() function signature |

## 7. The two-engine trap — stacked renderers

```text
App renders input → jinja → then feeds output to another engine?
   e.g. SSTI → markdown → markdown's OWN template? rare
JS-template-literal → f"..." → ejs? — the DOUBLE-template:
   server builds a template via a template — eval order matters!
Frameworks with TWO engines (e.g. Spring + jsp + thymeleaf)
   → the VIEW-RESOLVER picks by name — .jsp vs .html routes differ
```

`return "user/"+lang+"/welcome"` — the returned name picks the
template FILE — injecting `../` picks a different template;
injecting `__${}__` gets it EVALUATED as the fragment. Two
different bugs in one line.

## 8. Confirm-then-map — the probing order

```text
1. {{7*7}}  → evaluates?  (the gate)
2. {{7*'7'}} → str-mul?   (python-family vs php-family)
3. ${7*7}   → evaluates?  (java/groovy/el family)
4. <%=7*7%> → evaluates?  (ejs/erb/jsp family)
5. force-error → stack-trace names it
6. {{'a'+'b'}} → 'ab' (python) vs '0' (twig)
7. {{config}}/{{_self}}/{{app}} → framework guess
```

Seven probes → engine + usually framework. `variant_matrix`
runs the shape-sweep in one pass.
