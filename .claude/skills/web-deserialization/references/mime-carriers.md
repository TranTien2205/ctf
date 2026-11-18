# MIME Carriers — the transport envelopes around the blob

## The idea — the blob rides inside a standard container

A serialized payload doesn't always sit in a naked field — it rides inside
multipart, a JWT, an XML element, a form field, a file upload, a cookie.
The envelope shapes which parser sees it and which checks gate it.

## The carrier census

| Carrier | Shape | Notes |
|---|---|---|
| multipart file | `Content-Disposition: form-data; name="f"; filename="x"` | upload → unmarshal |
| multipart field | `name="d"` plain field | field value is the blob |
| JSON field | `{"obj":"<b64>"}` | the JSON is the envelope |
| XML element | `<d><![CDATA[<b64>]]></d>` | CDATA carries raw bytes |
| JWT claim | `{"obj":"<b64>"}` inside payload | signature-gated |
| cookie value | `name=<b64>` | the most common |
| header | `X-Data: <b64>` | header-based |
| URL param | `?d=<urlb64>` | GET-carried |
| form field | `__VIEWSTATE=<b64>` | ASP.NET |
| body raw | `aced...` | binary POST body |
| WebSocket frame | binary/text frame | ws-carried |
| gRPC msg | protobuf field | inside a message field |
| GraphQL var | `{"variables":{"d":"<b64>"}}` | inside a query var |
| SSE/event | `data: <blob>` | server-sent events — rare |
| filename field | `filename="x.ser"` | the NAME is the payload (session.upload_progress) |
| `enctype` switch | url-encoded vs multipart | the same field, different encoding |

## The multipart file → unmarshal path

```
POST /upload  multipart  →  server stores file → a loader unmarshals it
                          → the file's BYTES are the gadget — not the name
```

The `filename` is cosmetic — the file CONTENT is the blob. Upload a `.ser`/
`.pkl`/`.npy`/`.xml`/`.yml` whose *bytes* are the gadget; a `.jpg` name on
pickle bytes only matters if the app sniffs content.

## The JSON-envelope case

```json
{"data":"Tzo4OiJVc2VyIjoyOntzOjQ6Im5hbWUiO3M6NToiYWRtaW4iO30="}
```

A JSON field whose string is a base64-blob — `json_decode`→`unserialize(
base64_decode($x))`. The JSON is valid, the field is the smuggled grammar.
`application/json` content-type = WAF inspects JSON, not the inner field.

## The XML-envelope case

```xml
<request><data><![CDATA[rO0ABXN...]]></data></request>
```

CDATA carries bytes XML can't escape — a serialized blob inside `<![CDATA[
...]]>` survives XML parsing intact, then the app unmarshals the CDATA
contents. `XStream`/JAXB parse the XML; a `byte[]`/String field carries it.

## The JWT-inside-JWT / format-in-format

```json
{"alg":"none"}.{"obj":"<b64 of O:4:\"User\"...>"}.
```

The JWT payload is JSON; a claim inside carries the serialized blob. Forge
the JWT (alg=none/confusion) → the claim reaches the deserializer. Two
formats stacked.

## The `filename`/`name` field as the payload

`session.upload_progress` (php-session.md) — the FILENAME is stored in the
session file as a serialized-string value. A multipart field's `filename`
attribute is the payload, not the file body.

## The "which field gets unmarshalled" hunt

```bash
# in source, for each param/field/file, trace to a deserializer:
#   $_POST['x'] → unserialize       → the field is the blob
#   file_get_contents($_FILES)      → the file is the blob
#   json_decode($_POST['d'])->obj    → a nested field is the blob
#   a header → base64_decode → unserialize → the header is the blob
```

## The transfer-encoding detail — `chunked`/`deflate`/compression

- `Content-Encoding: gzip` — the body is gzipped before TLS — the app
  `gzuncompress`es; send `gzip(blob)` not the raw blob
- `Transfer-Encoding: chunked` — splits the body — usually transparent to
  the app, but a proxy may inspect the *whole* body — a smuggle-gap
- a `Content-Encoding: deflate` that the app doesn't decompress → the app
  sees compressed bytes → `unserialize` fails on them → parser-error shape

## The multipart boundary smuggle

A field `name` or a part `Content-Type` the app's parser splits
differently than the WAF — parser-differential overlap (see
`web-parser-differential` skill). The blob is hidden in a part one parser
sees and the other doesn't.

## Output to record

- Which carrier the blob rode in (cookie/JSON-field/file/JWT/multipart)
- The nested-format chain (carrier → encoding → grammar)
- The verbatim response/OOB proving it landed
