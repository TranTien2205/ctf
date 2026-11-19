# Cloud metadata and internal endpoints — case catalogue

When the app runs on a cloud host, metadata services and internal admin endpoints may be reachable directly — or via SSRF, which is a different class.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /latest/meta-data or 169.254.169.254 reachable | metadata exposed | cloud creds |
| 2 | internal admin port on the same host | misconfigured exposure | probe |
| 3 | kubernetes/azure/gcp metadata paths | platform metadata | read tokens |

## Falsifier

Falsifier — no cloud signature in headers and no internal endpoint surface: out of scope for this class.

## Coverage notes

- Metadata is SSRF territory when it needs a fetch primitive — route to web-ssrf.
- IMDSv2 requires a PUT token first — a simple GET failing isn't proof of absence.
- Don't scan internal ranges — the scope is the supplied target.

## Cross-references

`../web-ssrf/` · `header-disclosure.md`
