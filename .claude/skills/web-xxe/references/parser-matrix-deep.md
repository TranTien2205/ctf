# Parser Matrix — deep — every behavior, measured

## Java Xerces — the reference implementation

```
DocumentBuilderFactory.newInstance().newDocumentBuilder()
SAXParserFactory.newInstance().newSAXParser()
XMLReaderFactory.createXMLReader()
JAXB Unmarshaller
dom4j/JDOM/woodstox/xstream/jackson-xml wrapping it
```

| Feature | Default |
|---|---|
| internal `&x;` | ✓ |
| external `&x;` `file:` | ✓ |
| external `&x;` `http:` | ✓ |
| param `%x;` internal | ✓ |
| param `%x;` external | ✓ |
| external-subset-fetch | ✓ |
| param-entity-in-internal-subset-compose | ✗ (strict) |
| `NDATA` | ✓ |
| `data:` URI | ✗ |
| `php://`/`phar://`/`expect://` | ✗ |
| `jar:`/`netdoc:` | ✓ |
| `ftp:` | ✓ |
| `gopher:` | JDK7- only |
| `file:///dir/` listing | ✓ |
| UTF-16/EBCDIC | ✓ |
| Billion-Laughs cap | `entityExpansionLimit` 64000 |
| XInclude | opt-in `setXIncludeAware` |

Error: `org.xml.sax.SAXParseException`, `FileNotFoundException`,
`MalformedURLException`, `IOException`.

## .NET — `XmlReader`/`XmlDocument`/`XDocument`/`XmlSerializer`/`DataSet`

| Feature | Default (4.5.2+) | With `DtdProcessing.Parse`+`XmlUrlResolver` |
|---|---|---|
| DOCTYPE | refused | allowed |
| internal `&x;` | n/a | ✓ |
| external `&x;` `file:` | n/a | ✓ |
| param `%x;` | n/a | ✓ |
| ext-subset fetch | n/a | ✓ |
| `NDATA` | n/a | ✓ |
| XInclude | n/a | opt |

Errors: `XmlException: DTD is prohibited`, `DirectoryNotFoundException`,
`XmlException`, `WebException`.

The default-Prohibit is the wall — `DtdProcessing.Parse`+`XmlUrlResolver`
is the live-config — grep the `XmlReaderSettings`/`XmlResolver`.

## libxml2 — PHP/Python/Ruby substrate

`libxml2` is the C library under `simplexml`, `DOMDocument`, `XMLReader`,
`lxml`, `Nokogiri`, `REXML`-some.

| Feature | Default | With `NOENT`/`DTDLOAD` |
|---|---|---|
| internal `&x;` | ✓ | ✓ |
| external `&x;` | ✗ (no NOENT) | ✓ |
| param `%x;` internal | ✓ | ✓ |
| param `%x;` external | ✗ (no DTDLOAD) | ✓ |
| ext-subset fetch | ✗ | ✓ |
| param-compose-in-ext-subset | ✓ (lax) | ✓ |
| `data:` URI | ✓ | ✓ |
| `php://`/`phar://`/`expect://` | PHP | PHP |
| `ftp:`/`gopher:`(curl) | ✓ | ✓ |
| Billion-Laughs cap | amplification ~100 | same |
| XInclude | `XML_PARSE_XINCLUDE` opt | opt |

The `LIBXML_NOENT` flag is the external-entity switch — `simplexml`/
`DOMDocument` default has it OFF — the verified card's name
`simplexml-noent` records exactly that.

## Python — the per-lib matrix

| Lib | internal | external | param | DTD-fetch | data: | safe-default? |
|---|---|---|---|---|---|---|
| `xml.etree.ElementTree` | ✓ | ✗ | ✗ | ✗ | ✗ | mostly-safe |
| `xml.dom.minidom` | ✓ | ✓ | ✓ | ✓ | — | live |
| `xml.sax` | ✓ | ✓ | ✓ | ✓ | — | live |
| `lxml.etree` | ✓ | ✓ | ✓ | ✓ | ✓ | live |
| `xmlrpc.client` | ✓ | ✓ | ✓ | ✓ | — | live |
| `defusedxml.*` | ✗ | ✗ | ✗ | ✗ | ✗ | hardened |

The trap — `ElementTree` only does INTERNAL entities — `&x;` internal
expands, `SYSTEM`-external doesn't — "external dead, internal live" is
the ElementTree signature.

## PHP — `simplexml`/`DOMDocument`/`XMLReader`/`xml_parse`

| Lib | internal | external | param | NOENT needed? |
|---|---|---|---|---|
| `simplexml_load_string` | ✓ | ✗(default) | ✓ | YES for ext |
| `DOMDocument->loadXML` | ✓ | ✗(default) | ✓ | YES |
| `XMLReader::XML` | ✓ | ✗(default) | ✓ | YES |
| `xml_parse` | ✓ | ✓ | ✓ | NO — different lib |

The PHP-specific detail — internal entities ALWAYS expand; EXTERNAL
entities need `LIBXML_NOENT` or `substituteEntities` — the flag-off
default is PHP's quirk.

## Ruby — `Nokogiri`/`REXML`

| Lib | internal | external | param |
|---|---|---|---|
| `Nokogiri::XML()` | ✓ | ✗ | ✓ |
| `Nokogiri::XML(){noent}` | ✓ | ✓ | ✓ |
| `REXML::Document.new` | ✓ | ✓ | ✓ |

## Node — `xml2js`/`xmldom`/`libxmljs`/`sax`/`fast-xml-parser`

| Lib | internal | external | param |
|---|---|---|---|
| `xml2js` (expat) | ✓ | ✗ | ✗ |
| `xmldom` | ✓ | ✗ | ✗ |
| `libxmljs` | ✓ | ✓ | ✓ |
| `sax` | ✓ | ✗ | ✗ |
| `fast-xml-parser` | ✗ | ✗ | ✗ |
| `node-expat` | ✓ | ✓ | ✓ |

Node is mostly internal-only — XXE is rare — `libxmljs`/`node-expat`
are the exceptions.

## Go — `encoding/xml`

```
xml.Unmarshal / xml.NewDecoder().Decode
```

NO entities at all — `&x;` errors or passes through unexpanded —
Go is XXE-immune by design.

## The "the wrapper matters more than the parser" — lib-by-lib

- `Apache POI` — uses Xerces — inherits Xerces config
- `Apache CXF`/`JAX-WS` — uses StAX — StAX config decides
- `python-docx`/`python-pptx` — lxml — lxml config
- `openpyxl` — ElementTree — internal-only
- `ClosedXML` — `XmlReader` — .NET config
- `xstream`/`jackson-xml` — their own defaults
- `saxon` — the XSLT-processor parse — extension-rich
