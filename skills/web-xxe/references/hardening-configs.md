# Hardening Configs — what a real fix looks like, and the gaps

## Java — the full Xerces hardening

```java
DocumentBuilderFactory f = DocumentBuilderFactory.newInstance();
f.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
f.setFeature("http://xml.org/sax/features/external-general-entities", false);
f.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
f.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
f.setXIncludeAware(false);
f.setExpandEntityReferences(false);
```

The GAPS a real config may leave:
- `disallow-doctype-decl=false` + only `external-general-entities=false`
  → param-entities + external DTD still live → blind XXE works
- `expandEntityReferences=false` alone → general entities don't expand
  but param-entities do
- no `setXIncludeAware(false)` → XInclude still fetches
- custom `EntityResolver` still resolves — a resolver that wraps
  `URLResolver` fetches anyway

## .NET — `XmlReaderSettings` safe-by-default

```csharp
// SAFE (4.5.2+ default)
var r = XmlReader.Create(stream);                    // DtdProcessing.Prohibit

// DANGEROUS — explicit settings re-enable
var r = XmlReader.Create(stream, new XmlReaderSettings {
    DtdProcessing = DtdProcessing.Parse,             // allows DOCTYPE
    XmlResolver = new XmlUrlResolver()               // resolves external
});
```

The gap: `DtdProcessing.Parse` + `XmlResolver=null` → DOCTYPE allowed
but nothing resolves → internal entities expand, external dead.
`XmlResolver = new XmlUrlResolver()` is the live-resolver tell.

## Python — `lxml` vs `defusedxml`

```python
# SAFE
defusedxml.ElementTree.parse(...)
defusedxml.lxml.parse(...)
lxml.etree.parse(..., parser=lxml.etree.XMLParser(resolve_entities=False, no_network=True))

# DANGEROUS
lxml.etree.parse(...)                     # resolve_entities=True default
xml.sax.parse(...)                        # no hardening by default
xml.dom.minidom.parse(...)
```

The gap: `resolve_entities=False` but `no_network=False` → entities
still fetched, just not substituted → OOB still fires.

## PHP — `libxml`

```php
// SAFE-ish
libxml_set_external_entity_loader(function(){ return null; });
$d = new DOMDocument; $d->loadXML($xml);  // no LIBXML_NOENT → no ext-entity expand

// DANGEROUS
$d->loadXML($xml, LIBXML_NOENT|LIBXML_DTDLOAD);
$d->substituteEntities = true;
```

The gap: `LIBXML_NOENT` alone → external entities expand.
`libxml_set_external_entity_loader(null)` kills fetches.

## Ruby — Nokogiri

```ruby
Nokogiri::XML(xml)                        # default — entities not substituted
Nokogiri::XML(xml){|c| c.noent}           # DANGEROUS — substitute entities
Nokogiri::XML(xml){|c| c.nonet}           # SAFE — no network
```

The gap: `.noent` without `.nonet` → external fetches live.

## libxml2 raw

```c
xmlReadMemory(xml,len,"x",NULL,XML_PARSE_NOENT|XML_PARSE_DTDLOAD)
```

`XML_PARSE_NOENT` = substitute; `XML_PARSE_DTDLOAD` = load external DTD;
`XML_PARSE_NONET` = no network. `XML_PARSE_NOENT` without `NONET` = the
live XXE config.

## The "the config string is the evidence" — whitebox confirmation

Grep the config — the exact flags tell you which doors are open BEFORE
probing:

- `disallow-doctype-decl` → XInclude only
- `DtdProcessing.Parse` + `XmlUrlResolver` → full XXE
- `LIBXML_NOENT` → external entities expand
- `no_network=False` → fetches live

## The safe-default libs — where XXE just dies

`defusedxml` (Python), Go `encoding/xml`, `xml2js`/`xmldom` (Node),
.NET default `XmlReader` — the class is dead unless a non-default path
or a different parser handles the doc.
