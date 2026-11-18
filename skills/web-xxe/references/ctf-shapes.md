# CTF Shapes — where XXE actually appears in jeopardy

## The classic five — the high-frequency shapes

1. **SOAP/XML-RPC endpoint** — `?wsdl`, `text/xml`, `SOAPAction` —
   SOAP-XXE → `soap-wsdl.md`
2. **File upload accepting `.svg`/`.docx`/`.xml`** — parser inside the
   container → `svg-xxe.md`/`ooxml.md`
3. **An XML "config import"** — a settings-file upload (`web.config`,
   `pom.xml`, `.plist`, `.resx`) → `misc-formats.md`
4. **A SAML/SSO endpoint** — `SAMLResponse` base64 → `saml.md`
5. **A `text/xml` API** — a "legacy" XML API alongside a JSON API →
   `content-type-confusion.md`

## The one-card-verified shape — `htb-xxe-content-type-branch`

The verified chain (`knowledge/chains/htb-xxe-content-type-branch-
simplexml-noent-file-read.json`): a JSON-looking endpoint that ALSO
accepts `application/xml` — `simplexml` + `LIBXML_NOENT` — the file-read
card. The lesson: when an endpoint accepts JSON, try XML.

## The "XML hiding inside a format" shapes

- **DOCX/XLSX upload** — text extraction feature reads `word/document.xml`
  → `ooxml.md`
- **EPUB reader** — a book-upload → `OEBPS/content.opf` XXE
- **`.drawio`/diagram upload** — drawio XML
- **`.xlsx` "bulk import"** — `xl/sharedStrings.xml` entity → rendered
  in the displayed table
- **`.plist` iOS-adjacent** — settings import
- **`.gliffy`/`.xmind`/`.mm`** — diagram/mindmap files
- **`.xps`/`.oxps`** — XML pages
- **GPX/KML map upload** — GPS XML
- **`.cbz`/comic archive** — embedded `.xml` metadata

## The "the parser is buried in a pipeline" shapes

- An "import contacts" feature → parses vCard/`.vcf` (not XML) → but
  `.xcs`/`SyncML` are XML
- A "convert to PDF" that accepts `.svg`/`.xml` → rasterizer XML parse
- A "translate" feature → `.xlf`/`.xliff`/`.ts` upload
- A "scan import" → `.nmap`/`.nessus` XML upload
- An OIDC/OAuth "metadata fetch" → parses XML metadata
- A `webhook`/`callback` URL that posts XML

## The "the XML is in a header/param" shapes

- `?xml=<doc>` — the query-param-is-XML shape
- `xml=` form field
- An HTTP header that carries XML (`X-Custom: <xml>`)
- A SOAP `Detail`/`Header` sub-element injection

## The "it's XXE-adjacent but not XXE" — near-shapes

- **XML Signature Wrapping (XSW)** — SAML — auth bypass, not XXE
- **XPath injection** — XML doc, XPath query, not entity — different class
- **XSLT injection** — `<xsl:>`/`xml-stylesheet` — exec surface, not entity
- **XML bombs** — Billion Laughs — DoS, `billion-laughs.md`
- **DTD-based CSRF/SSRF** — the `<!ENTITY x SYSTEM "http://internal">` —
  the fetch IS the impact — `ssrf-via-xxe.md`

## The "the endpoint isn't even XML" — content-type-confusion shapes

- `Content-Type: application/xml` on a JSON endpoint
- `application/x-www-form-urlencoded` with `xml=` nested
- `multipart/form-data` with a `.xml` part
- `text/xml` on a REST endpoint that uses a shared deserializer

## Record the shape for the ledger

`state.py <name> --hypothesis "xxe-<shape>" --class web-xxe` — the shape
name guides the next rung and survives a class-switch.
