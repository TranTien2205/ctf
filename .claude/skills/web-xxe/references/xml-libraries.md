# XML Libraries — the app-facing parsers per ecosystem

## Java — the wrapper landscape

### `DocumentBuilderFactory`/`DocumentBuilder` (JAXP-DOM)

```java
DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
DocumentBuilder b = f.newDocumentBuilder();
Document d = b.parse(inputStream);
```

Raw default = external entities ON. The classic XXE line.

### `SAXParserFactory`/`SAXParser` (JAXP-SAX)

```java
SAXParserFactory f = SAXParserFactory.newInstance();
SAXParser p = f.newSAXParser();
p.parse(inputStream, handler);
```

Default = entities ON.

### `XMLReaderFactory`/`XMLReader` (SAX2)

```java
XMLReader r = XMLReaderFactory.createXMLReader();
r.parse(inputSource);
```

### `XMLInputFactory`/`XMLStreamReader` (StAX)

```java
XMLInputFactory f = XMLInputFactory.newInstance();
XMLStreamReader r = f.createXMLStreamReader(stream);
```

StAX — the streaming parser — `IS_SUPPORTING_EXTERNAL_ENTITIES`/`SUPPORT_DTD`
properties — the StAX-specific hardening.

### `JAXB`/`Unmarshaller`

```java
JAXBContext c = JAXBContext.newInstance(X.class);
Unmarshaller u = c.createUnmarshaller();
u.unmarshal(stream);
```

JAXB uses SAX underneath — the Unmarshaller's parser config decides.

### `TransformerFactory`/`Transformer` (JAXP-XSLT)

```java
TransformerFactory f = TransformerFactory.newInstance();
Transformer t = f.newTransformer(new StreamSource(stream));
```

XSLT parse — the stylesheet is the surface — `xxe-to-rce.md`.
`FEATURE_SECURE_PROCESSING`/`ACCESS_EXTERNAL_DTD`/`ACCESS_EXTERNAL_STYLESHEET`.

### `XPathFactory`/`XPath`

```java
XPath x = XPathFactory.newInstance().newXPath();
x.evaluate(expr, doc);
```

The `doc` parse — XPath-eval on a doc — the parse is the surface.

### `SchemaFactory`/`Schema`/`Validator`

```java
SchemaFactory f = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
Schema s = f.newSchema(new StreamSource(stream));
```

Schema-load — the schema-file itself is XML — `schemaLocation` fetch.

### `Digester` (Commons)

```java
Digester d = new Digester();
d.parse(stream);
```

### `dom4j`/`SAXReader`/`DocumentHelper`

```java
SAXReader r = new SAXReader();
Document d = r.read(stream);
DocumentHelper.parseText(xml);
```

dom4j's SAXReader — external entities ON by default historically.

### `JDOM`/`SAXBuilder`

```java
SAXBuilder b = new SAXBuilder();
Document d = b.build(stream);
```

### `XStream`/`XmlMapper`/`Jackson-Xml`/`Castor`/`XmlBeans`/`JibX`

```java
XStream x = new XStream();
x.fromXML(xml);
XmlMapper m = new XmlMapper();
m.readValue(xml, X.class);
```

Data-binding libs — the parse is under the hood — the lib's default
decides.

### `Saxon`/`net.sf.saxon`/`s9api`

Saxon — the XSLT/XQuery processor — extension-rich — `xxe-to-rce.md`.

### `woodstox`/`WstxInputFactory` (StAX impl)

### `Jersey`/`Spring`/`CXF`/`Metro`/`Axis2` — the framework layer

The framework's message-reader — `MessageBodyReader`/`XMLStreamReader`/
`StAX`/`DocumentBuilderFactory` — the framework's config decides —
`spring-ws`/`cxf` have their own hardening flags.

## .NET — the wrapper landscape

### `XmlReader.Create`

```csharp
XmlReader.Create(stream)                              // default Prohibit
XmlReader.Create(stream, settings)                    // settings decide
```

### `XmlDocument`/`XmlDataDocument`

```csharp
new XmlDocument().LoadXml(xml)
new XmlDocument().Load(stream)
doc.XmlResolver = new XmlUrlResolver()                // the dangerous line
```

### `XDocument`/`XElement`

```csharp
XDocument.Load(stream)
XDocument.Parse(xml)
```

### `XmlSerializer`/`DataContractSerializer`/`BinaryFormatter`

```csharp
new XmlSerializer(typeof(T)).Deserialize(stream)
new DataContractSerializer(typeof(T)).ReadObject(stream)
```

