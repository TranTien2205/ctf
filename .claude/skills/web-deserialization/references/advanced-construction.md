# Advanced Construction — the tricks past the basic chain

## The "gadget inside a data structure" trick — List/Map wrappers

The top-level object needn't be the gadget — wrap it in a collection the
entry `readObject`/`unserialize` walks:

```php
// PHP — an array whose element is the object:
a:1:{i:0;O:6:"Logger":1:{...}}
// a filter scanning for a top-level O: on the ROOT sees an a: — the
// gadget is nested inside the array
```

```java
// Java — a LinkedList/HashMap/TreeSet containing the gadget object
// the collection's readObject walks entries → fires the gadget's method
```

## The `__destruct`-only chain — skipping `__wakeup` entirely

If a chain's `__wakeup` resets the props, declare MORE props than supplied:

```
O:6:"Logger":3:{s:10:"\0*\0handler";O:11:"FileHandler":2:{...}}
             ↑ declares 3, supplies 1 → __wakeup skipped, __destruct fires
```

PHP <5.6.25 / <7.0.10 (CVE-2016-7124). The prop count is a LIE that survives
the grammar — `unserialize` accepts it.

## The multi-gadget cross-format smuggle

A blob that's simultaneously a valid pickle AND a valid PHP-serialize —
rare but possible where both parsers tolerate leading garbage. More
practically: a JSON doc carrying TWO typed fields where each app's parser
reads a different one.

## The `BUILD`/`__setstate__` second-stage — a chain inside the chain

```python
# pickle: the REDUCE fires a callable, then __setstate__ runs on the result:
#   return (SomeClass, args, the_state)
# the state dict reaches SomeClass.__setstate__ — a SECOND code path
```

A gadget that needs TWO code runs — the `__reduce__` callable to set up +
`__setstate__` to execute. phpgcc-style "two-stage" chains exist in PHP too
(the `R:`-referencing-object trick).

## The `TemplatesImpl` smuggle — code as DATA in the graph

```
TemplatesImpl → _bytecodes = a compiled .class file's bytes
             → newTransformer() → defineClass → static block runs
```

You don't smuggle a method name — you smuggle a WHOLE CLASS's bytecode.
The chain only needs `newTransformer` called on the object — Jdk7u21/CC.
`unsafe-reflection.md` covers the bytecode recipe.

## The "gadget is the constructor-arg" trick

Some classes' `readObject`/`__wakeup` reads a prop then passes it to a
factory — `new $prop->class()` or `Class.forName($prop)` — the class NAME
is a string prop → instantiate any class. The gadget's sink is "instantiate
a chosen class" → `TemplatesImpl`, `JdbcRowSetImpl`, `ScriptEngineManager`.

## The `Serializable` non-Serializable wrap

A field that must be a `Serializable` type but your payload class isn't —
wrap it in a `Serializable` container (a `Map.Entry`, a proxy, a
`LinkedList` element). The container satisfies the type; the element is
the gadget.

## The `serialVersionUID` patch — patching a captured stream

```bash
# a captured stream of the RIGHT class but wrong UID — patch the 8-byte UID:
# locate it via java_ser.py's classdesc dump, flip to the server's value
```

The exception's `local class incompatible: stream = A, local = B` tells you
the expected UID — patch the stream's UID to `B` and the parse succeeds.

## The `readResolve`/`writeReplace` swap

A `writeReplace`d class — the wire class differs from the code class.
When a gadget's entry class `writeReplace`s into a proxy, the stream's
classdesc is the PROXY's — a filter on the original class name misses it.

## The `long class name` UTF-8 smuggle

`TC_STRING` names are modified-UTF8 — `\xC0\x80` is a NUL in modified-UTF8.
`com.foo.Bar` padded with `\xC0\x80` inside = same class to the parser,
no longer matches a substring filter. Java-deep.md has the token grammar.

## The `classdescFlags` lie — `SC_WRITE_METHOD` + blockdata smuggle

A stream's classdesc can lie about `SC_WRITE_METHOD` — adding the flag makes
the parser expect a `TC_BLOCKDATA` tail where your custom bytes smuggle the
inner object. The field-table-only filter never reads the blockdata.

## The OOB-bridge — a chain that exists only to reach a second sink

Some chains don't RCE — they exist to reach a different sink:

```
deser → SoapClient → WSDL fetch          → proves + reaches remote
deser → JdbcRowSetImpl → JNDI            → a second exploitation stage
deser → file write → LFI the written file → a read-primitive chain
deser → file write → include the written → RCE via a different vector
```

The gadget's "impact" is sometimes just a pivot — the real sink is reached
a step later. Plan the two-step, not the one.

## The "no public chain fits" — the version-mix chain

A classpath with `commons-collections 3.2` + `commons-beanutils` + `groovy`
— pick whichever lib a chain exists for; the chain only needs ITS lib, not
all. Mixing gadgets across libs in one stream is possible if the entry
class resolves — a CC chain whose `AnnotationInvocationHandler` wraps a
BeanUtils gadget is valid if both libs exist.

## Output to record

- The specific trick that bypassed the basic-chain limit
- The verbatim response/OOB proving the advanced path worked
