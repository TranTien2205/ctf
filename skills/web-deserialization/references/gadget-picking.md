# Gadget Picking — the decision matrix under pressure

## The pick algorithm — ordered by what you know

```
1. is the classpath known?       → lockfile → pick by version
2. is the classpath fingerprintable? → probe classes → pick by what resolves
3. is the classpath unknown?      → universal/JDK-only chains first
4. is RCE needed or just the flag? → pick the cheapest impact
5. is egress open?                → pick OOB-capable or in-band
```

## The decision table — Java

```
any Java deserializer + unknown libs      → URLDNS first (prove it ran)
commons-collections ≤3.2.1                → CommonsCollections1/5/6
commons-collections4 4.0                  → CommonsCollections2/4
commons-beanutils (no CC)                 → CommonsBeanutils1
JDK ≤7u21                                 → Jdk7u21
JDK 8u20                                  → JRE8u20
groovy on classpath                       → Groovy1
spring                                    → Spring1/2
aspectjweaver + need file-write           → AspectJWeaver
commons-fileupload+wicket                 → FileUpload1
c3p0 + JNDI possible                      → C3P0
need JNDI, JDK only                       → JdbcRowSetImpl via fastjson/ser
no matching lib + JRMP egress             → JRMPClient → JRMPListener 2-stage
no lib match + file write OK              → a file-write chain on ANY lib
```

## The decision table — PHP

```
guzzlehttp/guzzle                         → Guzzle/RCE1 or FW1
monolog                                   → Monolog/RCE* by version
laravel                                   → Laravel/RCE* by version
symfony                                   → Symfony/RCE* by version
swiftmailer                               → SwiftMailer/FW1-3
yii / thinkphp / slim / zend / magento    → the matching family
drupal7 / joomla / wordpress / codeigniter → the matching family
SoapClient available + need OOB            → SoapClient __call → WSDL fetch
phar file-op trigger available            → phar-deser.md (no lib needed)
a custom class in the app                  → the app's own gadget — build it
```

## The decision table — Python

```
a plain pickle.loads                       → os.system/subprocess/eval reduce
a find_class whitelist                     → builtins-eval path
protocol-0 needed (ASCII channel)          → --protocol 0
npy/joblib/shelve                          → the pickle inside the container
yaml.load (unsafe)                         → !!python/object/apply
jsonpickle                                 → py/reduce form
```

## The decision table — .NET

```
BinaryFormatter                            → TypeConfuseDelegate > ActivitySurrogate
LosFormatter/ViewState                     → TextFormattingRunProperties
SoapFormatter                              → TextFormattingRunProperties / ActivitySurrogate
Json.NET TypeNameHandling                  → ObjectDataProvider
NetDataContractSerializer                  → TextFormattingRunProperties / TypeConfuseDelegate
Xaml                                       → ObjectDataProvider
XmlSerializer (weak)                       → ObjectDataProvider via proxy type
Mono runtime                               → TypeConfuseDelegateMono
```

## The decision table — Ruby

```
Marshal.load                               → the universal ERB-proxy chain
Psych YAML.load                            → !ruby/object the same chain
safe_load + permitted gadget class         → the permitted class's hook
Rails version known                        → the version-matched universal
```

## The "no library match" fallback — the universal/JDK paths

- Java → `URLDNS` (detect), `Jdk7u21`/`JRE8u20` (version-gated RCE),
  `JdbcRowSetImpl` (JNDI — JDK class), `JRMPClient` (2-stage)
- PHP → `phar://` (no lib needed — file-op trigger), the app's own classes
- Python → `builtins`/`os`/`subprocess` are always there
- .NET → `ObjectDataProvider`/`TextFormattingRunProperties`/`WindowsIdentity`
  are framework classes — often whitelisted by a Binder anyway
- Ruby → the ERB-universal uses only stdlib+ActiveSupport
- Node → `child_process`/`require` are runtime classes

## The "impact first" shortcut — pick by what the flag needs

```
the flag is a file  → a file-READ gadget — cheaper than RCE
the flag is a DB row → an RCE or a query-gadget
the flag needs admin → a prop-injection (role=admin) — no code
the flag needs RCE   → the RCE chain
egress blocked      → file-write or error-exfil, not OOB
```

**Rule:** pick the CHEAPEST impact that reaches the flag — a file-read
gadget that lands the flag beats an RCE that fails on egress.

## The "measure twice" checklist — before spending the gadget

```
□ the format is right (fingerprint, not a guess)
□ the deserializer runs (corrupt-diff, not assumed)
□ the classpath version is measured or the chain is version-free
□ the delivery channel is right (cookie vs body vs field vs file)
□ the signature/wrapper is satisfied
□ the impact type is the cheapest that reaches the flag
```

## Output to record

- The classpath measurement that picked the chain
- The chain name + the version-match rationale
- The verbatim confirmation the chain fired