### `XmlTextReader` (deprecated)

```csharp
new XmlTextReader(stream)          // Prohibit default in modern .NET
```

### `XmlUrlResolver`/`XmlSecureResolver`

```csharp
XmlResolver = new XmlUrlResolver()                    // the live resolver
XmlResolver = null                                    // the safe resolver
XmlResolver = new XmlSecureResolver(new XmlUrlResolver(), "...")  // scoped
```

## Python — the wrapper landscape

### `xml.etree.ElementTree`

```python
ElementTree.parse(file)
ElementTree.fromstring(xml)
ET.XML(xml)
```

Internal-entities only — external doesn't resolve.

### `xml.dom.minidom`

```python
xml.dom.minidom.parse(file)
xml.dom.minidom.parseString(xml)
```

External entities resolve — the dangerous one.

### `xml.sax`

```python
xml.sax.parse(file, handler)
xml.sax.make_parser().parse(file)
xml.sax.parseString(xml, handler)
```

`feature_external_ges`/`feature_external_pes` — the SAX feature-flags —
external ON by default in some versions.

### `lxml.etree`

```python
lxml.etree.parse(file)
lxml.etree.fromstring(xml)
lxml.etree.XML(xml)
lxml.etree.parse(file, parser=lxml.etree.XMLParser(resolve_entities=True))
```

`resolve_entities`/`no_network`/`load_dtd` — the lxml flags — the
dangerous default is `resolve_entities=True`.

### `xmlrpc.client`/`xmlrpc.server`

```python
xmlrpc.client.loads(xml)
```

The XML-RPC deserializer — historically resolves entities.

### `untangle`/`xmltodict`/`xmljson`/`xmljson.parker`

```python
untangle.parse(file)
xmltodict.parse(xml)
```

Wrappers — most use `expat`/`sax` internally — inherit the underlying
parser's behavior.

### `defusedxml`

```python
defusedxml.ElementTree.parse(...)
defusedxml.lxml.parse(...)
defusedxml.sax.parse(...)
defusedxml.minidom.parse(...)
defusedxml.xmlrpc.loads(...)
```

The hardened drop-in — `EntitiesForbidden`/`DTDForbidden` — dead.

## PHP — the wrapper landscape

### `simplexml`

```php
simplexml_load_string($xml)
simplexml_load_file($file)
new SimpleXMLElement($xml)
new SimpleXMLElement($xml, LIBXML_NOENT)
```

`LIBXML_NOENT` flag or default — the external-entity switch.

### `DOMDocument`

```php
$d = new DOMDocument();
$d->loadXML($xml)
$d->loadXML($xml, LIBXML_NOENT|LIBXML_DTDLOAD)
$d->load($file)
$d->substituteEntities = true
```

### `XMLReader`

```php
$r = new XMLReader();
$r->XML($xml)
$r->open($file)
$r->setParserProperty(XMLReader::SUBST_ENTITIES, true)
```

`XMLReader::SUBST_ENTITIES` — the property flag.

### `xml_parse`/`xml_parser_create` (expat)

```php
$p = xml_parser_create();
xml_parse($p, $xml);
xml_parse_into_struct($p, $xml, $vals);
```

expat — external entities resolve — `xml_set_external_entity_ref_handler`.

## Ruby — the wrapper landscape

```ruby
Nokogiri::XML(xml)
Nokogiri::XML(xml){|c| c.noent}
Nokogiri::XML(xml){|c| c.nonet}
REXML::Document.new(xml)
REXML::Parsers::PullParser.new
Ox.load(xml)
Ox.parse(xml)
XmlSimple.xml_in(xml)
Gyoku.xml
Noriben
```

## Node — the wrapper landscape

```javascript
xml2js.parseString(xml, cb)               — expat — internal only
new xmldom.DOMParser().parseFromString(x)  — internal only
libxmljs.parseXml(x)                       — libxml2 — live
sax.parser(true).write(x)                  — internal only
fast-xml-parser.parse(x)                   — no entities
node-expat                                 — external live
xml-js / @xmldom/xmldom
```

## Go

```go
xml.Unmarshal([]byte, &v)
xml.NewDecoder(r).Decode(&v)
```

`encoding/xml` — no entities — dead.

## Perl

```perl
XML::Simple
XML::LibXML
XML::Parser
XML::Twig
XML::LibXSLT
```

`XML::LibXML` — libxml2 — live; `XML::Parser` — expat — live.

## The "the lib's default is the verdict" — summary

The lib's default hardening decides the class — `hardening-configs.md`
has the config-strings to grep.
