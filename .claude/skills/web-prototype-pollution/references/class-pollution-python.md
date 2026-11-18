# Class pollution (Python) — attribute paths to the deciding check

The Python twin of prototype pollution: a routine walks dotted
attribute names on an object — `setattr(obj, name, value)` in a loop,
a recursive `update`, a document-store path — and the attribute name
is attacker-shaped. The reachable targets are `__class__`,
`__globals__`, `__init__`, `__subclasses__`, and every module-level
name those reach.

---

## 1. The primitive vs the JS one

JS writes onto `Object.prototype` — a single shared object every `{}`
inherits. Python has no single root; the equivalent targets are:

- the class object (`__class__`) — every instance shares it
- the module globals (`__globals__`) — every function in that module
  sees them
- the builtins (`__builtins__`) — global to the interpreter
- a specific module attribute (`sys.modules`, `os.environ`)

So Python pollution names a PATH, not a key: you don't pollute a
marker, you overwrite the attribute a later read resolves through.

## 2. The canonical paths

```
instance.__class__.__init__.__globals__
instance.__class__.__module__            → module name (string)
instance.__class__.__bases__             → parent classes
instance.__class__.__mro__               → the resolution order
instance.__class__.__subclasses__()      → every loaded subclass
instance.__class__.__init__.__globals__['SECRET']
instance.__class__.__init__.__globals__['os']
instance.__class__.__init__.__globals__['__builtins__']
```

`__globals__` is the payoff — it is the function's module namespace,
writable, and it holds imports, config values, and the flag-shaped
secrets the module imported.

## 3. Where the write comes from

**setattr loop** — the app walks `request.json` applying
`setattr(obj, k, v)`:

```python
for k, v in payload.items():
    setattr(obj, k, v)   # k = "__class__" reaches the class
```

The primitive is per-key: `__class__` as a top-level key gets the
class object itself rebound — usually a crash, but combined with a
second update it re-instantiates with different behaviour.

**Dotted-path setter** — `set(obj, "a.b.c", value)` split on `.`:

```python
path = "profile.__class__.__init__.__globals__.debug"
set(obj, path, True)
```

Each intermediate segment is `getattr` — a walk into whatever the
object graph exposes. `__class__` anywhere in the path escapes the
instance.

**Document-store path syntax** — a Mongo-style `{"$set":
{"a.b": v}}` against a Python object graph, or the app's own dotted
API (`PATCH /obj {"a.b.c": 1}`).

**Pickle/other deserializers** — adjacent class; see
`skills/web-deserialization/`. Class pollution proper is the
attribute-write path, not the object graph.

**The bot-relayed write** (TornadoService — confirmed): the write
endpoint answered 403 locally, so a bot/admin-relay carried the
pollution — the write went through, the class attribute changed, and
the app's global setting flipped. The CSRF was the delivery; the
class attribute was the bug.

## 4. The useful attribute targets

| Path | What it buys |
|---|---|
| `__class__.__init__.__globals__['DEBUG']` | flip debug on |
| `__class__.__init__.__globals__['SECRET_KEY']` | read/overwrite the session key |
| `__class__.__init__.__globals__['app'].config` | app config — `FLAG`, `ADMIN` |
| `__class__.__init__.__globals__['verify']` | replace the check function |
| `__class__.__init__.__globals__['os'].environ` | env vars |
| `__class__.__hash__`/`__eq__`/`__repr__` | corrupt the class's own behaviour |
| `__class__.__subclasses__()[i]` | reach another class entirely |
| `__class__.__init__.__globals__['__builtins__']['eval']` | eval hook |

Any `__globals__` key the later code reads is a gadget — the map from
attribute to sink is `gadget-index.md`.

## 5. The safe-marker protocol

Before writing anything security-relevant, prove the path with a
harmless attribute:

1. Pick a module-level name that exists and is read somewhere visible
   (a `title`, `version`, or `name` string).
2. Write `__class__.__init__.__globals__['<name>'] = 'marker'` via the
   path primitive.
3. Re-read wherever the name surfaces (a rendered page, a JSON field).

The class-attribute write is process-global — same blast radius as JS
pollution, and on a shared instance you are changing the app for
everyone until restart. Use the narrowest target.

## 6. The `__globals__` inventory

The module namespace the function's globals exposes — typical keys
worth probing when you can list them (debugger, error, or the
attribute-walk itself):

```
SECRET_KEY  FLAG  ADMIN_TOKEN  DEBUG  TESTING  ENV  CONFIG  config
settings  app  application  db  session  cache  redis  mongo  engine
os  sys  subprocess  eval  exec  compile  open  __import__  globals
locals  vars  dir  getattr  setattr  delattr  hasattr  type  object
super  isinstance  issubclass  callable  iter  next  repr  str  int
hash  id  help  exit  quit  license  credits  copyright
```

On a CTF target `FLAG`/`SECRET`/`KEY`-shaped names are the win; on a
real target the same names gate the next hop.

## 7. Falsifiers

- The setter rejects `__`-prefixed segments — try URL-encoding the
  segment, splitting across keys (`{"a":{"__class__":...}}`), or the
  numeric `__subclasses__` route.
- `setattr` on a class attribute raises `AttributeError`/`TypeError`
  for read-only descriptors — the error echo tells you which segment
  failed; the walk up to that segment still ran.
- The written value is coerced (int→str) before the read — pick a
  target where a string is still effective (a name, a path, a flag
  string, a truthy value).

## 8. Framework-specific surfaces

- **Flask**: `request`, `session`, `g`, `current_app` proxies —
  `current_app.config` is a dict; `config.update(req.json)` is a
  direct merge into the app config.
- **Django**: `settings.configure`/`django.conf.settings` —
  `settings.DEBUG` reachable through `__globals__`.
- **Jinja2**: `{{ ''.__class__.__mro__[2].__subclasses__() }}` is the
  SSTI equivalent — same walk, different carrier.
- **grpc/protobuf** (Artificial University — confirmed): protobuf
  message fields accept attribute assignment; a handler applying
  `setattr` per field reached an `eval`-adjacent global — the gRPC
  reflection of the schema told you which field names existed.

## 9. The read primitives

After a successful write, confirm through:

- the rendered output carrying the new value,
- a JSON field reflecting the module global,
- a behaviour flip (debug page appearing, 403→200, a gate opening),
- `__globals__` listing via a second walk.

No readback means no confirm — `inconclusive`, not `confirms`.
