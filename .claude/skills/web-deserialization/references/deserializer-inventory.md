# Deserializer Inventory — every parser that can be the sink

## The point — the bug is wherever bytes become typed objects

The complete inventory of "bytes → objects" calls across the ecosystem —
for the white-box grep and the fingerprint. Any of these on user input is
the sink.

## PHP

```php
unserialize($x)                        // the canonical
maybe_unserialize($x)                   // WordPress wrapper — same sink
session_decode($x)                      // decodes the php_session format
unserialize_callback_func              // autoload on miss
igbinary_unserialize($x)               // igbinary format — same class of bug
wddx_deserialize($x)                   // WDDX XML format
readline_completion_function / custom  // rare
msgpack_unpack / others                // ext-codec dependent
```

## Java

```java
new ObjectInputStream(in).readObject()          // OIS — the canonical
new ObjectInputStream(in).readUnshared()        // unshared variant
ois.readObject() / ois.readObjectNC / readFields
new XMLDecoder(in).readObject()                  // XML beans
new XStream().fromXML(reader)                    // XStream
new XStream().unmarshal(...)                     // XStream
new HessianInput(in).readObject()                // Hessian
new Hessian2Input(in).readObject()               // Hessian2
new Kryo().readClassAndObject(in)                // Kryo
new Yaml().load(reader)                          // Snakeyaml
Yaml.loadAs(...) / Constructor                   // Snakeyaml
ObjectMapper.readValue(..., defaultTyping)       // Jackson polymorphic
fastjson JSON.parse / JSONObject.parseObject      // fastjson
Burlap / Thrift / Protobuf-cassandra / Castor    // misc
InputStream subclassed ObjectInputStream         // custom
```

## Python

```python
pickle.loads(b)                 pickle.load(f)          _pickle.loads
cPickle.loads(b)                dill.loads(b)           joblib.load(f)
shelve.open(path)[k]            numpy.load(f, allow_pickle=True)
pandas.read_pickle(f)           sklearn joblib.load(f)
yaml.load(s)                    yaml.unsafe_load(s)     yaml.full_load(s)  [partial]
yaml.load(s, Loader=UnsafeLoader)   yaml.Loader
jsonpickle.decode(s)            jsonpickle.loads(s)
marshal.loads(b)                marshal.load(f)
msgpack.unpackb(data, ext_hook=...)   # the ext_hook is the sink
redis cache.get → pickle.loads        memcached → pickle.loads
bson.loads / codec decode             # ext-field dependent
```

## Ruby

```ruby
Marshal.load(b)                 Marshal.restore(io)
YAML.load(s)                    Psych.load(s)           Psych.unsafe_load
Psych.parse / full_load         Oj.load(s, mode: :object)
ERB — loaded objects with .result called
SafeYAML — the safe_load boundary
dbm / PStore — file-backed Marshal
```

## .NET / C#

```csharp
new BinaryFormatter().Deserialize(stream)              // BinaryFormatter
new SoapFormatter().Deserialize(stream)                // SoapFormatter
new LosFormatter().Deserialize(s)                      // LosFormatter — ViewState
new ObjectStateFormatter().Deserialize(s)              // ObjectStateFormatter
new NetDataContractSerializer().ReadObject(r)          // NetDataContract
new DataContractSerializer().ReadObject(r)             // DataContract
new DataContractJsonSerializer().ReadObject(s)         // DataContractJson
JsonConvert.DeserializeObject(s, TypeNameHandling.*)   // Json.NET typed
new JavaScriptSerializer(resolver).Deserialize(s)      // SimpleTypeResolver
new XmlSerializer(t).Deserialize(r)                    // XmlSerializer
new XmlSerializer(t, types).Deserialize(r)             // XmlSerializer typed
YamlDotNet DeserializerBuilder                         // YamlDotNet
BinaryReader custom formats                            // app-side
MessagePack ext-codec                                  // MessagePack
```

## Node.js

```js
require('node-serialize').unserialize(x)        // $$ND_FUNC$$
require('funcster').deserialize(x)              // $$__FUNCTION__$$
require('serialize-javascript') + custom reviver
require('js-yaml').load(s)                       // ≤3.x — !!js/function
require('devalue').parse(x)                      // typed revive
require('superjson').deserialize(x)              // meta-typed revive
BSON deserialize + $where                        // the JS field
JSON.parse(x, reviver)                           // custom reviver sink
vm.runInNewContext / eval on a field             // the eval overlap
```

## The "not in the list but is" traps

- `session_decode` / `readline_*` — obscure PHP sinks
- `readResolve`/`readExternal`/`finalize` — the secondary Java hooks
- `__setstate__`/`BUILD` — the secondary Python hooks
- `ObjectMessage.getObject` — the JMS sink inside a "queue" call
- `Castor`/`JAXB`/`XStream`/`Hessian`/`Kryo`/`Fastjson`/`Jackson` — the Java
  alternate-serializer family
- `msgpack`/`bson`/`protobuf`/`avro`/`thrift` `ext_hook`/custom-codec — the
  app-defined revive
- `function.*` revive in `devalue`/`superjson` — the typed-object JSON

## The grep master-pattern — the one-line sweep

```bash
grep -rniE "unserialize|readObject|pickle\.load|pickle\.loads|Marshal\.load|Marshal\.restore|YAML\.load|yaml\.load|Psych\.load|Oj\.load|BinaryFormatter|SoapFormatter|LosFormatter|ObjectStateFormatter|NetDataContractSerializer|DataContractSerializer|JavaScriptSerializer|XmlSerializer|JsonConvert\.Deserialize|TypeNameHandling|XMLDecoder|XStream|Hessian|Kryo|new Yaml|Yaml\.load|ObjectInputStream|readUnshared|fastjson|jsonpickle|joblib\.load|read_pickle|allow_pickle|node-serialize|funcster|js-yaml|devalue|superjson|msgpack.*ext_hook|bson.*decode|readExternal|OnDeserializ|__setstate__|marshal_load|init_with" --include='*.php' --include='*.java' --include='*.py' --include='*.rb' --include='*.cs' --include='*.js' .
```

## Output to record

- The sink call found + the provenance of its argument
- The format it implies + the module it routes to
