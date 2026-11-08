# Class pollution in Python

The same merge idea, different runtime: a JSON body merged into a Python object
graph can walk the dunder chain — `__class__`, `__init__`, `__globals__`,
`__subclasses__` — to attributes the API never exposed. Where `__proto__` is
the JS door, `__class__` is the Python one.

## Probe shape that worked (TornadoService)

Fetch a public read endpoint to obtain a valid object id, then confirm the
write endpoint answers `403` for a direct request — the class pollution probe
must ride the *update* mechanism that is authorized, not the write the ACL
blocks.

```json
{"id": "<fetched-id>", "__class__": {"__init__": {"__globals__": {"marker": "pp"}}}}
```

Expected: the merge walked the dunder chain and an attribute on the class or
its globals changed — observable when the object is re-read or the affected
code path runs. Falsifier: the update rejects dunder keys, or the attribute is
unchanged on re-read.

## The walk

| Step | Reaches |
|---|---|
| `__class__` | the object's class |
| `.__init__.__globals__` | the module globals that defined the class |
| `.__subclasses__()` | every live subclass — the gadget catalogue |
| `__base__` / `__mro__` | parent classes — escape a sandbox subclass |

The sink that matters is whatever reads the polluted attribute next: a
rendered template, an `eval`/`exec`, a command the code builds, a config the
framework reloads.

## Falsifier

Dunder keys are stripped, the merge refuses non-data attributes, or the change
does not survive a second fetch — the object graph is not the merge target.

## Traps

- A merge that *creates* attributes on an instance (`__dict__`) is not class
  pollution — the write must reach shared state to be the class.
- The bot or job may be what re-reads the object; place the polluted state
  first, then poll for the effect (recorded trap).
