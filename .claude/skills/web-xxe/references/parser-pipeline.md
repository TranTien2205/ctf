# Parser Pipeline — the full lifecycle of an XXE

## Stage 0 — the input reaches a parser

```
HTTP body → Content-Type router → deserializer → XML parser
```

Which parser — `Content-Type`, `Accept`, `?format=`, the field-name,
the endpoint's convention — `multi-parser.md`.

## Stage 1 — tokenization

The bytes are scanned — `<`, `&`, `]]>`, quotes — the tokenizer sees
`<!DOCTYPE` and enters the DTD-scan state — the `encoding=`/`BOM` is
honored here — `utf-encodings.md`.

## Stage 2 — DOCTYPE internal-subset

The `[...]` block parses — each declaration type is recognized —
`<!ENTITY`/`ELEMENT`/`ATTLIST`/`NOTATION`/PI/comment — entities are
DEFINED here — param-entities in the internal subset expand DURING
this parse.

## Stage 3 — the external-subset fetch

`<!DOCTYPE r SYSTEM "uri">` or `PUBLIC ... "uri"` — the parser fetches
the external DTD — the DTD's own param-entities expand — the DTD's
declarations merge with the internal subset — internal wins on
collision.

## Stage 4 — the entity-resolution hooks

The parser's `EntityResolver`/`LSResourceResolver`/`XmlResolver`/
`libxml-entity-loader` is called for EVERY entity — a custom resolver
can map, refuse, or fetch — the resolver is code — `parser-abuse.md`.

## Stage 5 — the body parse

Elements/attributes/text parse — `&x;` general entities expand at
each reference — `NDATA`-typed attributes resolve — `xpointer`/
`xinclude`/`schemaLocation`/`xml-stylesheet`/`xml-model`/`xml:base`
fetches fire at their elements.

## Stage 6 — the DOM/SAX event emission

- DOM — the tree holds EXPANDED text — `getTextContent()` returns the
  substituted value
- SAX — `characters()` fires with expanded text — the event-stream
  carries the content
- StAX — `getText()`/`getElementText()` — expanded

## Stage 7 — the app's use

- the DOM is read (`getTextContent`, `toString`, a field accessor)
- the doc is re-serialized (`toString`/`serialize`/`transform`)
- a value is compared/logged/echoed
- a value reaches a sink (SQL, command, file)

## Stage 8 — the error-path

Any stage's failure → the exception — the exception carries the URI/
entity-name — the error-channel — `errors-deep.md`.

## The "each stage is a surface" — the full map

| Stage | Surface | Class |
|---|---|---|
| Content-Type router | wrong-type XML | `content-type-confusion` |
| tokenizer | encoding | `utf-encodings` |
| DOCTYPE-internal | entity decls | XXE |
| ext-subset-fetch | DTD URL | OOB/SSRF |
| EntityResolver | custom resolver | resolver-code |
| body-parse | `&x;` | XXE |
| ATTLIST-default | attr entity | `xml-structure-abuse` |
| NDATA | unparsed entity | `xml-structure-abuse` |
| xpointer/xinclude | fragment fetch | `xinclude` |
| schemaLocation | schema fetch | `parser-abuse` |
| xml-stylesheet | XSLT fetch | `xxe-to-rce` |
| xml-model | schema fetch | `parser-abuse` |
| xml:base | resolution-base | `parser-abuse` |
| DOM-read | expanded text | echo-channel |
| re-serialize | substituted doc | echo-channel |
| error | exception-URI | `errors-deep` |

## The "the resolver is the chokepoint" — the security-hook

`EntityResolver`/`LSResourceResolver`/`XmlResolver`/`libxml-loader` is
called for EVERY external entity — a null-resolver kills all external
resolution — the resolver config is the single-point-of-control —
`hardening-configs.md`.

## The "the parse is lazy" — the deferred-parse surface

Some parsers lazy-load — a DTD fetch might not fire until the doc is
accessed — the "send-and-forget" surface where the fetch fires on a
LATER access — `second-order.md`.

## The "the parse is a pipeline" — multi-stage processing

`parse → transform → validate → serialize` — each stage may use a
DIFFERENT parser config — the first-stage-parse may be hardened, the
XSLT-transform may use a raw parser — `multi-parser.md`.
