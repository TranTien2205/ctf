# Injection-point taxonomy — WHERE the render happens

SSTI isn't one shape — the input can land in a template string,
a template NAME, an expression inside markup, a log-format, an
email subject. Each position changes what's reachable.

---

## 1. The render-point positions

| Position | Example | What's reachable |
|---|---|---|
| Direct template source | `render_template_string(input)` | EVERYTHING — full engine |
| Concatenated into source | `"Hi "+name` | full engine |
| Template NAME/path | `render(request, input)` | file-inclusion adjacent |
| View-fragment name | Spring `return "user/"+x` | preprocessing eval |
| Expression attribute | `th:text="${x}"` value from input | expression-eval |
| Message-format | `fmt.format(input)` | format-string attrs |
| Log/template-format | `logger.info("u: "+x)` | log-eval? rare |
| Stored then rendered | profile→dashboard | admin-context |
| Email body/subject | mail-render | mail-context |
| PDF gen | wkhtmlto | engine+renderer double |
| RSS/XML gen | feed-render | template in xml |
| Search-results echo | `results for "x"` | full engine if templated |
| Error-message echo | `error: x` | error-template |
| Chat/comment render | `user: x` | template in chat |
| Admin report | report-gen | privileged context |
| Notification text | push/slack format | mailer-engine |

## 2. The stored-vs-reflected split

```text
REFLECTED (param → immediate render):
  ?name={{7*7}}  → page shows 49
  → iterate freely — engine fingerprintable fast

STORED (field → later render):
  profile.bio={{7*7}} → renders on view-profile / dashboard / admin
  → render-context differs — DIFFERENT bound objects
  → fire polyglot + grab-bag — one render per save
```

## 3. The "name in template" vs "name AS template"

```python
render_template_string("Hello {{name}}", name=x)   # SAFE — data
render_template_string("Hello "+x)                   # VULN — code
```

The first is what devs INTEND — the second is what they write.
White-box: grep for `+`/f-string/format in the render-call args.
Black-box: `{{7*7}}` — only the second shape evaluates it.

## 4. Path-shaped injection — template NAME as input

```python
return render(request, request.args['t'])        # t = template PATH
return render(request, "pages/"+p+".html")
```

This isn't eval — it's template-file INCLUSION:

```text
t = ../../../etc/passwd      → file-read if loader allows
t = admin                     → render admin template without auth
t = ..%2f..%2f                 → path-traversal
t = flag                      → render flag-template
t = ../../../app/secret       → read protected template-source
```

File-inclusion adjacent — read `file-read-primitives` skill.
Path traversal reaches flag-templates the auth-gate hides.

## 5. The preprocessing position — `__${x}__`

```java
return "__${"+x+"}__::fragment"    → Spring SpEL preprocessing
th:replace="__${x}__"
```

`__${}__`/`__#{}__` — Thymeleaf preprocessing markers — the
content inside evaluates BEFORE the outer expression → double-
evaluation → the `__` wrapper turns a static-context into eval.

## 6. The expression-inside-attribute position

```html
<div th:text="${user.name}">   — ${} is INSIDE the attr —
                                  input becomes an expression
<input value="{{x}}">           — {{}} in attr — same
```

When input lands INSIDE a quoted attribute of a template-directive
— the surrounding `th:...`/`v-...`/`ng-...` decides the grammar.

## 7. The second-order render positions

```text
CSV export → downloaded file → opened in a TEMPLATE context?
Invoice number → invoice-template → PDF
Ticket subject → digest-email template
Username → logs → log-viewer → template?
Order-notes → order-detail render → confirmation email
Product review → admin-moderation page → moderator-context
Theme/css-name → layout-template → all-pages render
```

## 8. The async render positions

```text
Queued job:      worker renders input → different bound-objects
                 (no request!) but model objects rich
Cron report:     scheduled — the digest render binds admin-scope
Background task: celery/sidekiq — task-context objects
Cache warm:      pre-render with system-context
```

Async renders often run PRIVILEGED — batch-jobs bind system
objects, not user-request objects. Higher ceiling, no `request`.

## 9. The engine-boundary trick — WHERE the injection is parsed

```text
Input → app1 (jinja, safe: renders x as data)
      → forwarded to app2 (parses x as template!) → eval

Input → proxy/template-middleware → engine sees the raw input?
```

Multi-tier: the engine that evaluates isn't the one you talked
to — a backend renderer/admin-service may template your stored
input with a DIFFERENT engine than the front.

## 10. The injection-point checklist

```text
□ Direct eval:  template-string(input) — cleanest
□ Concat:       "..."+input+"..." — engine full-reach
□ Path:         render(input) — file-inclusion adjacent
□ Name:         return "prefix/"+x — view-name — preprocessing
□ Attr:         th:${x} inside attr — expression-eval
□ Stored:       field → deferred render — richer/poorer context
□ Email:        mail-template — your inbox = the output channel
□ PDF:          gen-template — engine+wkhtmlto-double
□ Async:        queue/cron — privileged context, no request
□ Format:       fmt.format/input — format-string class (see
                format-string.md — attr-walk only, no calls)
```

Each position has its own "what objects are bound" inventory —
the reason one payload works on web-view but fails in email.
