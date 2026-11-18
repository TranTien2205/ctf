# Framework contexts — where SSTI actually lives

SSTI isn't "input into template" — it's the app passing attacker
data where the engine treats it as code. The vuln PATTERNS are
framework-shaped: learn the code shapes that create it.

---

## 1. Flask / Jinja2 — the canonical CTF stack

### The vulnerable patterns

```python
# THE classic — render_template_string with user data:
return render_template_string("Hello " + request.args['name'])
return render_template_string("<h1>" + username + "</h1>")
return render_template_string(request.args['t'])
return render_template_string(f"Hi {name}!")

# Jinja2 direct:
from jinja2 import Template
Template(user_input).render()
Template("Hello "+name).render()

# Environment:
env = jinja2.Environment()
env.from_string(user_input).render()
env.from_string("Hi "+name).render()
```

vs the SAFE pattern (data in render-context, not template):

```python
render_template_string("Hello {{name}}", name=name)   # safe
render_template("page.html", name=name)                # safe
```

The distinction: `{{user_input}}` INSIDE a template = data =
escaped. `user_input` CONCATENATED INTO the template string =
template code = evaluated.

### Where it appears in apps

```text
- greeting/name endpoints      → "Hello {name}" concatenation
- error-page templates          → "Error: {message}"
- email send                    → render_template_string(body)
- custom-404/500                → "Page {path} not found"
- redirect/confirm pages        → "Redirecting to {url}"
- PDF/invoice generation        → reportlab/weasyprint + jinja
- preview endpoints             → ?template= ... raw eval
- theme/customization           → user "theme" = template string
- notification text             → "Hi {user}, {msg}"
```

### Flask globals reachable from ANY template — always try

```jinja2
{{config}}            -- app.config — FLAG/SECRET_KEY lives here
{{self}}              -- TemplateReference
{{request}}           -- full request
{{session}}           -- session contents
{{g}}                 -- flask.g
{{url_for}} {{get_flashed_messages}} {{lipsum}} {{cycler}} {{joiner}} {{namespace}}
```

`{{config}}` alone solves a huge share of CTF Flask-SSTI — flag
as a config key, or SECRET_KEY to forge sessions
(`flask-session-cookie-manager`/`session_dissect` chain).

---

## 2. Django — rarely SSTI-able, but watch for

```python
# SAFE by default — {{x}} escapes:
return render(request, 'page.html', {'x': user_input})

# VULNERABLE — template built from user input:
from django.template import Template, Context
Template(user_input).render(Context())
Template("Hello "+name).render(Context())
engine.from_string(user_input).render()

# OR — include-path injection:
{% include user_controlled_name %}     → template-file inclusion
```

Django templates are logic-less — even with injection you get
`{{var}}` access + `{% %}` tags only — the payload ceiling is
`{% include %}` path-traversal + bound-object field-leaks.
`{{user.password}}`, `{{user.email}}`, `{{settings.SECRET_KEY}}`
(if bound).

---

## 3. Spring Boot + Thymeleaf — the `__${}__` pattern

```java
// THE vuln shape — user input inside a Thymeleaf expression:
@GetMapping("/path")
public String path(@RequestParam String lang) {
    return "user/" + lang + "/welcome";   // view-name concat!
    // lang = "__${7*7}__::x"  → SpEL in the fragment name
}

// or: message codes / fragments from params:
return "__${" + param + "}__";           // raw concat → eval
```

The `__${...}__::x` fragment-name trick: `lang=__${7*7}__::x`
turns the return-value into a preprocessing expression → SpEL eval.
`{x}` inside `th:replace="__${x}__"` is the same mechanism.

Spring error-pages: a bad view name in the error template →
your injected name gets SpEL'd → RCE.

---

## 4. Rails — ERB inline-render and user-owned templates

```ruby
# VULNERABLE:
ERB.new("Hello #{name}").result           -- name in template
render inline: params[:template]           -- the template IS input
render inline: "Hello #{name}"             -- ruby-interpolated THEN
                                             template-parsed — double!
render template: params[:t]                -- template-path → LFI-ish
eval(params[:x])                           -- direct — not SSTI but worse
```

