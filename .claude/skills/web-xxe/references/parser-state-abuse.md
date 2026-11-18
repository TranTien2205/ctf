# Parser State Abuse — the state machine quirks

## The "the parser is stateful" — the context that matters

A SAX parser fires events — `startElement`/`characters`/`endElement` —
entity expansion happens inside `characters()` — an entity whose content
CONTAINS `<`/`&`/`]]>` breaks the text-run — the parse state is the
surface.

## The "the expansion happens in `characters`" — the text-context

`&x;` inside a text node expands INTO the text — the expanded content
is a text-run — if the file content has `<`, the parser sees it as
markup AFTER expansion? No — entity content is NOT re-parsed as
markup — it's inserted as literal text — UNLESS the entity is
declared as `parse="xml"` in an XInclude — the re-parse nuance.

## The "the entity content is literal, not re-parsed" — the rule

`&x;` expands to `file://` content as CHARACTER DATA — `<`/`&` inside
the file don't create elements — they appear as literal chars in the
DOM text — but the ENTITY REFERENCE ITSELF is parsed — the file's
`<` can't introduce a tag, but it CAN break the text-run if it
contains `]]>`.

## The "the param-entity inside a value" — the value-expansion

`<!ENTITY % a "<!ENTITY &#37; b SYSTEM 'x'>">` — when `%a;` is
referenced, its VALUE is re-scanned — `%b;` inside the value expands
RECURSIVELY — the DTD-as-macro-language insight.

## The "the expansion order" — the parse sequence

```
internal-subset param entities expand → DURING internal-subset parse
external-subset fetched → its param entities expand
body general entities expand → as elements parse
attribute defaults expand → when the ATTLIST fires
NDATA entities → when ENTITY-typed attr read
```

The order decides WHICH fetch fires first — the exfil-DTD's `%file;`
fetches BEFORE the body's `&send;` — the read-then-send order.

## The "the recursive expansion" — entity-in-entity

```xml
<!ENTITY a "x">
<!ENTITY b "&a;&a;&a;">
<!ENTITY c "&b;&b;&b;">
```

`&c;` → `&b;&b;&b;` → each `&b;` expands → 9× `x` — the recursive
expansion is the Billion-Laughs engine — `billion-laughs.md`.

## The "the entity-loop" — the self-reference

```xml
<!ENTITY a "&b;">
<!ENTITY b "&a;">
```

Parser must detect the cycle — `Detected an entity reference loop`/
`recursive entity` — the error type fingerprints the parser.

## The "the CDATA boundary" — the `]]>` trap

A file containing `]]>` inside an entity breaks the containing CDATA
section — `cdata-wrapping.md` composes `<![CDATA[` + file + `]]>` —
the file's own `]]>` terminates the wrapper early — the truncated read.

## The "the `standalone` state" — the parse-context flag

`standalone="yes"` → no external declarations — a validating parser
refuses external DTDs — the parse state affects entity resolution.

## The "the namespace-context" — `xmlns` scoping

`&x;` inside a namespaced element — the entity expands regardless —
namespaces don't affect entity resolution — but an entity whose
content is `xmlns:foo="..."` can inject a namespace — a weird edge.

## The "the `xml:space`/`xml:lang`/`xml:base`" — the xml-attrs

`xml:base` changes URI resolution — `xml:space`/`xml:lang` are
hints — `xml:base="file:///"` + a relative `href` = the file-read —
`parser-abuse.md`.

## The "the app holds the DOM" — the post-parse state

The DOM holds EXPANDED text — a `toString`/`serialize` shows content
not `&x;` — the re-serialization echo channel.

## The "the SAX-handler sees the expanded text" — the event model

`characters()` receives the EXPANDED text — a handler that logs events
leaks the file content in the event stream — the "the log is the
channel" edge.

## Falsifiers

- the parser is a non-validating non-entity parser (Go `encoding/xml`,
  a strict JSON-shim) → no expansion at all → dead
