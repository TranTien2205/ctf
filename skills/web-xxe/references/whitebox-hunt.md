# Whitebox Hunt — finding the parser in source

## The sink calls — grep these

**Java:**
```java
DocumentBuilderFactory.newInstance()     .newDocumentBuilder()
SAXParserFactory.newInstance()           .newSAXParser()
XMLReaderFactory / XMLInputFactory       .createXMLReader / .createXMLStreamReader
Unmarshaller / JAXBContext               .unmarshal
TransformerFactory                       .newTransformer (XSLT)
XStream / XmlMapper (Jackson-XML)        .fromXML / .readValue
DocumentBuilder.parse / SAXParser.parse  .parse(inputStream|file|string)
DocumentBuilder.parse(InputSource)
new SAXParser().parse
XPathFactory / XPath                     — XPath-inj not XXE but same doc
SchemaFactory / Validator                .newSchema / .validate
Digester / Commons-Digester
dom4j / JDOM SAXBuilder / DocumentHelper
org.dom4j.io.SAXReader
net.sf.saxon / Saxon
```

**.NET:**
```csharp
XmlReader.Create        XmlDocument.Load / LoadXml
XmlSerializer           XDocument.Load / Parse
DataSet.ReadXml         XmlTextReader
XmlUrlResolver          XslCompiledTransform
XmlSchema / XmlDataDocument / XmlDocument
soap / WCF DataContractSerializer
```

**Python:**
```python
lxml.etree.parse / fromstring / XML
xml.etree.ElementTree.parse / fromstring / XML
xml.dom.minidom.parse / parseString
xml.sax.parse / make_parser
xmlrpc.client.loads / ServerProxy
defusedxml.*                             — check which defused module
untangle / xmltodict
```

**PHP:**
```php
simplexml_load_string / simplexml_load_file
DOMDocument->loadXML / ->load
XMLReader::XML / ->open
xml_parse / xml_parser_create
LIBXML_NOENT / LIBXML_DTDLOAD / substituteEntities
```

**Ruby:** `Nokogiri::XML`/`REXML::Document.new`/`XmlSimple`/`Ox`
**Node:** `xml2js`/`libxmljs`/`xmldom`/`fast-xml-parser`/`sax`/`node-expat`
**Go:** `encoding/xml.Unmarshal`/`NewDecoder` — no entities at all — dead

## The fingerprint of a LIVE parser — the missing hardening

Look for what's NOT there:

```java
// Java — DANGEROUS — no features set
DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
DocumentBuilder b = f.newDocumentBuilder();        // resolves external entities

// vs SAFE — features set
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
```

```csharp
// .NET — DANGEROUS — explicit live resolver
var s = new XmlReaderSettings { DtdProcessing = DtdProcessing.Parse,
                                XmlResolver = new XmlUrlResolver() };
// vs default = Prohibit = SAFE
```

```python
# Python — DANGEROUS — lxml default resolves external
lxml.etree.parse(request.body)         # resolve_entities=True default
xml.dom.minidom.parseString(body)      # external entities resolve
xml.sax.parseString(body, handler)     # external entities resolve
# vs SAFE — defusedxml or ElementTree (internal-only)
```

```php
// PHP — DANGEROUS — LIBXML_NOENT or substituteEntities
$d->loadXML($xml, LIBXML_NOENT);
$d->substituteEntities = true;
// vs default — external entities don't expand
```

## The "the parser is inside a library" — second-order parsing

- a `json`→`xml` converter
- an XML-RPC/SOAP lib (`xmlrpc`, `Zeep`, `suds`, `JAX-WS`, `Apache CXF`)
- an `svg`/`docx`/`epub` handler
- a `SAML`/`OIDC`/`WS-Fed` lib
- a `metadata`/`config` importer
- a `feed`/`rss`/`atom` reader
- an `sitemap.xml`/`rss` fetcher

Find what CALLS the parser — the app's own helper or a lib's internals —
then the input route to it.

## The "the lib hardens it" — safe-by-default libs

`defusedxml` (Python), `.NET 4.5.2+` `XmlReader`, Go `encoding/xml`,
`xml2js`/`xmldom` (Node internal-only), hardened `DocumentBuilderFactory`
wrappers (OWASP `SafeXML`, `SAXParsers.createSafe`) — a lib that's
safe-by-default closes the class.

## The "the route to the sink" — trace the input

The sink is `parse($input)` — where does `$input` come from:
`request.body`/`file`/`form`/`soap`/`metadata-url`/`saml-response` —
which route/endpoint carries it — that's your injection point.
