# web-file-upload — reference index

The canonical contract is `../SKILL.md`. This index routes every stored
question to exactly one module. Start at the decision tree; open the file
it names; come back only when that file's falsifier fires.

## Decision tree — where does the file go?

```
upload accepted?
├─ NO → detection.md — find what the filter actually checks
│        ├─ extension check      → extension-bypass.md + filter-evasion.md
│        ├─ MIME/Content-Type    → mime-bypass.md
│        ├─ magic bytes          → file-type-detection-deep.md + polyglot-files.md
│        ├─ structural parse     → parser-differentials.md + content-bypass.md
│        └─ AV/content scan      → eicar-av-test.md + webshell-advanced.md
│
└─ YES → where does it land?
         ├─ exec-mapped dir + exec ext    → execution-paths.md → apache/nginx/iis-deep.md
         ├─ webroot but not exec-mapped   → server-configs.md (handler override)
         │                                ├─ .htaccess/.user.ini → init-hooks.md
         │                                └─ web.config          → iis-deep.md
         ├─ include/LFI reachable         → phpwrappers-upload.md + file-read
         ├─ extraction/consumer parses    → second-order-processing.md
         │                                ├─ archive extract      → archive-attacks.md
         │                                │                        zip-format-deep.md
         │                                │                        symlink-upload.md
         │                                │                        zip-bombs-deep.md
         │                                ├─ phar://               → phar-format-deep.md
         │                                ├─ imageMagick          → imagemagick-deep.md
         │                                ├─ image parsers        → image-attacks.md
         │                                ├─ video/audio          → video-audio-attacks.md
         │                                ├─ pdf                  → pdf-deep.md
         │                                ├─ office/documents     → document-attacks.md
         │                                │                        office-formats-deep.md
         │                                ├─ xml/svg              → svg-attacks.md
         │                                │                        xxe-in-uploads.md
         │                                ├─ csv/formula          → csv-dde-injection.md
         │                                ├─ markdown/rendered    → markdown-preview.md
         │                                ├─ html                 → html-upload.md
         │                                ├─ deserialization      → web-deserialization/
         │                                ├─ pickle/model load    → wasm-upload.md + python-specific.md
         │                                ├─ jar/war deploy       → jar-war-deploy.md
         │                                ├─ node plugin/require  → node-specific.md
         │                                └─ queue/worker         → queue-workers.md
         │
         ├─ filename reaches a sink        → filename-injection.md
         │                                  + response-header-injection.md
         │                                  + unicode-and-normalization.md
         │
         ├─ path/destination field         → path-traversal.md
         │                                  + file-overwrite.md
         │                                  + symlink-upload.md
         │                                  + readonly-fs.md
         │                                  + git-upload.md
         │                                  + backup-restore-upload.md
         │                                  + theme-plugin-deploy.md
         │                                  + init-hooks.md
         │                                  + windows-quirks.md
         │                                  + node-specific.md
         │                                  + python-specific.md
         │
         ├─ upload-by-url                  → upload-by-url.md + web-ssrf/
         ├─ graphql upload                 → graphql-uploads.md
         ├─ json/base64 api                → json-upload-apis.md
         ├─ chunked/resumable              → chunked-resumable.md
         ├─ raw PUT/WebDAV/MTOM            → api-endpoints.md
         ├─ cloud/object storage           → cloud-storage.md
         │                                  + storage-backends.md
         │                                  + cdn-and-proxy.md
         ├─ checksum-named file            → checksum-dedup.md
         ├─ the serve is auth-gated        → authz-and-scope.md
         ├─ the serve is negotiated        → content-negotiation.md
         └─ the serve path itself          → retrieval.md + serving-context.md
```

## Core workflow files

| File | Covers |
|---|---|
| `detection.md` | what the filter checks, per-layer probes |
| `retrieval.md` | where the file lands, how it's served |
| `serving-context.md` | origin, MIME, disposition on serve |
| `workflow.md` | the end-to-end bounded workflow |
| `tooling.md` | `upload_probe`/`archive_gen`/`race_probe`/`http_probe`/`pdf_text` |
| `payload-dictionary.md` | the full payload corpus by attack class |
| `evidence-rules.md` | what each result proves |
| `error-analysis.md` | reading upload errors into the filter model |
| `common-mistakes.md` | the traps that waste budget |
| `ctf-shapes.md` | the typical challenge delivery shapes |
| `cheatsheet.md` | the compressed field tables |
| `whitebox-hunt.md` | grep targets when source is available |
| `fuzzing-uploads.md` | systematic filter-fuzzing |
| `theory-of-upload.md` | why the bug class exists at all |

## Filter bypass (the validator is the wall)

| File | Covers |
|---|---|
| `extension-bypass.md` | ext tricks: double-ext, case, null-byte, alternates |
| `mime-bypass.md` | Content-Type spoofing, param order, missing parts |
| `content-bypass.md` | magic bytes, polyglot content, compression tricks |
| `filter-evasion.md` | the systematic filter-probing matrix |
| `client-side-bypass.md` | JS validation bypasses |
| `parser-differentials.md` | front-vs-back parse disagreements |
| `multipart-spec.md` | multipart body grammar and quirks |
| `file-type-detection-deep.md` | every check layer and its residual |
| `eicar-av-test.md` | fingerprinting the AV scanner |

## Content-based payloads (the file IS the payload)

