# OOXML Deep — the parts inside the container

## The full part inventory — where entities can live

```
docx:
  [Content_Types].xml
  _rels/.rels
  docProps/app.xml  docProps/core.xml
  word/document.xml          — the main text
  word/_rels/document.xml.rels
  word/styles.xml            — the styles
  word/fontTable.xml
  word/settings.xml
  word/webSettings.xml
  word/comments.xml
  word/footnotes.xml
  word/endnotes.xml
  word/header*.xml footer*.xml
  word/theme/theme1.xml
  word/numbering.xml
  word/media/*               — images
  word/embeddings/*
  word/glossary/document.xml
  word/customXml/*.xml       — custom XML parts
  word/people.xml
  word/commentsExtended.xml

xlsx:
  [Content_Types].xml
  _rels/.rels
  xl/workbook.xml
  xl/_rels/workbook.xml.rels
  xl/worksheets/sheet1.xml sheet2.xml ...
  xl/_rels/sheet1.xml.rels
  xl/sharedStrings.xml       — the cell text table
  xl/styles.xml
  xl/theme/theme1.xml
  xl/calcChain.xml
  xl/comments*.xml
  xl/drawings/drawing*.xml
  xl/pivotTables/*.xml
  xl/tables/table*.xml
  xl/externalLinks/externalLink*.xml
  xl/externalLinks/_rels/externalLink*.xml.rels

pptx:
  [Content_Types].xml
  _rels/.rels
  ppt/presentation.xml
  ppt/_rels/presentation.xml.rels
  ppt/slides/slide1.xml ...
  ppt/slides/_rels/slide1.xml.rels
  ppt/slideMasters/slideMaster1.xml
  ppt/slideLayouts/slideLayout*.xml
  ppt/theme/theme*.xml
  ppt/notesSlides/notesSlide*.xml
  ppt/comments/comment*.xml
  ppt/drawings/drawing*.xml

odt:
  mimetype
  META-INF/manifest.xml
  content.xml                — the main content
  styles.xml
  meta.xml
  settings.xml
  meta-inf/...
```

## The `word/document.xml` injection — the text path

```xml
<w:p><w:r><w:t>&xxe;</w:t></w:r></w:p>
```

`w:t` = the text element — a text-extraction feature renders it —
`&xxe;` expands into the displayed text.

## The `sharedStrings.xml` injection — the cell-text path

```xml
<sst xmlns="..." count="1" uniqueCount="1">
  <si><t>&xxe;</t></si>
</sst>
```

`xl/sharedStrings.xml` is the string-table — a cell references `<si>`
by index — the extracted text shows the entity.

## The `.rels` files — the URL-fetch without entities

```xml
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="http://YOU/x" TargetMode="External"/>
</Relationships>
```

`TargetMode="External"` + a referenced `r:embed`/`r:id` in the doc —
the parser fetches the Target — the entity-free fetch.

## The `customXml` — the arbitrary-XML slot

`word/customXml/item*.xml` — OOXML's "custom XML" parts — parsed by
the app — inject entities there.

## The `docProps` — the metadata XML

`docProps/core.xml`/`app.xml` — `dc:title`/`dc:creator` — metadata the
app may display.

## The `header`/`footer`/`comments`/`footnotes` — the secondary parts

Each is a separate XML part — `header1.xml`/`comments.xml` — parsed
independently — a second injection point.

## The `[Content_Types].xml` — the MIME map

Maps parts to content-types — must declare your injected part if you
add one — usually reuse an existing part.

## The ODF equivalent — `content.xml`

`odt`/`ods`/`odp` — `content.xml` is the main content — `meta.xml`/
`styles.xml`/`settings.xml` the secondary — `mimetype` MUST be first
in the zip and STORED uncompressed.

## The `embeddings`/`media` — the binary slots

`word/embeddings/*` — OLE objects — not XML — skip.
`word/media/*` — images — may have XMP metadata — nested XML in media.

## The `pivotTables`/`externalLinks` — the data-source slots

`xl/externalLinks/externalLink*.xml` — external workbook refs —
`externalLink*.xml.rels` has the Target URL — a fetch.

## The "the app only parses ONE part" — the narrowing

A "preview text" feature may only read `word/document.xml` — inject
there, not everywhere. A "sharedStrings" feature reads `xl/sharedStrings.xml`.
Map which part the app actually renders.

## The "the app validates the doc" — schema-validation

An app that validates the OOXML against its XSD — the schema is XML —
`xsi:schemaLocation` inside the doc points to YOUR schema — the schema
fetch — `parser-abuse.md`.
