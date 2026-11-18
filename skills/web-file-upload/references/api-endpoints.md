# API Endpoint Shapes — the upload verb's many bodies

## The endpoint inventory — every form an upload takes

| Shape | Request | Attack notes |
|---|---|---|
| multipart POST | `Content-Type: multipart/form-data` | the standard — parser-differentials |
| raw PUT | `PUT /files/x.png` + body | filename in path — traversal in URL |
| raw POST binary | `application/octet-stream` | no multipart at all |
| base64 JSON | `{"content":"<b64>"}` | `json-upload-apis.md` |
| data-URI JSON | `{"image":"data:image/png;base64,..."}` | uri mime-claim |
| url fetch | `{"url":"https://x"}` | `upload-by-url.md` + SSRF |
| GraphQL Upload | operations+map+parts | `graphql-uploads.md` |
| tus resumable | POST+PATCH chunks | `chunked-resumable.md` |
| signed/presigned | policy→S3 PUT | `cloud-storage.md` |
| WebDAV PUT/POST | `PUT /dav/x` | method-level upload |
| SOAP/XML attach | MTOM/XOP or base64-in-xml | XXE + injection |
| email ingest | SMTP/IMAP or webhook | attachment handling |
| FTP/SCP | separate protocol | out of HTTP scope |

## Raw PUT / binary POST — the simplest bypass surface

No multipart parser means no multipart validation — the app reads the raw
body:

```bash
curl -X PUT "$BASE/files/x.php" --data-binary @shell.php
curl -X POST "$BASE/api/files?path=x.php" --data-binary @shell.php \
  -H 'Content-Type: image/png'
```

Check: ext/MIME checks may key on the URL path or a `filename`/`path`
field — a `name=x.php` query arg or `X-Filename` header.

## WebDAV — `PUT`/`MKCOL`/`MOVE`/`COPY`/`PROPFIND`

- `PUT /dav/x.php` — direct write
- `MOVE`/`COPY` with `Destination:` header — `Destination:
  /dav/../../x.php` — traversal via the header
- `PROPFIND`/`PROPPATCH` — metadata writes
- `LOCK`/`UNLOCK` — lock games

## SOAP/MTOM attachments — XML-carried files

```xml
<xop:Include href="cid:file1"/>
--MIME_boundary
Content-ID: <file1>
Content-Type: image/png
```

XML parsers touching `xop:Include`/MTOM or inline `base64` fields — XXE
inside the envelope, attachment the actual file.

## Email ingest — attachments via mail

`webhook`/`inbound` endpoints accepting `.eml`/raw MIME — attachment
parsing is a multipart-family parser with its own quirks; filename inside
`Content-Disposition: attachment; filename=` MIME headers — the SAME
injection grammar.

## The verb matrix — what each method triggers

```
POST   — create/store
PUT    — create-or-replace (often weaker validation)
PATCH  — modify (tus chunks)
GET    — retrieve (with path params → read-side attacks)
DELETE — remove
MOVE/COPY/PROPFIND — WebDAV
OPTIONS — discovery
```

Test `PUT`/`PATCH`/`MOVE` on the upload path even when the form is POST —
frameworks auto-route them to the same handler.

## Falsifiers

- only the documented method+shape is accepted; alternates 405/404

## Output to record

- which verb+shape the endpoint accepts beyond the documented one
