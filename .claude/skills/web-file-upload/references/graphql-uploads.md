# GraphQL Uploads — the multipart-request-spec and its own trap set

## The spec — `graphql-multipart-request-spec`

```http
POST /graphql
Content-Type: multipart/form-data; boundary=B

--B
Content-Disposition: form-data; name="operations"

{"query":"mutation($f:Upload!){uploadFile(file:$f){id path}}","variables":{"f":null}}
--B
Content-Disposition: form-data; name="map"

{"0":["variables.f"]}
--B
Content-Disposition: form-data; name="0"; filename="x.png"
Content-Type: image/png

<bytes>
--B--
```

The `map` JSON binds file parts (`0`, `1`...) into `variables` paths —
the file bytes never appear in `operations`.

## Why validators miss it

- a validator grepping `name="file"` / `$_FILES['file']` never sees
  `name="0"` — the field name is an index
- the `operations` part is JSON — checked separately from the `0` part
- `Upload!` scalar — typed as "the file" — server resolves it from `map`
- the content check often runs only on `operations` (the "request") —
  the `0` part is "just a variable"

## Attacks specific to this shape

### `map` confusion

```json
{"0":["variables.f"], "0":["variables.g"]}
{"0":["variables.files.0","variables.files.1"]}
{"0":["variables.f","variables.f"]}
{"0":["variables.nonexistent"]}
{"x":["variables.f"]}
```

Duplicate keys — last wins in JSON.parse; does the server's map-parser
take first/last? Mapping to a nonexistent variable — error path may leak.
Mapping one file to two variables — double-usage.

### Batch uploads — `operations` array

```json
[{"query":"mutation($f:Upload!){a:upload(file:$f){id}}","variables":{"f":null}},
 {"query":"mutation($g:Upload!){b:upload(file:$g){id}}","variables":{"g":null}}]
```

`map` binds `0`/`1` across the batch — one part can feed two uploads.

### Field-level checks bypassed by `map` naming

The schema's `Upload` scalar gets the part — a validator inspecting
`variables.f` (null in `operations`) sees nothing. The file's name/type/
content all live in the `0` part.

## The "operations" side — query/mutation keys

- `upload`/`uploadFile`/`createAttachment`/`importData`/`setAvatar` —
  the mutation names that accept `Upload`
- `File`/`Upload`/`UploadScalar`/`Attachment` scalar types in introspection
- nested input objects — `{input:{file:$f}}` — `map` path
  `"variables.input.file"`

## JSON-body uploads inside GraphQL — no multipart at all

Some schemas take `{"file": "base64..."}` strings — `json-upload-apis.md`.

## Discovery — the introspection tells

```graphql
{__schema{types{name fields{name type{name kind ofType{name kind}}}}}}
```

Look for `Upload`/`File`/`Attachment` scalars and mutations taking them —
`web-graphql` for the query-side depth.

## Falsifiers

- no `Upload` scalar in the schema / no multipart support on the endpoint
- the `map`+parts validation covers name/type/content for every part

## Output to record

- the `operations`/`map` pair that carried the payload
- which check the index-named part bypassed
