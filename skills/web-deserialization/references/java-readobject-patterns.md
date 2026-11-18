# Java readObject Patterns — what the app's own code looks like

## The sink signatures — grep-first

```java
// the direct sinks:
ObjectInputStream ois = new ObjectInputStream(in);
Object o = ois.readObject();
Object o = ois.readUnshared();

// the wrapped sinks:
new ObjectInputFilter...                     // a JEP-290 filter — the obstacle
new ValidatingObjectInputStream(in)           // Apache commons-io whitelist
new XStream().fromXML(reader)                 // XML-family sink
new XmlDecoder(in).readObject()               // XML beans
new Yaml().load(reader)                       // Snakeyaml
new Hessian2Input(in).readObject()            // Hessian
new Kryo().readClassAndObject(in)             // Kryo
JSON.parse / JSONObject.parse / fastjson.parse // fastjson
mapper.readValue(..., defaultTyping)          // Jackson polymorphic
```

## The readObject custom logic — what to look for INSIDE the app's class

```java
// the class's own readObject — often the real entry:
private void readObject(ObjectInputStream ois) {
    ois.defaultReadObject();              // fields filled
    this.handler.close();                  // ← calls a field's method — THE hook
}
```

The pattern to hunt: `readObject` that calls a method on a FIELD —
`handler.close()`, `comparator.compare(a,b)`, `key.hashCode()`. The field is
the prop you control; the method it calls is the trampoline.

## The field-table shape — what you control

```java
class Logger implements Serializable {
    private Handler handler;    // ← you set this — it's the trampoline
    private String path;        // ← you set this — the arg
}
```

A `Serializable` field you can set = a sub-object slot. The chain is:
top object's `readObject` calls `field.method()` → field is your gadget
class → its method does the sink.

## The `transient`/`serialPersistentFields` trap

```java
private transient Handler handler;        // NOT serialized — you can't set it
private static final long serialVersionUID = ...;
```

`transient` fields don't round-trip — a gadget depending on a transient
field can't be delivered. `serialPersistentFields` override the declared
fields — read THAT table, not the class fields.

## The `readResolve`/`writeReplace` substitution

```java
private Object readResolve() {
    return new OtherClass(...);           // the result object is swapped
}
private Object writeReplace() {
    return new Proxy(...);                 // the wire object differs from the class
}
```

`writeReplace` means the serialized bytes hold a DIFFERENT class than the
code declares — the stream's classdesc names the replaced class. When a
source says `Session` but the stream says `SessionProxy`, `writeReplace` ran.

## `Externalizable` — the opaque-blob class

```java
class X implements Externalizable {
    public void readExternal(ObjectInput in) {
        this.data = in.readObject();       // reads ARBITRARY bytes — opaque
        Runtime.exec(...);                 // often the sink is inside
    }
}
```

An `Externalizable` class's stream has NO field table — the payload is a
raw blob the class parses itself. Any field a WAF scans for is invisible.
Gadget classes implementing `Externalizable` carry the exploit in-band.

## The `InvocationHandler`/proxy boundary

```java
// AnnotationInvocationHandler is a proxy handler:
//   memberValues = a Map the handler reads on ANY method call
// the serialized form: <proxy> + <AnnotationInvocationHandler handler>
// the map's entries are the gadget — 'get'/'entrySet'→transform→invoke
```

`java.lang.reflect.Proxy` serializes as the interface + the handler — the
handler's `memberValues`/`interceptors` field is the payload. The proxy is
the trampoline that turns ANY method call into `invoke()`.

## `Serializable` vs `Externalizable` flags in the classdesc

```
classDescFlags byte:
  SC_WRITE_METHOD   0x01   has readObject/writeObject → has blockdata
  SC_SERIALIZABLE   0x02   normal Serializable
  SC_EXTERNALIZABLE 0x04   opaque blob — no field table
  SC_BLOCKDATA      0x08   external data in blockdata
  SC_ENUM           0x10   enum
```

`java_ser.py` prints these per classdesc — `SC_EXTERNALIZABLE` means the
field table is absent and the payload is opaque.

## The app's own gadget — a class nobody publishes

CTF apps carry a *purpose-built* gadget:

```java
public class FlagLoader implements Serializable {
    private String path;
    private void readObject(ObjectInputStream ois) {
        ois.defaultReadObject();
        Files.readAllBytes(Paths.get(this.path));     // ← the sink
    }
}
```

A custom class with `readObject`/`finalize`/`toString` touching a field —
read EVERY Serializable class in the handout source for the one whose hook
does something useful. This is more common in CTF than a public-lib chain.

## The `ObjectInputFilter` / JEP-290 boundary

```java
ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
    "com.app.allowed.*;!*");               // only com.app.allowed classes
ois.setObjectInputFilter(filter);
```

A filter rejects non-whitelisted classes — `REJECTED` status on your gadget
= the filter is live. Bypass: a whitelisted class that itself has a gadget
(`com.app.*` classes often include the app's own gadget); or an
`arrayLength`/`depth` filter bypass via a deep/long stream.

## The "this class isn't Serializable" problem

Not every class can be a gadget — it must implement `Serializable` (or be a
special type). `java_ser.py` lists the classdesc names; check each is
Serializable in source. A class that isn't Serializable can't be smuggled
into the graph — wrap it inside a Serializable container (a `Map`/`List`/
proxy holding it as a field).

## The lazy-read — objects that don't deserialize on write

Some apps `readObject` the outer envelope but only materialize inner
objects on *use*. A payload inside a `Map`/`List`/`byte[]` field may never
deserialize unless the app iterates it — the gadget fires only when the
field is accessed. Trace whether the app touches the containing field.
