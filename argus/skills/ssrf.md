# SSRF - server-side request forgery

**When:** the server fetches a URL you control or influence. Signals: `url=`,
`callback=`, `webhook`, "import from URL", PDF/image renderers, admin bots,
avatar-by-URL, RSS importers, file-upload-from-link.

`probe_ssrf(url, param)` walks the internal-target ladder (loopback, link-local metadata, decimal/IPv6 encodings, redirect chains). The class is capped at `candidate` here on purpose - proving it needs an out-of-band collector the target can reach, and none ships with this package.

## Detect

1. Point the parameter at a controlled endpoint you can observe. In-scope
   option: a path on the target itself (`url=http://127.0.0.1:<port>/`) - a
   different response vs an unreachable host proves the server fetched.
2. Compare three cases and quote the differences:
   - reachable in-scope URL
   - unroutable address (`http://10.255.255.1/`) - should error/timeout
   - closed port on the target host (`127.0.0.1:1`)
   Differential error/timing/content = the fetch is real and you control it.
3. Cloud targets: try `http://169.254.169.254/latest/meta-data/` (AWS),
   `http://metadata.google.internal/` (GCP, needs header
   `Metadata-Flavor: Google` - note when you cannot set headers),
   `http://169.254.169.254/metadata/instance?api-version=2021-02-01` (Azure,
   header `Metadata: true`).

## What counts as proof for a report

- Response contains content only the server could reach (internal service
  banner, cloud metadata keys) - high/critical.
- Blind SSRF: timing/error oracle distinguishes open vs closed internal
  ports - medium-high; state honestly that read-back was not possible.
- Scheme flexibility: `file:///etc/passwd`, `gopher://`, `dict://` raise
  impact dramatically if accepted.

## Bypasses for naive filters

- Host obfuscation: decimal `2130706433`, hex `0x7f000001`, octal `0177.0.0.1`,
  short `127.1`
- DNS tricks: `localtest.me`, `nip.io` domains resolving to 127.0.0.1
- Redirect jump: your in-scope URL 302s to the internal target
- URL parsing: `http://allowed.com@127.0.0.1/`, `http://127.0.0.1#allowed.com`,
  `http://allowed.com.127.0.0.1.nip.io`
- Enclosed alphanumerics/unicode in hostnames against regex filters

## Blind spots to check

SSRF is often only reachable via a second feature: the webhook you register
fires later, the PDF renders the URL on fetch, the import job runs async.
Trigger the consumer and read its output before calling it dead.

## Falsifier

Controlled/uncontrolled destinations produce identical responses and no
outbound fetch is observable through any consumer.

## Severity guide

Internal resource read-back: high. Cloud credentials/metadata: critical.
Port-scan oracle only: medium. Unverifiable single case: info/lead.
