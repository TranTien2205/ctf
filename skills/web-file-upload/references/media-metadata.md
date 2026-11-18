# Media Metadata Payloads — EXIF/iTXt/XMP/tags as the carrier

## The shape — the payload lives in the file's metadata, not its pixels

EXIF, iTXt, XMP, ID3, QuickTime atoms, IPTC — metadata fields that
parsers/consumers read and sometimes render — an injection inside the
metadata survives the "valid image" check.

## EXIF fields — the `exif_read_data` sink

PHP `exif_read_data`, exiftool, `ImageMagick` EXIF display, web galleries
showing camera info — any field gets rendered:

```
EXIF UserComment = <?php system($_GET[c]);?>
EXIF ImageDescription = <script>alert(1)</script>
EXIF Artist = ' OR '1'='1
```

`exiftool -UserComment='<?php ...?>' x.jpg` writes it. The consumer that
renders the EXIF is the sink — a gallery's "camera info" page, an admin
metadata view.

## PNG `iTXt`/`tEXt`/`zTXt` — text chunks inside the image

```
iTXt key="<?php system($_GET[c]);?>" text="x"
tEXt Author=<script>...</script>
```

Text chunks carry keyword+text — a PNG can hold arbitrary text — the
metadata-viewer or `png_read` consumer is the sink.

## XMP — the XML metadata inside images

XMP is embedded XML — in JPEG/PNG/TIFF/PSD/PDF:

- `<?xpacket ...?>` XML inside the file
- fields like `dc:creator`, `dc:description` — a parser reads them as
  XML — an XXE inside XMP
- `dc:title` reflected on an info page = stored XSS via metadata

## ID3 tags — MP3 audio metadata

ID3v2 frames — `TIT2`/`TPE1`/`COMM` — a media info view or player
displays them — injection in the tag fields.

## QuickTime atoms — `.mov`/`.mp4` metadata atoms

`©nam`, `©too`, `udta` atoms — parsed by ffmpeg/players — a metadata
field carrying a payload.

## The "the metadata is parsed where?" question

- `exif_imagetype`/`exif_read_data` — reads exif — the metadata is
  attacker-controlled input to those functions
- `ImageMagick identify`/`convert` reads EXIF+XMP — a command-injection
  in metadata reaches `identify`'s args?
- the web's "media info" page — the metadata displayed = stored XSS
- a metadata-thumbnailing service — imagemagick on the file's metadata

## `exiftool` injection — the `exiftool` CVE history

`exiftool` itself had CVE-2021-22204 (code exec via crafted DjVu/
`eval` inside `exiftool`'s Perl eval) — if the server runs `exiftool`
on uploads — the file's metadata IS the exec. `DjVu`/`Ant`/`ParseAnt`
metadata trick.

## The "the metadata survives re-encode" caveat

- `convert`/`identify` usually preserve metadata
- `PIL.Image.save` strips EXIF unless explicitly carried
- `sharp`/`imagemin` strips metadata by default — the payload dies on
  re-encode unless the parser reads it first

## The detection — does the app READ metadata?

- a "media info" view exists → it reads exif
- `exiftool`/`identify` in the app's source/dependencies
- `exif_read_data`/`exif_imagetype` calls in source
- an image upload triggers a metadata response — `identify -verbose`
  output in the response

## Falsifiers

- no consumer reads the file's metadata
- every metadata field is escaped/sanitized on render

## Output to record

- which metadata field the app reads + whether it reaches a sink
