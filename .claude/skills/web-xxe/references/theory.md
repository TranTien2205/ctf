# Theory — the XML/entity model behind the bugs

## The parse pipeline — where entities live

```
bytes → tokenizer → parser → DOM/sax-events → app
         ↑                ↑
         entities expand  entities expand
         in the DTD       in the body
```

XML is two grammars: the DTD (inside `<!DOCTYPE [...]>`) and the body.
Entities expand in BOTH but with different rules — that's why
`&x;`/`%x;` have different scopes.

## The entity kinds — the type system

| Kind | Syntax | Scope | Resolves? |
|---|---|---|---|
| Internal general | `<!ENTITY x "v">` | body `&x;` | always |
| External general | `<!ENTITY x SYSTEM "uri">` | body `&x;` | parser-config |
| Internal param | `<!ENTITY % p "v">` | DTD-only `%p;` | always |
| External param | `<!ENTITY % p SYSTEM "uri">` | DTD-only `%p;` | parser-config |
| Unparsed | `<!ENTITY u SYSTEM "uri" NDATA n>` | attr of type ENTITY | parser-config |
| Predefined | `&lt;` `&amp;` `&quot;` `&apos;` `&gt;` | body | always |

## The parse-order — when which expansion fires

1. DOCTYPE internal subset parses → internal entities defined → param
   entities expand DURING the internal-subset parse
2. External subset (SYSTEM/PUBLIC on DOCTYPE) fetched → its param
   entities expand
3. The body parses → `&x;` general entities expand
4. Attributes in ATTLIST defaults expand
5. `NDATA` entities resolved when the ENTITY-typed attribute is read

The order matters: param-entities in the internal subset expand at
DOCTYPE-parse — before the body even starts — so `%x;` fires FIRST.

## The "external entity vs parameter entity" split — the two config flags

Java/Xerces treats them separately:
- `external-general-entities` — `&x;` external
- `external-parameter-entities` — `%x;` external
- `nonvalidating/load-external-dtd` — the DOCTYPE's own SYSTEM fetch

A config that kills general-entities leaves param-entities + DTD-fetch
live → blind XXE works even though `&x;` doesn't — the partial-
hardening gap.

## The "the fetch is the vuln, not the substitution" — the insight

An external entity does two things: FETCH the URI, SUBSTITUTE the
content. The fetch alone is SSRF — even if substitution is off, the
fetch may still fire (the parser fetched then discarded). The OOB-
listener sees the fetch even when the echo is suppressed.

## The "the DTD is a program" — the param-entity-as-code insight

Param entities inside an external DTD are effectively code — `%wrap;`
builds a NEW entity declaration dynamically → `%send;` executes it.
The DTD is a macro-language — the blind-exfil DTD is a program that
reads a file and builds an exfil URL.

## The `&#xNN;`/`&#NN;` decode — char-refs inside entity values

`<!ENTITY % e "<!ENTITY &#37; s ...">` — `&#37;` decodes to `%` AT THE
POINT the entity value is PROCESSED — not when declared — the char-
ref-in-value is the engine for nested param-entity construction.

## The "the internal-subset is stricter" — the Xerces rule

Inside the INTERNAL subset, a param-entity cannot be referenced in
certain positions (the "PE in internal subset" rule) — inside the
EXTERNAL subset (a fetched DTD), it can. This is WHY the exfil-DTD
must be external — `external-dtd.md` explains the `&#37;`-composition
that builds a declaration inside the external DTD.

## The `standalone` flag — the declaration-need signal

`standalone="yes"` asserts no external declarations — a validating
parser may refuse the external DTD entirely. `standalone="no"` or
omitted → external DTD allowed.

## The XML 1.0 vs 1.1 split — name-rules

XML 1.1 allows a wider `NameChar` set — some parsers accept XML 1.1,
some don't — a parser-mismatch surface for exotic names.

## The well-formedness contract — the parse-error floor

A doc must be well-formed to parse at all — `&x;` undeclared →
`Entity 'x' not defined`. The entity-reference rules are themselves
the fingerprint mechanism — the ERROR tells you the parser.

## The "the app may re-serialize" — the DOM round-trip

`parse → DOM → serialize` — the app may re-serialize the DOM — the
expanded entity value becomes literal text in the output — the "the
app echoes the expanded value back" channel.

## The "the DOM doesn't remember the entity" — the post-expansion truth

Once `&x;` expands, the DOM holds the CONTENT, not the reference —
a re-serialized doc shows the content, not `&x;` — the echo-check
looks for the CONTENT `XXE_PROBE`, not the `&x;` token.
