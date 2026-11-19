# Edge cases — the CORS corners that catch you

The non-obvious behaviors that break a naive analysis or a naive
exploit.

---

## 1. The `*+credentials` rejection — the universal rule

```text
ACAO:* + a fetch with credentials:'include' → the browser rejects
EVERY time, in every engine — 'The value of the
Access-Control-Allow-Origin header in the response must not be the
wildcard * when the request's credentials mode is include'.
```

## 2. The `Vary: Origin` omission — a cache that lies

```text
a reflected ACAO without Vary: Origin — a shared cache keyed only
on the URL serves the attacker-origin response to other visitors —
a cache-poison+CORS blend; the app's per-origin response is masked.
```

## 3. The `Access-Control-Max-Age` persistence — a stale preflight

```text
a long Max-Age caches the preflight — a tightened CORS still uses
the cached permissive answer. a test in the same browser session
sees the stale answer — a fresh context is the clean test.
```

## 4. The `SameSite=None` requirement — Secure is mandatory

```text
SameSite=None REQUIRES Secure — a SameSite=None cookie without
Secure is rejected by the browser — the credentialed read needs
Secure+None together.
```

## 5. The `Set-Cookie` in a CORS response — a cross-origin set

```text
a cross-origin response CAN set a cookie — but the cookie's own
SameSite decides whether it attaches to later fetches. a CORS-read
doesn't automatically carry a new cookie forward.
```

## 6. The `Access-Control-Expose-Headers` edge — a readable token

```text
a token in a response header (X-Token, Authorization) isn't readable
by JS unless listed in Expose-Headers — a 'the header is there but
JS can't see it' edge.
```

## 7. The `Content-Type: application/json` preflight edge

```text
a JSON-bodied POST is non-simple — needs a preflight. but a
urlencoded or text/plain POST is simple — no preflight. the
'content-type decides the preflight' edge.
```

## 8. The `null` origin's many sources — which opaque context

```text
'sandboxed iframe' → null; 'data: URL' → null; 'file: page' → null
(modern) or 'file://' (older); 'a redirect chain' → the final
navigation's origin may be null. test which applies.
```

## 9. The `Origin` on a same-origin request — the absent case

```text
a same-origin request's Origin header may be absent or same-origin —
the CORS check only applies cross-origin. a same-origin 'Origin:
https://target.com' is a no-op.
```

## 10. The OPTIONS preflight's own auth — no credentials on preflight

```text
the preflight NEVER carries credentials — it's a permission probe,
not the real request. a preflight that 'fails auth' is a misconfig —
the OPTIONS handler should be unauthenticated.
```

## 11. The `no-cors` opaque write — CSRF's twin

```text
mode:'no-cors' fires a write — the response is opaque (unreadable)
but the write lands. the SAME fetch mechanics as the CORS read,
opposite halves — the web-csrf class.
```

## 12. The `Referrer-Policy` edge — a Referer-gated fallback

```text
an app that falls back to checking Referer when Origin is absent —
a page whose Referer-Policy leaks the target string may pass a
Referer check where Origin fails — a rare fallback check.
```

## 13. The iframe-sandbox `allow-same-origin` edge

```text
a sandboxed iframe WITHOUT allow-same-origin → null origin.
WITH allow-same-origin → the iframe's real origin — a different
CORS answer for the same page.
```

## 14. The `Cross-Origin-Resource-Policy` separate gate

```text
CORP gates LOADING (img/script/iframe), not fetch-READING — a
CORP:same-origin resource won't load cross-origin even if CORS
would allow the fetch — a separate layer.
```

## 15. The `Private Network Access` edge — a loopback fetch

```text
a public-origin fetch to a private/loopback address needs a PNA
preflight — a separate Chrome-only gate beyond CORS. relevant when
the target is internal and the page is public.
```

## 16. The `Access-Control-Allow-Headers: *` credential edge

```text
ACAH:* covers MOST headers but NOT 'Authorization' on a credentialed
request in some engines — a `*` header-allow may still block the
Bearer.
```

## 17. The `Access-Control-Allow-Methods: *` credential edge

```text
ACAM:* covers the methods — but some engines require an explicit
list for credentialed requests — a `*` method-allow may not cover
a credentialed non-simple request.
```

## 18. The redirect-CORS edge — the final response's check

```text
a CORS fetch that redirects — the FINAL response's ACAO is checked,
not the redirect's. a redirect to a different origin is a new CORS
question entirely.
```

## 19. The `file://` origin — a local-file edge

```text
a file:// page's Origin is 'null' (modern) — it can read a
null-allowed CORS — a local-file phishing page + a null-allowed API.
```

## 20. The `about:blank` / `chrome-extension:` origin edge

```text
an about:blank iframe inherits the embedder's origin; a
chrome-extension page's origin is its extension id — neither is a
normal web origin — a loose 'any non-null origin' check may pass.
```

## 21. The `SameSite=None` + ITP edge — Safari's extra gate

```text
Safari's Intelligent Tracking Prevention strips a cross-site cookie
as 'tracking' even when SameSite=None — an extra non-spec gate that
breaks a credentialed CORS read in WebKit.
```

## 22. The `opaque` response edge — a `no-cors` read attempt

```text
a `no-cors` fetch's response is opaque — status 0, unreadable —
it LOOKS like a CORS block but is a different mechanism (the write
fired; only the read is opaque).
```

## 23. The `Access-Control-Request-Method` casing edge

```text
the preflight's Access-Control-Request-Method is case-sensitive —
'GET' vs 'get' — a strict ACAM check may reject a lowercase ask.
```

## 24. The double-ACAO edge — a duplicate header

```text
a response with TWO ACAO headers — the browser takes the LAST (or
rejects on ambiguity) — a proxy+app both setting ACAO is a
confusion source.
```

## 25. The edge-case index — a quick lookup

```text
*+creds            → rejected, always
no Vary            → a cache-poison surface
long Max-Age       → a stale permissive preflight
SameSite=None,noSecure → cookie rejected
JSON body          → a preflight needed
urlencoded body    → simple, no preflight
null origin        → sandboxed/data:/file:
no-cors fetch      → opaque write — CSRF, not CORS
CORP:same-origin   → blocks LOADING not reading
PNA                → a private-network preflight
ITP                → Safari strips the cookie anyway
```
