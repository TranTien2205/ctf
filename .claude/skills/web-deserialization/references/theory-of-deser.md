# Theory of Deserialization — the model underneath the payloads

## The core object — a constructor that skips the constructor

Every deserializer does the same trick: it builds an object WITHOUT calling
the constructor — `sun.misc.Unsafe.allocateInstance`, `Marshal` `allocate`,
pickle `__new__`, PHP `ReflectionClass::newInstanceWithoutCtor`,
`FormatterServices.GetUninitializedObject`. The init-time invariants the
class was *written* to hold are skipped — you supply the state directly.

```
normal:   new Logger()      → ctor runs → props get defaults + validation
deser:    allocate + set    → no ctor → props are whatever the stream says
```

The whole vulnerability class is **controlled state on an object the
constructor never validated** — the class trusts its own props because
"the ctor set them" — except you set them.

## Why it's a class, not a bug

A deserializer is safe if:
- it only instantiates classes whose *auto-called hooks* are safe, AND
- you can't influence which class/props arrive

The bug is always: attacker-controlled bytes → a parser that instantiates
typed objects → a hook (`__destruct`/`readObject`/`__reduce__`/setter) that
does something the props let you aim.

## The "instantiate anything" primitive

The deserializer hands you TWO things:

1. **class choice** — which class gets built (up to the classpath)
2. **prop control** — what that object's fields hold (up to type)

The leverage ceiling is the classpath — a gadget can only be a class the
app can load. The skill is routing "controlled class + controlled props" to
"a method call that matters".

## The hook — the part the app didn't write

The parser calls a hook you didn't ask for:

```
PHP    __wakeup / __unserialize / __destruct / __toString / __call / __invoke
Java   readObject / readResolve / hashCode / equals / compareTo / toString / validateObject / readExternal
Python __reduce__ / __setstate__ / BUILD
Ruby   marshal_load / _load / init_with
.NET   ISerializable ctor / OnDeserialized / setter
Node   $$ND_FUNC$$ revive + () / !!js/function + call
```

The hook is the *entrance* — the gadget is the path from the hook to the
sink. No hook → the object is inert data.

## The trampoline — hook → sink in N hops

```
hook fires on obj-1
  obj-1.hook calls obj-1.prop->method()       — prop is your choice
  obj-2 = the prop's class, whose method calls obj-2.prop->method()
  obj-3 = the sink class — its method does file/exec/eval/lookup
```

Each hop's METHOD NAME is fixed by the code; the OBJECT is yours. A chain
is a path through the classpath's own code — the gadgets are the reusable
trampolines.

## The classpath surface — what gadgets exist

The classpath is the ONLY source of trampolines — `vendor/`, `WEB-INF/lib`,
`site-packages`, the app itself. The gadget-catalog tools (phpgcc, ysoserial,
ysoserial.net) are *pre-built paths through common libs* — they exist
because the same libraries keep showing up on classpaths.

When no published chain covers the classpath → build a fresh one:
`gadget-construction.md` is the recipe.

## The serializer's check — `allowed_classes`/`Binder`/`find_class`/`safe_load`

Every serializer has a *type-resolution boundary* — the point where the
stream's class-name becomes a real class. A whitelist/blacklist lives there.

The bug survives when:
- a whitelisted class is itself a gadget
- the check is on the WRONG layer (the wrapper not the grammar)
- the check has a known gap (case, namespace, `C:`/`S:` types, nested)

## The signature layer — a different bug that shares the plumbing

A signed blob is *two* problems: the signature (a crypto problem) and the
deserialization (a grammar problem). The signature gates whether your bytes
reach the parser — `signature-bypass.md` is that module. The deserialization
bug only exists downstream of a signature you can satisfy.

## The "it's a parser" insight — the format IS the bug surface

Each format's PARSER is the bug surface — the grammar lets you name a class
+ set props. A stricter grammar (JSON, plain XML) has no typed-object
surface → no bug. The more the format can express, the bigger the surface:

```
JSON (data only)              → no typed objects → never deser
XML (data + schema)           → XStream/XMLDecoder add typed tags → deser
YAML (typed tags)             → typed tags → deser
PHP serialize (O:/a:/s:)      → typed objects → deser
pickle (opcode VM)            → a PROGRAM → full code
Marshal (typed graph)         → typed objects + load hooks → deser
BinaryFormatter (full graph)  → typed objects + callbacks → deser
```

## The "not really about objects" deeper truth

Deserialization isn't about objects — it's about **a parser that executes
the programmer's intent encoded as data**. The data IS the program. The
payloads differ per format but the primitive — "make the parser run code
the caller didn't write" — is identical. Every skill in this corpus is a
different spelling of that one primitive.
