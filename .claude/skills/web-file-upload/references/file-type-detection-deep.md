# File-Type Detection Deep — what each checker actually sees

## The detection stack — every layer a different answer

```
filename extension          → what the client claims
Content-Type header         → what the client claims
magic bytes (libmagic/`file`) → what the bytes say
structural parse            → does the file PARSE as the type
content scan (AV/DLP)       → does it contain bad bytes
size/ratio checks           → resource sanity
```

The attack exploits the disagreement between layers — `theory-of-upload.md`.

## `file`/`libmagic` — what the magic check reads

`file --mime-type x` reads the first few hundred bytes for magic numbers:

| Claimed type | What passes |
|---|---|
| `image/png` | `89 50 4E 47 0D 0A 1A 0A` at offset 0 |
| `image/jpeg` | `FF D8 FF` at offset 0 |
| `image/gif` | `GIF87a`/`GIF89a` at offset 0 |
| `application/pdf` | `%PDF-` at offset 0 |
| `application/zip` | `PK\x03\x04` at offset 0 |
| `image/svg+xml` | `<?xml` or `<svg` — text-based, weak magic |
| `video/mp4` | `ftyp` at offset 4 |
| `image/webp` | `RIFF....WEBP` |

`file` only checks the magic offset — a `.php` file with PNG magic at
byte 0 passes `file` as PNG AND runs as PHP if served as `.php` — the
canonical polyglot move.

## Structural parse — deeper than magic

`getimagesize()`/`exif_imagetype()`/`Image::open()`/`pdf parser` — checks
the file PARSES as the type, not just magic:

- `getimagesize` reads image headers — a fake png with valid headers +
  appended php passes
- `exif_imagetype` checks more header structure than raw magic
- `Image.open`/`load` actually decodes — the strongest check; a truncated
  png fails `load` even with good magic
- PDF: `pdfinfo`/`mutool` structure parse — trailer/xref must validate

A file that magic-passes but parse-fails is a polyglot attempt — the
parse check catches it. That's why `pdf_text.py`/`pdfinfo` exist.

## `getimagesize`/`exif` vs `file` — the common CTF split

- `file`/`libmagic` → magic only, fast, weak — polyglots pass
- `getimagesize`/`identify` → parse headers, moderate — valid-structure
  polyglots pass (a real png + appended php)
- `Image::load`/`pdf parser` → full decode — only actual polyglots pass

The defense gap: a check at layer N misses payloads valid at layer N+1.

## MIME-type header — the client's word

`Content-Type: image/png` in the multipart part — the client sets it —
always bypassable with `--data-binary`+header. Its only value: some
apps check it before reading the body at all. Sending `image/png` for a
`.php` file is step 1; it rarely blocks deeper.

## Content sniffing — `X-Content-Type-Options: nosniff`

Without `nosniff`, the browser guesses the type from bytes — a `.txt`
file of HTML sniffs to `text/html` → stored XSS without `.html` upload.
Check the response's `X-Content-Type-Options` on the uploaded file —
`nosniff` present = no sniffing; absent = sniffing possible.

## The charset/encoding trap — type claims vs byte reality

- `text/html` vs `application/octet-stream` — the `Content-Type` on SERVE
  decides browser interpretation
- a file served `text/plain` can't XSS; `text/html` can — the serve-type
  is the actual gate, not the upload-type
- `Content-Disposition: attachment` overrides — downloads instead of
  rendering

## The "the file LOOKS like X but IS Y" — a structural checklist

```
[ ] magic bytes match the claimed type at the right offset
[ ] the file PARSES as that type (full decode succeeds)
[ ] the Content-Type header claims the same type
[ ] the extension matches
[ ] no appended payload beyond the format's valid end
[ ] the file's size is sane for the type
```

A "real polyglot" passes every check but still IS the other type when a
different parser reads it — `polyglot-files.md`.

## The `file` vs `getimagesize` gotcha — they read different amounts

`file` reads ~few hundred bytes; `getimagesize` reads the whole header
structure — a png with valid magic but garbage in IHDR fails
`getimagesize` — the attack needs a valid-parse png, not just magic.

## The `file` database — `magic` ruleset coverage gaps

`libmagic` rules are patterns — obscure formats have weak rules — a file
claiming `application/octet-stream` that `file` can't classify but the
consumer parses as something else = the deep-bug territory.

## Falsifiers

- the file both magics AND parses AND decodes as the claimed type AND
  serves as a non-executable type AND no consumer parses it differently
- every layer agrees — the polyglot would have to be a true dual-format
  file with executable form in both

## Output to record

- which detection layer rejected/accepted which test file — the exact
  boundary between layers
