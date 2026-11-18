# Gadget Index — every public chain name, what it does, which lib

## PHP — phpgcc catalog by impact family

### RCE chains (call a function)

| Chain | Package | Trigger | Notes |
|---|---|---|---|
| `Guzzle/RCE1` | guzzlehttp/guzzle | FnStream `__destruct` → call | v6-7 |
| `Laravel/RCE1`..`RCE10` | laravel/framework | PendingCommand/eval | version-split |
| `Monolog/RCE1`..`RCE7` | monolog/monolog | handler destruct | version-split |
| `Symfony/RCE1`..`RCE11` | symfony/* | PropertyAccessor/Serializer | version-split |
| `Slim/RCE1` | slim/slim | | |
| `Yii/RCE1` | yiisoft/yii | | |
| `ThinkPHP/RCE1-2` | topthink/framework | | |
| `Phalcon/RCE1` | phalcon | | |
| `CodeIgniter4/RCE1-2` | codeigniter4 | | |
| `Drupal7/RCE1` | drupal/drupal 7 | | |
| `Joomla/RCE1-3` | joomla | | |
| `Doctrine/RCE1-2` | doctrine | | |
| `WordPress/*` | wp + plugins | plugin-split — check which plugin | |
| `ZendFramework/RCE1-4` | zendframework | | |
| `Dompdf/RCE1` | dompdf | | |
| `TCPDF/RCE1` | tecnickcom/tcpdf | | |
| `PHPExcel/RCE1` | phpexcel | | |
| `Smarty/RCE1` | smarty | eval via template | |

### File-write chains

| Chain | Package | What it writes |
|---|---|---|
| `Guzzle/FW1` | guzzle | cookie-jar persist → path |
| `SwiftMailer/FW1-3` | swiftmailer | transport flush → path |
| `Monolog/FW1` | monolog | StreamHandler buffer → streamUrl |
| `Symfony/FW1-3` | symfony | CacheWarmer/FileLoader |
| `Magento/FW1-2` | magento | |
| `ZendFramework/FW1` | zend | |
| `ThinkPHP/FW1-2` | thinkphp | |
| `TCPDF/FW1` | tcpdf | |
| `WordPress/FW*` | wp | |

### File-read / file-delete / SSRF / CMD

| Chain | Package | Impact |
|---|---|---|
| `Monolog/FR1` | monolog | file read → reflected |
| `ZendFramework/FR1` | zend | file read |
| `Drupal7/FD1` | drupal | file delete |
| `ZendFramework/FD1` | zend | file delete |
| `Guzzle/SSRF1` | guzzle | URL fetch |
| `Laravel/CMD1` | laravel | process command |
| `Magento/SQL1` | magento | SQL |

## Java — ysoserial catalog

### JDK-only (no external lib)

| Chain | Trigger | Impact | JDK gate |
|---|---|---|---|
| `URLDNS` | HashMap.hashCode→URL.resolve | DNS lookup | all |
| `Jdk7u21` | AnnotationInvocationHandler+TemplatesImpl | RCE | ≤7u21 |
| `JRE8u20` | bean-specific | RCE | 8u20 |
| `JRMPClient` | UnicastRef connect | 2-stage bootstrap | all |
| `JRMPListener` | listener | (listener side) | all |

### commons-collections family

| Chain | Lib version | Trigger |
|---|---|---|
| `CommonsCollections1` | commons-collections ≤3.2.1 | AnnotationInvocationHandler→LazyMap |
| `CommonsCollections2` | commons-collections4 4.0 | PriorityQueue→compare |
| `CommonsCollections3` | commons-collections 3.x | same template |
| `CommonsCollections4` | commons-collections4 | |
| `CommonsCollections5` | commons-collections 3.1-3.2.1 | BadAttributeValueExpException→toString (8u76+) |
| `CommonsCollections6` | commons-collections 3.1-3.2.1 | HashMap→TiedMapEntry (most reliable) |
| `CommonsCollections7` | commons-collections 3.x | Hashtable→equals |
| `CommonsBeanutils1` | commons-beanutils (no CC needed) | BeanComparator.compare→PropertyUtils getter |
| `CommonsCollectionsK1/K2` | variants | |

### Other-lib chains

| Chain | Lib | Trigger |
|---|---|---|
| `Groovy1` | groovy | MethodClosure.call |
| `Spring1/2` | spring-core+beans | ObjectFactoryDelegatingInvocationHandler |
| `Hibernate1/2` | hibernate-core | TypedValue getter |
| `Myfaces1/2` | myfaces | |
| `Rome` | rome | ToStringBean→equals |
| `Click1` | click-nodeps | |
| `Vaadin1` | vaadin | |
| `JSON1` | json-lib+spring | |
| `AspectJWeaver` | aspectjweaver | **file write** |
| `BeanShell1` | beanshell | bsh.Interpreter eval |
| `C3P0` | c3p0 | JNDI connect |
| `FileUpload1` | commons-fileupload+wicket | file write/move |
| `JBossInterceptors1` | jboss-interceptors | |
| `JavassistWeld1` | javassist+weld | |
| `MozillaRhino1/2` | rhino | |
| `Wicket1` | wicket | |
| `Python1` | jython | |
| `ImageIO` | | |

## .NET — ysoserial.net catalog

| Gadget | Formatters | Impact |
|---|---|---|
| `ActivitySurrogateSelector` | most | compile+run ctor — most reliable |
| `ActivitySurrogateSelectorFromFile` | most | payload from a file |
| `TypeConfuseDelegate` | BF, LosFormatter | Process.Start via Comparer |
| `TypeConfuseDelegateMono` | BF | Mono-safe |
| `TextFormattingRunProperties` | BF, LosFormatter, SoapFormatter, DCS | the ViewState standard |
| `WindowsIdentity` | BF | claims→process |
| `WindowsClaimsIdentity` | BF, Json.NET | claims→process |
| `ClaimsPrincipal` | BF | claims→process |
| `ObjectDataProvider` | Json.NET, Xaml, DataContractSerializer | named method call |
| `PSObject` | Json.NET | PowerShell |
| `AxHostState` | BF | ActiveX |
| `DataSet` | BF | ReadXml/GetType |
| `GenericPrincipal` | BF | claims |
| `RolePrincipal` | BF | roles |
| `SessionSecurityToken` | BF | session claims |
| `TransactionCEO` | BF | newer |
| `ResourceSet` | misc | resources |
| `RegistrationTrigger` | misc | trigger reg |
| `ToolboxItemContainer` | BF | toolbox host |

## Python — the callable inventory

| Callable | Reach | Notes |
|---|---|---|
| `os.system`/`posix.system`/`nt.system` | RCE | most reliable |
| `subprocess.check_output`/`getoutput` | RCE+output | captures stdout |
| `eval`/`exec` | arbitrary code | needs a string |
| `__import__` | module trampoline | first hop when eval blocked |
| `open`/`io.open` | file handle | needs .read() follow-up |
| `builtins.getattr`/`map`/`filter` | trampoline | builtins-only bypass |
| `codecs.decode`/`encode` | re-import | sneaky globals |
| `os._wrap_close`/`warnings.catch_warnings` | pyjail-style | `__init__`/`__repr__` hooks |
| `pty.spawn`/`os.execl*` | shell | interactive |
| `socket`/`urllib.request.urlopen` | OOB fetch | callback |

## Ruby — the universal chains

| Gadget | Gem/lib | Impact |
|---|---|---|
| ERB-proxy (ActiveSupport::Deprecation) | activesupport | ERB#result→eval — universal RCE |
| Gem::Requirement + TarReader | rubygems | resolve→system |
| Net::WriteAdapter + Gem::RequestSet | rubygems | git_set→system |
| ERB direct | stdlib | only if .result is called |

## Node — the revive paths

| Package | Payload shape | Impact |
|---|---|---|
| node-serialize | `{"x":"_$$ND_FUNC$$_function(){...}()"}` | auto-invoke → RCE |
| funcster | `$$__FUNCTION__$$` | same family |
| js-yaml ≤3 | `!!js/function 'code'` | revived fn — needs call |
| serialize-javascript | `{"fn":"function()..."}` | reviver-dependent |

## YAML — the typed tags

| Tag family | Lang | Impact |
|---|---|---|
| `!!python/object` + `apply`/`new`/`name`/`module` | PyYAML | RCE |
| `!!javax.script.ScriptEngineManager`/`!!com.sun.rowset` | Snakeyaml | RCE/JNDI |
| `!ruby/object:ERB`/`!ruby/object:Gem::*` | Psych | ERB eval/universal |
| `!!js/function` | js-yaml ≤3 | revived fn |
| `!<tag:yaml.org,2002:...>` | all | loader-split |

## The picking rule

1. fingerprint the lib+version (composer.lock / package-lock / pom.xml /
   serialVersionUID leak / GadgetProbe)
2. the chain whose version-range covers it
3. prefer in order: a JDK/package-universal chain (URLDNS, Jdk7u21,
   TypeConfuseDelegate, `os.system`) > a version-split chain > an exotic
   one-off
4. a non-RCE chain (file write/URL fetch/JNDI) when RCE is blocked but a
   different impact still reaches the flag