Rails `render inline:` with user input = direct ERB eval.
`#{...}` interpolation in the string happens BEFORE ERB parses —
`"Hello #{name}"` embeds the name as template SOURCE →
`<%= %>` inside `name` executes.

---

## 5. Express/Node — res.render + engines

```javascript
// VULNERABLE:
res.render(userInput)                        // view-name = input
res.render('page', {x: require('ejs').render(userInput)})
ejs.render(userInput)                         // template = input
ejs.render('Hello '+name)                     // concat into source
nunjucks.renderString(userInput)
nunjucks.renderString('Hi '+name)
pug.render(userInput)
pug.render('p Hello '+name)
template = `Hello ${name}`; ejs.render(template)  // JS-template bug!
```

The `${name}` inside a JS template-literal embeds the value INTO
the template source — `<%= %>` inside it then evaluates. The
double-template bug — a JS template building a template.

---

## 6. Laravel — Blade edge cases

```php
// Blade compiles at build — but these ARE injectable:
Blade::render($user_input)                  // compiles the string!
view()->make($user_template)                 // view-name input
eval('?>'.$user_input)                        // php-eval — not ssti
$template = "Hello {$name}"; Blade::render($template)
```

`Blade::render(string)` is the Laravel-SSTI surface — the string
compiles → `@php`/`{{}}` execute.

---

## 7. Java generic — MessageFormat/f-string adjacent

```java
// NOT template engines but eval-adjacent:
MessageFormat.format(userInput)             -- format-string!
String.format("%s", x)                       -- format specifiers
// and the real SSTI via user-template-strings:
freemarker.template.Template t = new Template("t", userInput, cfg);
   -- Template(name, source, cfg) — the string IS template source!
t.process(dataModel, out);
```

The `new Template("t", userInput, cfg)` pattern — FreeMarker's
string-source constructor — is THE FreeMarker SSTI code shape.

---

## 8. The polyglot detection — when engine unknown

The value renders in ANY context — fire the superset probe:

```text
{{7*7}}${7*7}<%=7*7%>#{7*7}*{7*7}
   → the position that evaluates names the family
   → e.g. renders "49${7*7}<%=7*7%>#{7*7}*{7*7}" → Jinja/Twig/etc
```

Or the error-forcing polyglot:

```text
{{'a'}}${'a'}<%='a'%>#{'a'}
   → whichever errors → engine syntax leaked in stack
```

`sanitizer_fuzz`/`variant_matrix` handle the systematic sweep.

---

## 9. Second-order sources — where the template-input comes from

```text
profile field → rendered in invoice/email/admin report
username → rendered in greeting/log/admin dashboard
order note → rendered in order-confirmation page/email
ticket body → rendered in support-dashboard
product description → rendered in catalog + PDF spec-sheet
template-attachment upload → rendered by preview
theme/layout customization → rendered for ALL visitors
email subject/body → rendered in notification pipeline
```

The render-context differs — an email template may run the same
engine with DIFFERENT bound objects (mailer-context ≠ web-context).
Test both.

---

## 10. The identify-then-attack map

| Code pattern | Engine | File |
|---|---|---|
| `render_template_string("..."+x)` | Jinja2 | jinja2.md |
| `Template(x).render()` | Jinja2 | jinja2.md |
| `return "user/"+x+"/page"` Spring | Thymeleaf | thymeleaf.md |
| `new Template("t",x,cfg)` | FreeMarker | freemarker.md |
| `Velocity.evaluate(ctx,w,"t",x)` | Velocity | velocity.md |
| `erb = ERB.new(x)` | ERB | ruby-engines.md |
| `render inline: x` | Rails ERB | ruby-engines.md |
| `Blade::render(x)` | Blade | misc-engines.md |
| `ejs.render(x)` / `nunjucks.renderString(x)` | Node | node-engines.md |
| `smarty->display("string:"+x)` | Smarty | smarty.md |
| `th:replace="__${x}__"` | Thymeleaf | thymeleaf.md |
