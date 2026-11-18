# Detection — where the upload surface is and which layer validates

## The intake order

```
1. find every upload endpoint            → forms, JS fetch/XHR, API docs
2. send one benign marker file           → what does the response return?
3. retrieve it                           → where does the file land?
4. send one rejected extension           → which layer answers?
```

Until all four answers exist, extension/MIME juggling is blind.

## Finding upload endpoints — surface inventory

- **HTML forms**: `<input type="file"`, `enctype="multipart/form-data"`, hidden
  `name=` fields on the form (MAX_FILE_SIZE, redirect targets, csrf tokens)
- **Front-end JS**: `FormData`, `.append(`, `axios.post`, `fetch(`, tus/resumable
  protocol endpoints (`Upload-Offset`, `Tus-Resumable` headers), chunked-upload
  APIs, presigned-URL flows (`getUploadUrl`, `/api/uploads/sign`)
- **API surface**: `/upload`, `/api/upload`, `/api/files`, `/api/attachments`,
  `/import`, `/api/import`, `/media`, `/avatar`, `/profile/photo`,
  `/documents`, `/convert`, `/render`, `/report`, `/thumbnail`
- **Hidden uploaders**: XML import (XXE), CSV import, "paste image" endpoints,
  webmail attachment handlers, webhook receivers storing a body, "custom
  theme"/"plugin"/"template" installers
- **White-box**: grep `multipart`, `multer`, `busboy`, `formidable`,
  `upload.single(`, `upload.array(`, `request.FILES`, `$_FILES`,
  `@RequestPart`, `MultipartFile`, `IFormFile`, `parse_multipart`,
  `FileField`, `ImageField`, `data:file:` / `base64` decode-then-write

Every upload-capable route counts, including admin-only ones behind a known
or forgeable role.

## The marker probe — what one upload tells you

Upload a benign text file with a unique marker in **both** filename and
content, e.g. `UPMARK_a1b2.txt` containing `UPMARK_CONTENT_a1b2`. Then read
the response and try to fetch it back:

| Response signal | What it means |
|---|---|
| returns `{"path":"/uploads/x.txt"}` / `{"url":...}` | path disclosed — go fetch it |
| returns only `{"ok":true}` / 201 | path must be discovered — `retrieval.md` |
| returns renamed filename (`<uuid>.txt`) | app renames — note the pattern |
| 400/415 with extension list in the error | validator leaks its whitelist |
| 403 on fetch but upload 200 | file stored but not public-served |
| upload 200, fetch 404 | different serve path or async processing |
| file served `Content-Type: text/plain` verbatim | raw-serve — executable if the dir runs code |
| file served `Content-Disposition: attachment` | download-only — pivot to parser/second-order |

## The rejected-extension probe — name the layer that answers

Send the same marker with `shell.php` (or `.aspx` matching the stack):

| Rejection shape | Layer that answered |
|---|---|
| nothing sent (JS alert, button disabled) | client-side only — strip the JS or replay direct |
| 400 `extension not allowed`, listing allowed set | extension whitelist — `extension-bypass.md` |
| 415 `unsupported media type` | Content-Type/MIME check — `mime-bypass.md` |
| 400 `invalid image` / `file appears corrupted` | content sniffing/magic bytes — `content-bypass.md` |
| 413 | size limit — note it for zip-bomb and polyglot padding |
| 200 but file lands renamed/inert | accept-then-quarantine — find what parses it |
| 500 stack trace naming `multer`/`Pillow`/`imagemagick` | framework + processor leaked — `framework-sinks.md` |

A successful `.php` upload is still not proof — only fetching it back and
seeing code **execute** (or seeing the source rendered verbatim, which is
also a win) confirms. Storage ≠ execution.

## Content-sniffing probes — distinguish shallow from deep checks

| Probe | Diagnoses |
|---|---|
| `GIF89a;` + payload as `.gif` | magic-byte prefix check only? |
| valid PNG + payload appended as `.png` | prefix + suffix tolerance |
| payload with `image/png` MIME, bad magic | whether magic bytes are checked at all |
| valid tiny PNG, payload in a comment chunk | chunk-level inspection? |
| `.png` that is actually a valid polyglot | does it re-encode? (diff the bytes back) |

Fetch the file back and `cmp` against what was sent — byte-identical means
no re-encoding; different means a processor (GD/Imagick/sharp) touched it
and the payload must survive re-encoding → `image-attacks.md`.

## The serve-context probe — who serves the file and how

- `Content-Type` on fetch: `image/*` fixed vs the real type vs `text/html`
- `X-Content-Type-Options: nosniff` — kills MIME-confusion executes
- `Content-Disposition: attachment` — download, not render — SVG XSS dead,
  polyglot-execute-by-include still alive
- CDN/proxy headers (`X-Cache`, `Via`, `CF-RAY`) — uploads may be served by
  a different vhost that never runs code
- Range requests / `Accept-Ranges` — static file server confirmed

## Falsifiers — when this class is closed

- no uploaded file is retrievable through any enumerable path, and no
  server-side parser (image resize, archive extract, document import,
  preview renderer) consumes the uploads
- every upload path lands on a separate storage host/bucket that only ever
  serves `application/octet-stream` with `attachment`, and nothing else
  reads the stored object
- white-box confirms writes go to a directory with `php_flag engine off` /
  no handler mapping, and all processing is byte-safe

## Output to record

- every upload endpoint found + its accepted field names
- the layer each probe response names
- where the marker landed + the exact fetch URL + served Content-Type
