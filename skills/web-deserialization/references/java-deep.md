# Java Serialization — TC_STREAM internals and hand-crafting

## Full token grammar

```
STREAM: AC ED 00 05 then a sequence of:

74  TC_OBJECT      → classDesc + field data
  72  TC_CLASSDESC   → classDescFlags, field count, fields, annotation, superDesc
    71  TC_REFERENCE   → u32 handle back-pointer (handles start at 0x7E0000)
    70  TC_NULL
    76  TC_STRING      → u16 len + utf8 (long: 7F TC_LONGSTRING + u64 len)
    75  TC_ARRAY
    73  TC_CLASS       → classDesc (a class object, not an instance)
    78  TC_BLOCKDATA   → u8 len + opaque bytes
    77  TC_BLOCKLONG   → u32 len + opaque
    7A  TC_RESET
    79  TC_ENDBLOCKDATA
    7B  TC_EXCEPTION
    7E  TC_ENUM
    74  TC_OBJECT nested
  classDescFlags: SC_WRITE_METHOD(1) SC_SERIALIZABLE(2) SC_EXTERNALIZABLE(4)
                  SC_BLOCKDATA(8) SC_ENUM(0x10)
```

## The annotation section — where gadgets hide

After each classdesc's field table comes a **classAnnotation** block of
arbitrary `contents[]` until `TC_ENDBLOCKDATA`. The gadget frameworks smuggle
the whole `templates`/`handler` object graph inside annotations — that is
why a raw `AC ED` blob is unreadable as JSON but `java_ser.py` still walks it.

## The handle-table trick — TC_REFERENCE cycles

Every OBJECT/STRING/CLASSDESC/ARRAY/ENUM allocates a handle
`0x7E0000, 0x7E0001, ...`. `TC_REFERENCE <handle>` reuses an earlier slot —
this is how circular graphs are encoded, and how a corrupt stream can point
a field at a DIFFERENT class's object (type confusion inside the graph).

## Field serialization order

Fields serialize in declared order of the classdesc — NOT the order the
gadget's author wrote them. A hand-crafted stream that mis-orders the
`serialVersionUID`, `flags`, or field list is rejected with
`StreamCorruptedException`. Always copy the classdesc layout from a REAL
stream of the same class (capture → `java_ser.py` → mimic the layout).

## Long-class-name smuggling — the parser-quirk bypass

Some WAFs/filtering deserializers scan for gadget class names in the stream.
Two bypasses:

1. **TC_REFERENCE indirection** — name the gadget class ONCE, then
   reference it by handle everywhere else.
2. **UTF-8 long-form / modified-UTF8 tricks** — a class name padded with
   `\xC0\x80` (modified-UTF8 NUL) is the SAME class to the deserializer but
   no longer matches a substring filter.

## Custom-writeObject escalation

A class with `SC_WRITE_METHOD` carries a `blockdata` tail AFTER its fields —
the app's `writeObject` wrote it, `readObject` reads it as raw bytes. The
gadget payload often lives there. When `java_ser.py` shows
`classdata + N bytes TC_BLOCKDATA`, that blob is the smuggled inner object.

## Externalizable — the code-is-data case

`classDescFlags & SC_EXTERNALIZABLE` → the class reads ITSELF via
`readExternal()`. No field table — the whole object is one opaque blob. An
`Externalizable` gadget (e.g. a bean that runs a script in `readExternal`)
carries its exploit in-band. Filter rules written for field-table streams
don't see it.

## The `Collections.unmodifiable*` wrappers — readObject entry points

The top-level object is rarely the gadget — it's a wrapper whose
`readObject` walks into the gadget:

```
PriorityQueue.readObject → heapify → comparator.compare(o1,o2)
HashMap.readObject       → put → key.hashCode()
Hashtable.readObject     → reconstitutionPut → equals()
AnnotationInvocationHandler.readObject → memberValues.entrySet → ...
BadAttributeValueExpException.readObject → val.toString()  (CC5)
```

Each is a different entry class, same sink. Pick the wrapper by WHICH method
your gadget implements (`compare`/`hashCode`/`equals`/`toString`/`invoke`).

## Proxy — the InvocationHandler trampoline

`AnnotationInvocationHandler` is a `java.lang.reflect.InvocationHandler` —
it wraps an interface (Map.Entry, Map, Comparable). ANY method call on the
proxy dispatches to `invoke()` which reads `memberValues`. The CC chains
hang a `LazyMap`/`TransformedMap` behind it so `invoke` → `get` →
`transform` → `InvokerTransformer` → exec. The proxy is the trampoline; the
transformer chain is the payload.

## The byte-level recipe — patch a captured stream

```bash
# capture a real stream for the same class, walk it
python3 tools/java_ser.py legit.ser

# the bytes you change are:
#   - TC_STRING payloads (the command string) — length-prefixed, patch len too
#   - the classdesc field values
#   - the handle references stay valid if you only change leaf strings
```

Patching a captured stream of a KNOWN-good gadget is far more reliable than
building from scratch — keep every handle and annotation byte, change only
the leaf `TC_STRING` carrying the command (and its u16 length).

## Falsifiers inside the format itself

- Stream header is `AC ED` but version isn't `00 05` → not a real OIS stream.
- A `serialVersionUID` mismatch error proves the class exists — it is NOT a
  parser failure, it is a version leak.
- `ObjectInputFilter: REJECTED` → a JEP-290 filter is live — only its
  whitelisted classes can chain.
