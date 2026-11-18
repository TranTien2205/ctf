# Parser Specifics — defaults and hardening per stack

## The question that decides everything — is the parser entity-safe?

Each stack's default config differs. The fingerprints and safe-defaults
below decide your first probe.

## Java — Xerces/`DocumentBuilderFactory`/`SAXParser`/`XMLReader`/`JAXB`/`XStream`/`Dom4j`/`JDOM`/`StAX`

```java
DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(...)
SAXParserFactory.newInstance().newSAXParser().parse(...)
XMLReaderFactory.createXMLReader()
Unmarshaller (JAXB)
XStream.fromXML
DocumentBuilder.parse(InputSource)
XMLInputFactory / StAX
```

**Defaults resolve external entities = YES** in raw `DocumentBuilder`/
`SAXParser` without hardening. Hardening flags:

```java
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
xmlReader.setFeature(...)
xmlReader.setEntityResolver(...)   — custom resolver — may still fetch!
```

The `disallow-doctype-decl` kills DOCTYPE entirely → only XInclude
path remains (also needs `setXIncludeAware(true)` — rare).
`external-general-entities=false` blocks `&x;` external but param-
entities may still resolve — the two flags are independent — a config
that only killed general entities is STILL blind-XXE-able via param.

**Signatures in errors:** `org.xml.sax.SAXParseException`, `xerces`,
`javax.xml.parsers`, `StAX`, `Wstx`, `woodstox`, `saxon`.

## .NET — `XmlReader`/`XmlDocument`/`XmlSerializer`/`DataSet`/`XDocument`/`BinaryFormatter`-adjacent

```csharp
XmlReader.Create(stream)
new XmlDocument(); doc.LoadXml(...)
new XmlSerializer(...).Deserialize(...)
XDocument.Load/Parse
DataSet.ReadXml
XmlTextReader (deprecated)
```

**Default since .NET 4.5.2:** `XmlReader` has `DtdProcessing =
Prohibit` → DOCTYPE rejected outright. `XmlDocument` uses XmlReader
defaults → also Prohibit. Older/looser code:

```csharp
new XmlReaderSettings { DtdProcessing = DtdProcessing.Parse,
                        XmlResolver = new XmlUrlResolver() }   — live XXE
new XmlTextReader(stream) { XmlResolver = new XmlUrlResolver() }
XmlDocument doc = ...; doc.XmlResolver = new XmlUrlResolver();
```

Errors: `System.Xml.XmlException: DTD is prohibited` — the tell for
`DtdProcessing.Prohibit`. `XmlException`/`FileNotFoundException` carry
entity URIs — `error-based.md`.

## Python — `ElementTree`/`lxml`/`minidom`/`xml.sax`/`defusedxml`

```python
xml.etree.ElementTree.parse / fromstring       — internal entities YES, external NO
xml.dom.minidom.parse                          — external entities YES
xml.sax.parse                                  — external entities YES
lxml.etree.parse / fromstring                  — resolve_entities=True default → external YES
xmlrpc.client.loads                            — yes
xml.sax.make_parser().parse                    — yes
defusedxml.ElementTree / lxml / sax / minidom — hardened wrapper — dead
```

**Fingerprint:** lxml/SAX/minidom are the XXE-live ones; stdlib
`ElementTree` only expands INTERNAL entities — `&x;` internal works,
`SYSTEM`-external doesn't. `defusedxml` presence = hardened.

**Errors:** `lxml.etree.XMLSyntaxError`, `ExpatError`, `xml.sax`
`SAXParseException`, `xml.etree.ElementTree.ParseError`.

## PHP — `simplexml_load_`/`DOMDocument`/`XMLReader`/`xml_parse`/`libxml`

```php
simplexml_load_string($xml)
simplexml_load_file
new DOMDocument(); $d->loadXML($xml, LIBXML_NOENT)
XMLReader::XML($xml)
xml_parse($parser,$xml)
```

**Default:** `LIBXML_NOENT` (substitute entities) is OFF —
`simplexml_load_string` by default does NOT expand external entities!
The classic PHP XXE requires `LIBXML_NOENT` OR an explicit
`$d->substituteEntities=true`/`LIBXML_DTDLOAD|LIBXML_DTDATTR` context —
OR the doc declares entities internally (`&x;` internal resolves
without NOENT for *internal* entities? — internal general entities
always expand; EXTERNAL entities need NOENT or a DTD-loader flag).

So PHP first probe = internal entity (`&x;` literal works always when
entities expand at all) → external entity needs NOENT — the verified
card's name literally is `simplexml-noent` — the flag was on.

**Errors:** `libxml` warnings — `Warning: simplexml_load_string(): ...
failed to load external entity`.

## Ruby — Nokogiri / REXML

```ruby
Nokogiri::XML(xml)                 — default NO external entities
Nokogiri::XML(xml){|c| c.strict.nonet.noent} — opts matter
REXML::Document.new(xml)           — external entities YES (historically)
```

Nokogiri default: `nonet` NOT set by default on `Nokogiri::XML()` —
`Nokogiri::XML()` default = `ParseOptions::DEFAULT_XML` = recover+
noent? — actually `RECOVER | NOENT | NONET`... varies — TEST IT.
`REXML` resolves external entities by default (and has had expansion-
DoS CVEs).

## Node — `xml2js`/`libxmljs`/`xmldom`/`fast-xml-parser`/`sax`

```javascript
xml2js.parseString               — expat-based — external entities NO
xmldom (DOMParser)               — internal only
libxmljs.parseXml                — libxml2 — external YES if opts
sax.parser(strict)               — internal only
fast-xml-parser                  — no entity support at all
```

Most Node parsers DON'T resolve external entities — XXE is rare in JS
stacks; `libxmljs`/`node-expat` with options enabled are the exception.

## Go — `encoding/xml`

```go
xml.Unmarshal / xml.NewDecoder().Decode
```

**Go stdlib does NOT resolve entities at all** — `&x;` →
`"invalid entity &x;"` error or unexpanded text. Go XXE is essentially
impossible via stdlib — the class is dead for Go targets.

## The fingerprint table — error → parser

| Error fragment | Stack |
|---|---|
| `SAXParseException`/`xerces`/`org.xml.sax` | Java |
| `XmlException`/`System.Xml`/`DTD is prohibited` | .NET |
| `libxml`/`simplexml`/`DOMDocument`/`XMLReader` | PHP |
| `XMLSyntaxError`/`lxml`/`ElementTree`/`ParseError`/`ExpatError`/`xml.sax`/`defusedxml` | Python |
| `REXML`/`Nokogiri` | Ruby |
| `encoding/xml`/`XML syntax error` | Go |
| `Expat`/`xml2js`/`sax`/`xmldom` | Node |

## Falsifiers

- parser = Go `encoding/xml`, or `defusedxml`, or .NET default
  `DtdProcessing.Prohibit` AND no XInclude path → class dead
