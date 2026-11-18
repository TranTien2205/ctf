# Magic-Method Table — the per-language hook index

## The primitive — every deserializer calls a hook you didn't ask for

A gadget chain is *a path from an automatic hook to a sink*. The hook fires
because the language/runtime calls it, not because the app does — your only
job is to make the object be the right class with the right props.

## PHP — `unserialize()` firing order

```
unserialize($blob)
  → build the object graph (properties set directly, no ctor)
  → __wakeup()    on each object, in creation order
  → (or __unserialize($data) on PHP≥7.4 classes)
  → request ends → __destruct() on each, reverse order
  → later: any use of the object → __toString/__get/__set/__call/__invoke
```

| Hook | Fires on | Chain use |
|---|---|---|
| `__wakeup` | end of unserialize | log/reset — first hook |
| `__unserialize` | PHP≥7.4 (replaces __wakeup) | same role |
| `__destruct` | GC/request end | file write, close, flush — the reliable one |
| `__toString` | string context | call into another object's method |
| `__get/__set` | missing prop | pivot |
| `__call` | missing method | named-method trampoline |
| `__invoke` | used as fn | call_user_func pivot |

## Java — `readObject()` hook order

```
OIS.readObject()
  → resolveClass (filter point — JEP-290 / whitelist)
  → instantiate (skip ctor — sun.reflect.Unsafe-style alloc)
  → readObject() / defaultReadObject() per class  ← THE HOOK
  → readResolve() (substitute result)
  → validateObject() (if registered)
  → readExternal() for Externalizable classes
  → finalize() later — unreliable
```

| Hook | Fires on | Chain use |
|---|---|---|
| `readObject` | the class's own read | gadget entry — collection rehash/walk |
| `readResolve` | after fields | substitute — rare as a sink |
| `hashCode/equals/compareTo/toString` | collection ops inside readObject | THE gadget method |
| `readExternal` | Externalizable | arbitrary code by design |
| `finalize` | GC | unreliable trigger |

## Python — `pickle.loads` hook order

```
loads(bytes)
  → VM executes opcodes
  → GLOBAL/STACK_GLOBAL → find_class(mod,attr)  ← filter point
  → REDUCE → callable(*args)                     ← __reduce__ result
  → BUILD  → obj.__setstate__(state)             ← second hook
  → INST/OBJ/NEWOBJ → instantiation paths
```

| Hook | Fires on | Chain use |
|---|---|---|
| `__reduce__`/`__reduce_ex__` | what the stream asked | returns callable+args → REDUCE |
| `__setstate__` | BUILD opcode | second code path after reduce |
| `find_class` (unpickler-side) | every GLOBAL | the security boundary |
| `__init__` | rarely — pickle skips it | note: pickle does NOT call __init__ |
| `__getattr__` | attr access during build | pivot |

## Ruby — `Marshal.load` / `Psych.load`

```
Marshal.load
  → allocate the object (no initialize)
  → marshal_load(data) / _load(str)     ← THE HOOK
  → ivars set
  → (later) method calls on the object
```

| Hook | Fires on | Chain use |
|---|---|---|
| `marshal_load`/`_load` | `u:`/`U:` types | arbitrary code in the hook |
| `initialize` | only if called later | weaker |
| `method_missing` | dispatch inside gadget | trampoline |
| `Psych` `init_with`/`yaml_as` | `!ruby/object` tags | YAML-side equivalent |

## .NET — BinaryFormatter hook order

```
BinaryFormatter.Deserialize
  → SerializationBinder.BindToType (filter point)
  → instantiate (FormatterServices — no ctor)
  → ISerializable ctor (info, context)           ← THE HOOK
  → OnDeserializing/OnDeserialized attrs
  → IDeserializationCallback.OnDeserialization
```

| Hook | Fires on | Chain use |
|---|---|---|
| `ISerializable` ctor | on deserialize | gadget entry |
| `OnDeserialized`/`IDeserializationCallback` | after fields | gadget sink — e.g. `Process.Start` via a property |
| `SerializationBinder` | per type | the filter to bypass |
| property setters | XmlSerializer/Json.NET | weaker — needs ObjectDataProvider |

## Node.js — revive + invoke

```
node-serialize.unserialize
  → JSON.parse with a reviver
  → _$$ND_FUNC$$_ string → new Function() → revived function
  → trailing () → IIFE invoke                      ← THE SINK
```

| Hook | Fires on | Chain use |
|---|---|---|
| `$$ND_FUNC$$` revive | the tag string | builds the function |
| `()` auto-invoke | the trailing call | runs it — THE trigger |
| `!!js/function` | js-yaml ≤3 | revived function — needs a later call |

## The read-across — which hook to hang your payload on

| Want | Hang it on |
|---|---|
| reliable fire, no app cooperation | `__destruct`/`readObject`/`REDUCE`/`marshal_load`/`ISerializable ctor` |
| fire only when used | `__toString`/`toString`/`OnDeserialized` |
| a second code path | `__setstate__`/`BUILD`/`readResolve`/`validateObject` |
| the "safe" bypass | `allowed_classes` gap / `find_class` whitelist gap / `Binder` gap |
