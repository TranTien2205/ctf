# Detection — finding where XML is parsed

## Where XML parsers hide

XXE exists wherever XML is parsed server-side. The endpoint does not
need to *look* XML-ish:

- **Dedicated XML endpoints** — `/api/xml`, SOAP services, XML-RPC,
  WSDL, WebDAV, RSS import, sitemap upload
- **JSON endpoints that also accept XML** — content-type confusion;
  the framework's `application/xml` parser is a second parser behind a
  JSON-looking API — `content-type-confusion.md`
- **File uploads** — DOCX/XLSX/PPTX/SVG/EPUB are ZIP containers of XML;
  the parser is invoked server-side by the upload handler
- **SSO/SAML** — SAML responses are XML, parsed with privileged XML
  stacks
- **Config/property uploads** — `.xml`/`.plist`/`.config`/`.csproj`/
  `.resx`/`.manifest`/`pom.xml`/`web.config`/`build.xml`/`web.xml`
- **SOAP / XML-RPC / WCF / WebDAV** — always XML
- **XMPP / Jabber** — XMPP stanzas are XML
- **SVG uploads** — SVG is XML; rasterizers parse it server-side
- **PDF XMP metadata** — XMP packets are XML parsed by PDF tools
- **RSS/Atom import** — feed parsers
- **SAML/OAuth** — SAML responses/assertions
- **WebDAV/CalDAV/CardDAV** — XML bodies on `PROPFIND`/`REPORT`/`MKCALENDAR`
- **Office upload** — DOCX/XLSX/PPTX/ODT/ODP are XML-in-ZIP
- **E-book/firmware configs** — `.epub` (XML in zip), `.opml`, `.xspf`,
  `.wsdl`, `.gpx`, `.kml`, `.musicxml`, `.xsl`, `.xslt`, `.wsdl`,
  `.maven`/`pom.xml`, `.csproj`/`.vbproj`/`packages.config`/`web.config`

## Signals that XML is parsed — recon

- Response headers/`Server`/`X-Powered-By` naming a stack known to
  ship XML parsers (Java EE, .NET, PHP-DOM, libxml2)
- An endpoint that accepts `application/xml`/`text/xml` and answers
  differently from `application/json`
- An endpoint that returns XML output (`Content-Type: application/xml`)
  — likely also parses XML input
- SOAP action headers (`SOAPAction:`), `text/xml` responses, WSDL at
  `?wsdl`
- An error message quoting XML parser names:
  `SAXParseException`/`org.xml.sax` (Java), `System.Xml` (.NET),
  `SimpleXML`/`DOMDocument`/`libxml` (PHP), `lxml`/`ElementTree`/
  `xml.etree`/`defusedxml` (Python), `REXML`/`Nokogiri` (Ruby),
  `encoding/xml` (Go), `XmlReader`/`XmlDocument` (C#)
- File upload of office formats (the parser is invoked server-side)
- Error page paths: `org.xml.sax`, `javax.xml.parsers`, `System.Xml`,
  `MSXML`, `libxml`, `Expat`, `Xerces`, `Saxon`, `lxml`

## The baseline document — establish the shape first

Before any entity, send a well-formed minimal doc matching the observed
endpoint shape. Record status/body-length/timing. This is your control.

```xml
<?xml version="1.0"?>
<data><field>BASELINE</field></data>
```

If the endpoint echoes the field (registration forms, echo APIs,
preview endpoints, `?format=xml`), you have an in-band channel.

## The harmless-entity probe — entity resolution check

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY probe "XXE_PROBE_7f2a">]>
<r>&probe;</r>
```

Three outcomes:

- `XXE_PROBE_7f2a` appears in the response → internal entities resolve —
  escalate to external entity
- `&probe;` literal → entities not substituted — parser disabled or
  output is entity-escaped; try parameter entities / error channel
- parse error → parser exists; the error TYPE tells you whether DOCTYPE
  is rejected (then try XInclude) or XML itself is broken (fix the doc)

## The content-type matrix — probe all four

```
Content-Type: application/xml
Content-Type: text/xml
Content-Type: application/soap+xml
Content-Type: application/x-www-form-urlencoded   (with xml in a field)
```

Each may route to a different parser/validator config. Test all.

## The where-it-usually-hides checklist

- an endpoint that parses a doc you upload → XXE via upload
- a docx/xlsx upload → XXE inside the ZIP's xml parts
- an SVG → image-pipeline XML parser
- a PDF → XMP metadata XML
- SAML/OAuth → assertion XML
- a SOAP endpoint → SOAP envelope
- RSS/Atom import → feed XML
- an "import contacts"/"import data" feature → often XML/CSV/XLSX parser
- a WSDL/SOAP endpoint discovered by path fuzz — `?wsdl`, `/service`,
  `/soap`, `/api/soap`
- XMPP / jabber integration
- a `.config`/`.plist`/`.xml` config upload
- WebDAV `PROPFIND`/`REPORT`/`LOCK`/`MKCALENDAR` bodies
- PDF XMP metadata (`xpacket`) — parsed by PDF tools
- ePub upload — zip of XML

## The "there's no XML anywhere visible" case — content-type confusion

The verified chain here is exactly this: a JSON-looking API that
*branches on Content-Type* and routes XML bodies to a second parser.
Always retry JSON endpoints with `Content-Type: application/xml` —
`content-type-confusion.md`.

## Falsifiers

- no XML parser is reachable on any probed surface → class dead for
  this target
- the parser strips DOCTYPE on every surface → entities off →
  class dead (or pivot to XInclude which doesn't need DOCTYPE)

## Output to record

- which surface parses XML + which parser + whether DOCTYPE/entities
  are allowed
