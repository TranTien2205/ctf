# Serializer Hardening — reading the defense, finding the gap

## The defense layers — what the app may have

```
1. input validation   → regex on the bytes before the parser
2. class whitelist    → allowed_classes / Binder / find_class / safe_load
3. signature/MAC      → HMAC over the blob
4. encryption         → AES/RSA around the blob
5. type restriction   → accept only one class / one field
6. depth/size limit   → ObjectInputFilter limits
7. container check    → expect the root to be a Map/List/scalar
8. a canary field     → reject if a known field is absent/present
```

## Reading the whitelist — the gap inside it

### PHP `allowed_classes`

```php
unserialize($x, ['allowed_classes' => ['User','Session']]);
```

- the whitelist is a LIST — a class on it can be the gadget
- `Session`/`User` themselves may have a `__wakeup`/`__destruct` — the chain
  lives inside an allowed class
- `allowed_classes` only gates O:-objects — `a:`/`s:`/`i:`/`b:`/`N:`/`R:`/
  `C:`/`S:` types still pass — an `a:` of props, or a `C:` Serializable-
  class bypasses it
- the check is the class NAME — a namespaced lookalike (`app\user` vs
  `App\User`) may confuse a weak comparison

### Python `find_class`/`Unpickler`

```python
def find_class(self, mod, name):
    if mod in {'safe.mod','builtins'}:
        return super().find_class(mod,name)
    raise UnpicklingError(mod)
```

- `builtins` whitelisted → `eval`/`exec`/`getattr`/`__import__`/`map`/`open`
  are all builtins → full sink still reachable
- `__main__` whitelisted → any class in `__main__` is a gadget
- `copyreg`/extension-registry opcodes bypass `find_class`
- a whitelisted module that RE-EXPORTS (`from os import system` re-exported
  as `safe.mod.system`) → the whitelist checks `mod`, you get `os.system`

### Java `ObjectInputFilter`/`resolveClass`

```java
ois.setObjectInputFilter(info ->
    switch (info.serialClass().getName()) {
        case "com.app.Safe" -> Status.ALLOWED;
        default -> Status.REJECTED;
    });
```

- a whitelisted class that IS a gadget (`com.app.*` includes a gadget)
- `UNDECIDED` vs `REJECTED` — a filter that returns UNDECIDED for unknown
  classes lets them through the default behavior
- `depth`/`arrayLength`/`streamBytes` limits — a chain under the limits
  still lands
- `resolveClass` override — the override's own `Class.forName` is the gate;
  a class it loads by name can still be a gadget

### .NET `SerializationBinder`

```csharp
binder.BindToType(asm, typeName) {
    if (!whitelist.Contains(typeName)) throw ...
}
```

- the whitelist is by TYPE-NAME — a whitelisted framework type
  (`ObjectDataProvider`, `TypeConfuseDelegate` is a gadget anyway)
- the check is on the top-level type — a nested type inside an allowed
  container may bypass it
- a binder that remaps `X`→`Y` — the remap target may be a gadget

### YAML `safe_load`/`SafeConstructor`/`permitted_classes`

- `permitted_classes:[Symbol,Date]` — `Symbol`/`Date` alone don't chain,
  but a permitted class WITH a hook does
- `add_constructor`/`add_multi_constructor` — a registered tag routes to
  the app's own function — the danger is the function
- `yaml.load` is still `UnsafeLoader`-ish in older PyYAML — the version
  decides

## The signature-check gaps

- `hash_hmac` with a leaked key → forge
- `alg=none`/kid/jku/confusion → `signature-bypass.md`
- a signature checked AFTER `unserialize` (wrong order) → the blob is
  already parsed when the sig fails
- `hash_equals` vs `==` — a non-constant-time compare → timing oracle
  (rarely exploitable but real)

## The "container check" gap

```php
if (is_array($x) && isset($x['ok'])) unserialize($x['ok']);
// the check is on the WRAPPER — $x['ok'] can still be O:...
```

- the check validates the CONTAINER, not the bytes → your gadget inside
- a "must start with `a:`" check → wrap the O: inside `a:1:{i:0;O:...}`

## The encoding-check gap

```php
if (strpos($x, 'O:') !== false) die;   // blocks the literal 'O:'
```

- `O:+4:` signed length — the regex `O:\d` misses it
- `S:` hex-escape the `O` inside a string — `S:1:"\4f";`
- a second format the check doesn't know — igbinary/`C:`/phar metadata
- `gzuncompress`/`base64_decode` before the check — the check scans the
  wrapper, not the grammar

## The hardening that's actually correct

- `safe_load`/`allowed_classes=false`/`Binder` whitelist + NO permitted
  gadget class + no other sink → the class is truly closed
- encryption (not signing) with an unreachable key → no grammar access
- `unserialize` never called on the value (stored verbatim only) → no parser

## The "which layer is the gap" table

| Defense | The usual gap |
|---|---|
| regex blacklist | signed-length/`S:`-escape/alternate format |
| class whitelist | a whitelisted class's own gadget |
| signature | key-leak/alg=none/kid/confusion |
| encryption | padding-oracle/key-leak |
| container check | the check validates the wrapper not the grammar |
| encoding check | the check scans the wrapper not the decoded bytes |
| type restriction | the one allowed class is itself the gadget |

## Output to record

- Which defense layer was present + the gap inside it
- The verbatim bypass payload + the response proving it landed
