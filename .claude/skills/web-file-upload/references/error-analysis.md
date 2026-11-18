# Error Analysis — reading upload rejections and pipeline complaints

## Rejection messages → the layer that spoke

| Error text | Layer | Next move |
|---|---|---|
| `extension .php not allowed` / `invalid file extension` | extension whitelist/blacklist | `extension-bypass.md` |
| `unsupported media type` / 415 | per-part Content-Type or sniffed type | `mime-bypass.md` |
| `invalid image` / `not a valid image` / `corrupted` | `getimagesize`/PIL/sharp structural | real file + payload — `polyglot-files.md` |
| `magic bytes` / `signature mismatch` | prefix sniffing | prefix/polyglot |
| `file appears to be malicious` / `virus detected` / `malware` | AV/content grep | `filter-evasion.md` |
| `file too large` / `exceeds max` | size limit | smaller payload/polyglot pad |
| `invalid filename` / `illegal characters` | name sanitizer | which char? iterate the name |
| `destination not writable` / `permission denied` | server-side perms | not a bypass target — path problem |
| `quota exceeded` | disk/quota | not a bug |
| `upload disabled` / `forbidden` | auth/feature gate | escalate auth first |
| silent 200 + file dropped | async validate/quarantine | `race-and-temp-files.md`, `retrieval.md` |

## Parser errors — the pipeline confessing

- `Parse error: syntax error, unexpected ... in /uploads/x.php` — **the
  file IS being executed**; the syntax broke. Fix the PHP, resend
- `Call to undefined function` — exec works; the fn name is blocked
- `Warning: include(...)` / `failed to open stream` — include path
  mechanics — the LFI path is wrong, not the upload
- `Uncaught ImagickException`/`Imagick: ...` — ImageMagick ran — coder
  surface confirmed → `image-attacks.md`
- `GPL Ghostscript ...` in stderr — gs ran — `image-attacks.md`
- `Error: command not found` / `sh: 1: -write: not found` — filename
  reached argv — inject through the name
- `org.apache.tika` / `POIXMLException` / `ZipException` — Java doc/zip
  parser identified
- `yaml.scanner`/`composer.json` style errors — importer parses the file
- `Cannot read properties of` + multer/busboy in trace — Node multipart
  parser — `parser-differentials.md`

## Timing errors

- `504`/gateway timeout on a big upload — the server processed it (slow
  extract/scan); small file tells you whether the endpoint itself is alive
- `413 Request Entity Too Large` — body cap; split or shrink
- `RequestTimeout`/`408` — dribble attack may leave a partial file stored

## Fetch errors on the stored file

| Fetch result | Meaning |
|---|---|
| 200 + bytes identical | served verbatim — `upload_probe verify` = `served-raw` |
| 200 + bytes differ | transformed — processor ran; payload may be stripped |
| 403 | rule denies — file exists; try ext/path variants |
| 404 | wrong path — `retrieval.md`; or the file never landed |
| 500 + stack trace | the server-side handler choked — leak framework/stack |
| redirects to login | the serve endpoint is auth-gated |

## The "upload accepted, nothing works" diagnostic

1. fetch the benign marker — bytes identical? → served, no processing
2. marker 404? → wrong path → `retrieval.md`
3. marker served `attachment`? → download-only → parser/consumer angle
4. `marker.php` rejected but `marker.txt` ok → validation layer identified
5. marker polyglot accepted but not executed → docroot doesn't exec —
   `execution-paths.md`

## White-box error-path reading

- the upload handler's `try/catch` tells you exactly which checks exist
  and in which order — read it before probing
- error strings often name the validator class (`ImageValidator`,
  `MimeTypeValidator`, `ExtensionValidator`)

## Falsifiers

- every rejection is a real validation of the same kind across all probe
  families — the layer is airtight
- errors are generic 400/500 with no pipeline signal — keep probing blind,
  no conclusion yet

## Output to record

- the verbatim error text + the layer it names
- the probe that produced it
