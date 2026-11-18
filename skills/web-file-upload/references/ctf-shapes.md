# CTF Shapes — how upload challenges actually look

## The canonical CTF upload shapes — recognized on sight

### 1. Avatar/profile upload → extension bypass → shell

Signup → profile photo → whitelist `.jpg|.png` → bypass via `.pht`/polyglot/
`.htaccess` → `/uploads/x.pht?c=cat /flag`. The most common shape — solve
path is usually `extension-bypass.md` + `server-configs.md` when `.htaccess`
is in play.

### 2. Import/upload → consumer parses the file → XXE/deser/formula

`/import` takes docx/csv/yaml/zip — the file is never served; the parser
runs it. `document-attacks.md` / `archive-attacks.md` /
`web-deserialization` skill. The flag read is in the parsed output or an
OOB callback.

### 3. Image upload → resize/preview → ImageMagick/Ghostscript

`/upload` → thumbnail generated → the coder/demuxer delegates reach local
files or exec → `image-attacks.md` / `video-audio-attacks.md`.

### 4. Upload → stored → include via another primitive

Upload lands unreachable-by-URL but a separate `?page=`/`?file=` LFI
includes it → GIF89a+PHP polyglot included executes → `execution-paths.md`.
Or `phar://` into `file_exists`/`getimagesize`/`exif_read_data` → PHP
object injection → `web-deserialization`.

### 5. Admin file-write + traversal → overwrite

An admin-only file write with a path join — traversal lands the file over
a template (`apexsurvive` shape) → template renders SSTI → flag. The
validator requires parseable content (PDF) — the payload lives inside a
polyglot/stream.

### 6. Multi-layer: cache/hop-by-hop → upload polyglot → loader runs it

`htb-novacore` shape — the upload scanner sees an archive, the plugin
loader sees an executable — a polyglot that satisfies both. The bypass is
that the scanner and the loader read different offsets of the same file.

### 7. Plugin/theme "installer" — code by design

`/admin/plugins` accepts zips whose manifest is loaded — a "plugin" with a
code file is RCE-by-design; the trick is the archive/manifest shape the
installer wants, and the bypass is scanner-vs-loader polyglot.

### 8. Upload → stored on S3/bucket → presigned-URL/consumer abuse

`cloud-storage.md` — the app signs, the client PUTs, the bucket serves;
the attack is policy-condition gaps or the downstream processor.

### 9. Upload → race the validator/renamer

Temp path is fetchable during the validate-then-delete window —
`race-and-temp-files.md`.

### 10. Upload → stored for an admin bot to view → stored XSS via svg/html

The file is a document the admin opens — `.svg`/`.html`/`.pdf` with
script — `svg-attacks.md` / XSS-skill payload.

## The CTF-specific reads

- **the description usually names the angle**: "secure file storage" →
  traversal; "image uploader" → polyglot/magick; "document converter" →
  parser/gs; "import feature" → XXE/deser
- **the whitelist shown in the error is the answer key** — the allowed
  list tells you exactly which ext to weaponize via config or polyglot
- **the file path in a response/error is the serve root** — `retrieval.md`
- **"files are stored outside the web root"** = consumer/import challenge,
  not serve challenge
- **docker-compose with an "imagemagick"/"clamav"/"ghostscript" service**
  = that IS the attack surface

## Verified chain shapes here

- `htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce` — cache
  poisoning → DOM clobber → polyglot plugin upload → exec (scanner reads
  archive, loader reads executable)
- `htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce`
  — race → stored XSS → admin file-write traversal → template overwrite →
  SSTI (PDF-parseable polyglot)

Both hinge on the file landing where a DIFFERENT consumer loads it — the
upload is the delivery, not the exploit.

## The "is this even an upload challenge" check

Upload endpoints appear in challenges whose real class is SSRF (upload-by-
URL), XXE (xml/docx import), SSTI (template/theme), deserialization
(pickle/yaml/serialized upload), race (profile update), or CSRF (the bot
uploads it). The classifer names the *sink* class; the upload is delivery.
When the endpoint is a file-accept but the exploit is a different class —
route to that skill's depth file.

## Falsifier restated

No retrievable file AND no consumer = closed. Before concluding, verify
every upload endpoint was probed — CTF apps hide the real one behind an
import/plugin/avatar endpoint.

## Output to record

- the shape matched + the chain card if one exists
- the actual class routed to (upload is delivery, the sink is the class)
