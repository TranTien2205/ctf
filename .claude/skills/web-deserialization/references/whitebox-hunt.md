# White-Box Hunt — the source-grep patterns per language

## The grep-first rule

A deserialization challenge with source is a grep exercise — find the sink
call, trace its argument's provenance, find the signature/key check in
between, then pick the gadget. Do not fuzz when the call site is visible.

## The sink patterns — one grep per language

### PHP

```bash
grep -rn "unserialize\|maybe_unserialize\|igbinary_unserialize\|wddx_deserialize" --include='*.php' .
grep -rn "session_start\|session_decode\|unserialize(.*_COOKIE\|unserialize(.*_GET\|unserialize(.*_POST\|unserialize(.*_REQUEST" .
grep -rn "phar://\|file_exists\|is_dir\|getimagesize\|mime_content_type" --include='*.php' .   # phar triggers
grep -rn "allowed_classes\|__wakeup\|__destruct\|__toString\|__call\|__invoke" --include='*.php' .   # the magic methods
grep -rn "SoapClient\|SimpleXMLElement\|DOMDocument" --include='*.php' .
```

### Java

```bash
grep -rn "readObject\|readUnshared\|ObjectInputStream\|XMLDecoder\|XStream\|fromXML\|fromXml" --include='*.java' .
grep -rn "new Yaml\|\.load(\|Yaml(" --include='*.java' .     # Snakeyaml
grep -rn "fastjson\|JSON.parse\|JSONObject.parse\|@type\|autoType" --include='*.java' .
grep -rn "ObjectInputFilter\|resolveClass\|serialVersionUID" --include='*.java' .   # the filter
grep -rn "InitialContext\|\.lookup(" --include='*.java' .     # JNDI
grep -rn "Runtime.getRuntime\|ProcessBuilder\|Method.invoke\|newTransformer" --include='*.java' .  # the sink
```

### Python

```bash
grep -rn "pickle.loads\|pickle.load\|cPickle.loads\|_pickle.loads\|dill.loads\|joblib.load\|read_pickle\|shelve.open\|yaml.load\|yaml.unsafe_load\|full_load\|jsonpickle.decode\|marshal.loads" --include='*.py' .
grep -rn "find_class\|Unpickler\|RestrictedUnpickler\|safe_load\|SafeLoader\|FullLoader" --include='*.py' .   # the filter
grep -rn "np.load\|allow_pickle" --include='*.py' .
grep -rn "os.system\|subprocess\|eval(\|exec(" --include='*.py' .   # the sink
```

### Ruby

```bash
grep -rn "Marshal.load\|Marshal.restore\|YAML.load\|Psych.load\|Oj.load\|safe_load" --include='*.rb' .
grep -rn "session\|secret_key_base\|MessageVerifier\|MessageEncryptor" --include='*.rb' .
grep -rn "permitted_classes\|marshal_load\|_load\|init_with" --include='*.rb' .
```

### .NET / C#

```bash
grep -rn "BinaryFormatter\|SoapFormatter\|LosFormatter\|ObjectStateFormatter\|NetDataContractSerializer\|JavaScriptSerializer\|XmlSerializer\|JsonConvert.Deserialize\|TypeNameHandling\|SerializationBinder\|XmlReader" --include='*.cs' .
grep -rn "machineKey\|validationKey\|decryptionKey\|ViewStateUserKey\|EnableViewStateMac" --include='*.config' --include='*.cs' .
grep -rn "ReadObject\|Deserialize\|FromXml\|DataContractJsonSerializer" --include='*.cs' .
```

### Node

```bash
grep -rn "node-serialize\|funcster\|serialize-javascript\|js-yaml\|devalue\|superjson\|unserialize\|toJSON\|reviver" --include='*.js' .
grep -rn "yaml.load\|safeLoad\|!!js/function\|_$$ND_FUNC$$_" --include='*.js' .
grep -rn "child_process\|eval(\|new Function" --include='*.js' .
```

## The provenance trace — the second grep

Once you have the sink call, trace the argument BACKWARD:

```bash
# where does the argument come from?
grep -rn "the_variable_name" .
# → a cookie? a param? a stored value? a file? a header?
# → and what wraps it — a signature check? a decrypt? a decode?
```

```
sink:    $u = unserialize($_COOKIE['user']);
source:  $_COOKIE['user']                    → direct input — deser confirmed
wrapped: base64_decode($_COOKIE['user'])     → + b64 layer
signed:  hash_verify($_COOKIE['sig'], ...)   → + HMAC — key needed
stored:  $_SESSION['x']                      → second-order — find the write
```

## The config-grep — what signs/loads/whitelists

```bash
grep -rn "secret\|key\|sign\|verify\|hmac\|allowed_classes\|safe_load\|TypeNameHandling\|SerializationBinder\|find_class\|ObjectInputFilter" .
grep -rn "SECRET_KEY\|APP_KEY\|secret_key_base\|machineKey\|validationKey" .
grep -rn "composer.json\|package-lock\|Gemfile\|pom.xml\|requirements.txt\|packages.config" .
```

## The gadget-surface grep — which classes exist

```bash
# PHP — which classes have magic methods:
grep -rn "function __wakeup\|function __destruct\|function __toString\|function __call\|function __invoke" --include='*.php' .

# Java — which Serializable classes / which libraries:
grep -rn "implements Serializable\|readObject\|extends.*Serializable" --include='*.java' .
find . -name "*.jar" | xargs -I{} basename {}    # the lib list
grep -rn "commons-collections\|groovy\|spring\|hibernate\|c3p0" .

# .NET — which serializable / which formatter deps:
grep -rn "Serializable\|ISerializable\|OnDeserialized" --include='*.cs' .
```

## The decision checklist

```
□ sink call found? (unserialize/readObject/loads/Marshal.load/Deserialize)
□ argument provenance? (cookie/param/body/store/file)
□ wrapper? (signature/encryption/encoding — signature-bypass.md if so)
□ filter? (allowed_classes/safe_load/Binder/find_class — the gap inside)
□ gadget surface? (the classes/libs on the classpath — the chain pick)
□ version? (composer.lock/package-lock/pom.xml → phpgcc/ysoserial version)
```