| File | Covers |
|---|---|
| `polyglot-files.md` | GIFAR, PNG/PHP, PDF/ZIP hybrid |
| `image-attacks.md` | EXIF, ICC, ImageTragick surfaces |
| `svg-attacks.md` | script/entity/foreignObject in svg |
| `document-attacks.md` | docx macro/DDE/XXE embedded |
| `pdf-deep.md` | pdf js/launch/embedded files |
| `office-formats-deep.md` | OOXML part-level attacks |
| `video-audio-attacks.md` | ffmpeg/m3u8/concat/file-read |
| `imagemagick-deep.md` | MSL/coder-delegate/file-read |
| `csv-dde-injection.md` | `=`/`+`/`-`/`@` formula leads |
| `markdown-preview.md` | markup-rendered XSS |
| `html-upload.md` | `.html` serving as page |
| `xxe-in-uploads.md` | which file parts carry XML entities |
| `webshell-advanced.md` | shell payload corpus + obfuscation |
| `webshell-templates.md` | webshell syntax reference (AV-safe) |
| `wasm-upload.md` | wasm/.so/.pyc/.class native-blob loads |
| `payload-types.md` | per-platform shell corpus + minimal payload forms |
| `embedded-chains.md` | the format-carried feature attack (docx OLE, pdf /JS, etc.) |
| `media-metadata.md` | EXIF/iTXt/XMP/ID3 as the payload carrier |
| `session-upload.md` | PHP session-file write + include chain |
| `crossdomain-flash.md` | flash-era policy and swf uploads |

## Storage & path (where the file lands)

| File | Covers |
|---|---|
| `path-traversal.md` | destination-field control |
| `file-overwrite.md` | landing over a valuable file |
| `archive-attacks.md` | zip-slip, tar-slip, link entries |
| `carrier-formats.md` | 7z/rar/gz/bz2/xz/zstd format specifics |
| `zip-format-deep.md` | local-header vs CD-name disagreement |
| `phar-format-deep.md` | `phar://` meta deserialization |
| `symlink-upload.md` | archive symlink entries |
| `zip-bombs-deep.md` | decompression DoS shapes |
| `readonly-fs.md` | writable-vs-readonly split |
| `storage-backends.md` | disk/db/s3/memory differences |
| `cloud-storage.md` | presigned/policy/object storage |
| `cdn-and-proxy.md` | edge caching/transformation layer |
| `windows-quirks.md` | ADS/trailing-dot/reserved/8.3 |
| `unicode-and-normalization.md` | NFKC/UTF-8/case-fold filename drift |
| `filename-injection.md` | the name as an injection vector |
| `response-header-injection.md` | CRLF in disposition/location headers |
| `double-upload-collision.md` | same-name collision + overwrite policy |
| `form-field-confusion.md` | filename/name[]/field-order confusion |
| `checksum-dedup.md` | content-hash naming and collision games |

## Serve & execution (the file runs)

| File | Covers |
|---|---|
| `execution-paths.md` | serve-exec vs include-exec vs consumer-exec |
| `server-configs.md` | handler map — which ext executes where |
| `apache-deep.md` | AddHandler/AddType/.htaccess/mod_php quirks |
| `nginx-deep.md` | location blocks/php-fpm/alias traversal |
| `iis-deep.md` | IIS handlers/web.config/.aspx/.asp |
| `phpwrappers-upload.md` | php://filter/phar://include chains |
| `php-cgi-params.md` | `?-s`/`?-d`/`?-r` argv injection |
| `framework-sinks.md` | per-framework upload defaults and sinks |
| `extraction-sinks.md` | extract-to-disk consumer routes |
| `init-hooks.md` | `.htaccess`/`.user.ini`/bashrc/hooks |
| `theme-plugin-deploy.md` | CMS plugin/theme install endpoints |
| `jar-war-deploy.md` | Java servlet container deploys |
| `node-specific.md` | package.json/node_modules/config-js sinks |
| `python-specific.md` | .pth/sitecustomize/conftest/pickle sinks |
| `git-upload.md` | .git/config/hooks writes |
| `backup-restore-upload.md` | config/db restore import attacks |

## The request's shape

| File | Covers |
|---|---|
| `api-endpoints.md` | PUT/WebDAV/MTOM/email-attach forms |
| `graphql-uploads.md` | multipart-spec graphql uploads |
| `json-upload-apis.md` | base64/data-uri/hex JSON bodies |
| `chunked-resumable.md` | tus/resumable state machines |
| `upload-by-url.md` | fetch-my-url upload = SSRF |
| `race-and-temp-files.md` | TOCTOU on check-then-write |

## Second-order and downstream

| File | Covers |
|---|---|
| `second-order-processing.md` | consumers that run later |
| `queue-workers.md` | async processing sinks |
| `post-exploitation.md` | what exec buys after the shell |
| `authz-and-scope.md` | role/IDOR/IDOR-read on uploads |
| `content-negotiation.md` | Accept/Range/Vary serve-side games |
| `content-length-games.md` | CL/TE/size-field lies |
| `request-body-encoding.md` | Content-Encoding/charset layer bypasses |
| `upload-rate-limit.md` | throttle detection and bypass |

## Reading order for a fresh challenge

1. `detection.md` — probe what the filter checks
2. `retrieval.md` — find where the file lands and how it's served
3. one of the per-landing modules above
4. `execution-paths.md` — pick exec-by-serve/include/consumer
5. `tooling.md` — the exact commands
6. `evidence-rules.md` — what the result proves
