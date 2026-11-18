# Per-Language Quirks — the details that change the answer

## PHP quirks

### `unserialize` is forgiving — until it isn't

- trailing garbage after the grammar is ignored
- leading whitespace is tolerated in some builds
- `O:+4:"X"` signed lengths are accepted
- a length lie inside the grammar errors — the offset is the tell

### `allowed_classes` semantics

```php
unserialize($x);                                  // all classes — default
unserialize($x,['allowed_classes'=>true]);        // all classes
unserialize($x,['allowed_classes'=>false]);       // NONE — O: refused
unserialize($x,['allowed_classes'=>['A','B']]);   // only A,B
unserialize($x,['allowed_classes'=>[]]);          // empty list = none
```

Case-insensitive class-name matching; namespaces count — `App\User` ≠ `User`.

### The `S:` vs `s:` type

- `s:` bytes-as-is — a literal `\x00`/`'` is literal
- `S:` `\xNN` escapes — decoded on parse; survives mangle

### `__unserialize` vs `__wakeup` (PHP ≥7.4)

`__unserialize(array $data)` replaces `__wakeup` — receives the raw prop
array, not the object. A class defining `__unserialize` uses it INSTEAD of
`__wakeup`. Check the PHP version + which method the class defines.

### `unserialize_callback_func`

```php
ini_set('unserialize_callback_func', 'autoload');
```

A class-not-found → the callback runs (usually autoload). If the callback
`include`s a file by the class name → a path-injection into a file-load —
`O:8:"../../etc/x":0:{}` → autoload a path.

## Java quirks

### `serialVersionUID` — the versioned contract

- mismatch → `InvalidClassException` — but the error LEAKS the expected UID
- `static final long serialVersionUID = <n>` in source pins it
- a class WITHOUT explicit UID gets a computed one — changes on recompile

### `transient`/`static` don't serialize

- `transient` fields are skipped — a gadget prop must NOT be transient
- `static` fields aren't in the stream — class-level, not object
- `serialPersistentFields` overrides the field list — read THAT not the class

### `readResolve`/`writeReplace` swap objects

- `writeReplace` → the wire class differs from declared
- `readResolve` → the result object is substituted after fields

### `ObjectInputFilter` (JEP-290, Java 9+)

```java
ois.setObjectInputFilter(info ->
    info.serialClass().getName().startsWith("com.app.") ? ALLOWED : REJECTED);
```

Filters on class name, depth, arrayLength, streamBytes — `REJECTED`/`UNDECIDED`
status. Bypass: a whitelisted class carrying a gadget, or filter-logic gap.

## Python quirks

### `pickle.loads` vs `pickle.load`

- `loads(bytes)` — the byte-string sink
- `load(file)` — the file-object sink — a file-path param
- `encoding='bytes'` vs `'ASCII'`/`'latin-1'` — a p0 protocol detail

### `__init__` is NOT called

pickle skips `__init__` — the object is built by `__new__`+state. A gadget
in `__init__` never fires on unpickle — `__reduce__`/`__setstate__`/`BUILD`
are the hooks.

### `find_class` — the real boundary

```python
class R(Unpickler):
    def find_class(self, m, n):
        if m in OK: return super().find_class(m,n)
        raise UnpicklingError(m)
```

Called once per GLOBAL/STACK_GLOBAL — the whitelist. Bypass: a whitelisted
module re-exporting a dangerous name.

### p0 vs p3+ bytes

`pickle.dumps(obj,0)` is ASCII — survives 7-bit channels. `80 03` prefix is
binary. A strict-ASCII channel forces protocol 0.

## Ruby quirks

### Marshal version

`\x04\x08` = Marshal 4.8 — Rails-era standard. `Marshal.load` checks the
version byte — `dump format error` on a wrong version.

### `safe_load` permitted_classes

```ruby
YAML.safe_load(x)                                   # basic types only
YAML.safe_load(x, permitted_classes:[Symbol])       # + Symbol
YAML.safe_load(x, permitted_classes:[Symbol,Date])  # + Date
```

`Symbol`/`Date`/`Time`/`Range`/`Regexp` are the usual permitted extras —
none reach a gadget alone, but a class that IS permitted and does have a
hook is the bypass.

## .NET quirks

### `SerializationBinder` — the type-name boundary

```csharp
binder.BindToType(assembly, type) → returns the type — can reject/remap
```

A custom binder is the whitelist — a type NOT in its map throws. Bypass:
a whitelisted type that reaches a gadget (`ObjectDataProvider` is often
whitelisted because it's a "safe" framework type).

### `TypeNameHandling` levels (Json.NET)

```
None      → ignores $type — safe
Auto      → $type only when it differs from declared — often safe-ish
Objects   → $type honored — UNSAFE
Arrays    → $type honored on arrays — UNSAFE
All       → $type honored everywhere — UNSAFE
```

`Auto` is subtle — only fires when `$type` ≠ the declared type — a
`$type` that IS the declared type's subclass/different resolves it.

## Node quirks

### `_$$ND_FUNC$$_` needs `()`

The revived function only auto-invokes with trailing `()` — no `()` =
revived-but-inert.

### `JSON.parse` is never deser

`JSON.parse` builds data — `node-serialize`/funcster/`devalue`+reviver is
the sink. A plain `JSON.parse` is a falsifier.

## YAML cross-cutting

- `yaml.load`/`UnsafeLoader`/`new Yaml()` — unsafe
- `safe_load`/`SafeLoader`/`SafeConstructor` — data-only (unless extended)
- `FullLoader` — partial — rejects apply/new, allows object
- custom `add_constructor`/`permitted_classes` — the app-side surface
