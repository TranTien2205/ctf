# Primitives — what a deserializer actually hands you

## The core primitive — controlled class instantiation

Every deserialization bug reduces to the same thing: **you choose which
class gets instantiated and what its properties hold**, inside a process
that trusts the result. Code never crosses the wire — *class names and
property values* do, and the target's own code does the rest.

```
attacker sends:   O:"Logger":{handler:O:"FileHandler":{file:"/x",data:"y"}}
target builds:    new Logger → Logger->handler = new FileHandler(file,data)
target calls:     __destruct → handler->close() → file_put_contents
```

Your leverage is bounded by what's *on the classpath/in the autoloader* —
you can only instantiate classes the app can already load.

## The four sub-primitives

### 1. Property injection — set any prop to any value

`{name:"admin", role:"admin"}` on an allowed class — no code, just state.
Impact: auth bypass (`is_admin:true`), config tamper, IDOR via object graph.

### 2. Method trampoline — make a hook call a useful method

A magic `__destruct`/`readObject`/`OnDeserialized` calls
`$this->handler->close()` — `handler` is a prop you control → pick a class
whose `close()`/`__toString()`/`compare()` does the sink.

### 3. Callable invocation — make a method run a chosen callable

`call_user_func($this->fn, $this->arg)` / `Method.invoke` / `__invoke` /
`EventHandler.action` → your chosen function on your chosen args → RCE.

### 4. File/resource op — make a file op run on a chosen path

`file_put_contents($this->path, $this->data)` / `unlink($this->f)` /
`FileOutputStream` / `AspectJWeaver` write → file write/delete/read.

## The leverage map — per language

| Lang | Instantiate | Props | Hook methods | Reachable sink |
|---|---|---|---|---|
| PHP | any class in autoloader | full control | `__wakeup`/`__destruct`/`__toString`/`__call`/`__invoke` | eval/system/file ops/SoapClient URL |
| Java | any Serializable class on classpath | fields (typed) | `readObject`/`readResolve`/`hashCode`/`equals`/`toString`/`invoke`/`compare` | Method.invoke→exec, JNDI, file write |
| Python | any class `find_class` allows | `__dict__`/state | `__reduce__`/`__setstate__`/`BUILD` | any callable → os/subprocess/eval |
| .NET | any `ISerializable`/serializable | fields | `ISerializable` ctor/`OnDeserialized`/setters | ObjectDataProvider method, Process.Start |
| Ruby | any class in `const_get` | ivars | `marshal_load`/`_load`/method_missing | ERB eval, Gem::Requirement exec, system |
| Node | revived object graph | props | `$$ND_FUNC$$`+`()`, `!!js/function`+call | child_process.exec, require |

## The leverage ceiling — what you CANNOT do

- Instantiate a class the autoloader/classpath/serializer can't resolve.
- Control a private/protected prop unless the serializer lets you set it by
  name (PHP `\0*\0` does; Java field-table does; Json.NET setters only).
- Reach a sink that requires a constructor arg — deserializers skip ctors
  (Unsafe/FormatterServices/marshal allocate, pickle `__new__`).
- Bypass a `SerializationBinder`/`find_class`/`allowed_classes`/`safe_load`
  whitelist except via a permitted class's own gadget.
- Sign or encrypt your blob — that's the signature problem, separate.

## Reading a class for gadget potential — the checklist

```
□ a magic method (the hook) — which fires on this class?
□ the hook touches $this->prop → can that prop be another object?
□ the hook calls a method on the prop → does any class on the
  classpath have a same-named method that does the sink?
□ the sink itself — a callable-invoke, file-op, URL-fetch, or eval?
□ the trigger — does anything else have to happen (request end,
  toString use, a later method call) for the sink to fire?
```

## The "gadget" — a name for a reusable trampoline

A gadget isn't magic — it's a class whose hook-chain reaches a sink through
*properties you control*. `InvokerTransformer.transform` runs
`Method.invoke` on a method-name prop. `EventHandler.action` runs a named
method. `ObjectDataProvider` calls a named method on a named object. The
gadget's value is that the *sink name is data* — you choose it per-target.

## The "POP chain" — composing trampolines

```
entry (a magic method that calls $prop->x())
 → gadget-1 (x() reads another prop → calls its method)
 → gadget-2 (that method calls a callable on a third prop)
 → sink (a function call / file op / URL fetch)
```

Each hop's method name is fixed by the class; the *objects* are yours.
A chain is a path through the classpath's own code.

## The "property-only" class

Some useful chains need no magic method at all — an object whose mere
construction reaches a sink: `__destruct` on a logging class flushing to a
path you own; a `HashMap.readObject` rehash; a `Serializable` whose field
is a `TemplatesImpl` that compiles on `newTransformer`. The hook can be the
deserializer itself re-hashing/re-resolving.
