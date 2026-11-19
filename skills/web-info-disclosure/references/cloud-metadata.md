# Cloud metadata and internal endpoints

When the app runs on a cloud host, metadata services and internal admin endpoints may be reachable directly — or via SSRF, which is a different class.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /latest/meta-data or 169.254.169.254 reachable | metadata exposed | cloud creds |
| internal admin port on the same host | misconfigured exposure | probe |
| kubernetes/azure/gcp metadata paths | platform metadata | read tokens |

## Steps

1. This class covers metadata reachable through the APP's own surface — direct SSRF to metadata is web-ssrf's class.
2. Check headers for cloud hints (X-Amz*, Azure headers, GCP signatures).
3. If the app proxies or fetches URLs, the metadata path goes through web-ssrf, not here.

## Falsifier

Falsifier — no cloud signature in headers and no internal endpoint surface: out of scope for this class.

## Traps

- Metadata is SSRF territory when it needs a fetch primitive — route to web-ssrf.
- IMDSv2 requires a PUT token first — a simple GET failing isn't proof of absence.
- Don't scan internal ranges — the scope is the supplied target.

## Commands

```bash
curl -sI '$BASE/' | grep -iE 'x-amz|x-ms|via|server'
```

## Cross-references

`../web-ssrf/` · `header-disclosure.md`
