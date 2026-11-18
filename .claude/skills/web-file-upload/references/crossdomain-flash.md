# Flash/Legacy Uploads — crossdomain.xml and .swf shapes

## `crossdomain.xml` — the flash-era wildcard policy

A `crossdomain.xml` upload that lands on a domain's root gives Flash
(and its legacy emulation) cross-site access:

```xml
<cross-domain-policy>
  <allow-access-from domain="*" />
</cross-domain-policy>
```

If the app serves it at `/crossdomain.xml` — old Flash content can read
any path on that origin. Legacy but still lands in some audits.

## `.swf` upload — the actionscript carrier

A `.swf` file served `application/x-shockwave-flash` — embeddable on the
same origin — an attacker-controlled swf calls `ExternalInterface`/`navigateToURL`/
`getURL(javascript:...)` — same-origin XSS via plugin content.

- `allowScriptAccess="always"` + same-domain swf = DOM access
- `crossdomain.xml` widens it further

## Other legacy carriers

- `.jar` served as `application/java-archive` — applet XSS
- `.xap` Silverlight — same idea
- `.pdf` with embedded Flash — pdf-deep.md

## Why this still matters in 2026

- corporate/enterprise apps with legacy plugin ingestion
- CTF "the old way" challenges
- crossdomain.xml is still occasionally served on real CDNs

## The "is the plugin actually loaded" question

Modern browsers don't run Flash — the upload is inert in a modern client.
The exploit needs either:
- the challenge's bot runs an old browser
- a legacy emulator is in play
- the file's parse by a server-side tool (swf tools) is the sink — a
  server-side swf parser vulnerability, not client-side exec

## Falsifiers

- no plugin/legacy runtime exists on the client side and no server-side
  tool parses the format

## Output to record

- whether a `crossdomain.xml` serves at root + whether the swf's target
  runtime exists
