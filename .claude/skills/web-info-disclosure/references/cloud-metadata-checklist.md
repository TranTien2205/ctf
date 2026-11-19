# Cloud metadata and internal endpoints — operational checklist

When the app runs on a cloud host, metadata services and internal admin endpoints may be reachable directly — or via SSRF, which is a different class.

## Checklist

- [ ] This class covers metadata reachable through the APP's own surface — direct SSRF to metadata is web-ssrf's class.
- [ ] Check headers for cloud hints (X-Amz*, Azure headers, GCP signatures).
- [ ] If the app proxies or fetches URLs, the metadata path goes through web-ssrf, not here.

## Abort conditions

- Metadata is SSRF territory when it needs a fetch primitive — route to web-ssrf.
- IMDSv2 requires a PUT token first — a simple GET failing isn't proof of absence.
- Don't scan internal ranges — the scope is the supplied target.

## Falsifier

Falsifier — no cloud signature in headers and no internal endpoint surface: out of scope for this class.

## Cross-references

`../web-ssrf/` · `header-disclosure.md`
