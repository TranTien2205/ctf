# XXE via content-type confusion

The most reliable XXE door in a modern app is not an XML endpoint — it is a
JSON endpoint whose body parser *also* speaks XML. The client sends JSON, the
framework picks the parser by `Content-Type`, and `application/xml` reaches a
parser that resolves entities.

## Probe that worked (WAFfles or Ice Cream)

Post the *same body* to the JSON endpoint with an XML content type and an XML
document that declares an internal entity in the echoed field:

```xml
POST /api/echo HTTP/1.1
Content-Type: application/xml

<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY x "canary-xxe">]>
<r><field>&x;</field></r>
```

Expected: the response echoes `canary-xxe` — the entity resolved, so the
parser is entity-capable and the XML path is live. Falsifier: the field comes
back as literal `&x;`, the endpoint rejects the content type, or the parser
errors on the DOCTYPE — entities are disabled or the route is JSON-only.

## The escalate ladder

Once `&x;` resolves in the echo:

| Step | Entity | Reads |
|---|---|---|
| external file | `<!ENTITY x SYSTEM "file:///etc/passwd">` | local file content |
| SSRF | `<!ENTITY x SYSTEM "http://169.254.169.254/...">` | internal HTTP |
| parameter entity | `<!ENTITY % e SYSTEM "..."> %e;` | exfil when echo is blind |
| error channel | file URL whose content lands in a parse error | blind exfil via error |

When the echo is blind, exfiltrate through a parameter-entity DTD hosted on a
host you control — the outbound fetch is itself the confirmation.

## Falsifier

The endpoint refuses non-JSON content types on every route, or the XML parser
strips DOCTYPE — no entity resolves on any field.

## Traps

- Test *every* route with the XML content type; parsers are configured per
  endpoint, and the one that accepts it may not be the obvious one.
- `text/xml` and `application/xml` can reach different parser configurations —
  send both.
- A WAF that inspects JSON may not inspect XML bodies at all — the same probe
  doubles as a filter bypass.
