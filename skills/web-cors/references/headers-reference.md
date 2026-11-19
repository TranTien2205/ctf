# Headers reference — every CORS header and what it does

The complete CORS header surface — the request headers, the response
headers, and the rules.

---

## 1. The request headers — what the browser sends

```text
Origin                            — the page's origin — the gate's input
Access-Control-Request-Method     — the preflight's method ask
Access-Control-Request-Headers    — the preflight's header ask
```

## 2. The response headers — the permission

```text
Access-Control-Allow-Origin       — which origin may READ (the gate)
Access-Control-Allow-Credentials  — may the credential ride (the gate)
Access-Control-Allow-Methods      — which methods (preflight)
Access-Control-Allow-Headers      — which headers (preflight)
Access-Control-Expose-Headers     — which response headers JS may read
Access-Control-Max-Age            — how long the preflight is cached
```

## 3. `Access-Control-Allow-Origin` — the read gate

```text
a single value or `*`. the browser compares the page's Origin to it:
- an exact match → the read allowed
- `*` → allowed WITHOUT credentials
- a mismatch / absent → the read blocked
```

## 4. `Access-Control-Allow-Credentials` — the credential gate

```text
'true' → the response may be read WITH credentials — the cookie/
header rides. 'false' or absent → non-credentialed. requires ACAO
to name the origin (not `*`).
```

## 5. `Access-Control-Allow-Methods` — the method list

```text
a comma-list — GET,POST,PUT,... or `*` (but `*` doesn't cover
credentialed requests in some engines). a non-simple method needs
its name in this list.
```

## 6. `Access-Control-Allow-Headers` — the header list

```text
a comma-list — the custom headers the request may send. `*` covers
most but NOT Authorization on a credentialed request. a custom
header not listed → the preflight fails.
```

## 7. `Access-Control-Expose-Headers` — which response headers JS sees

```text
by default JS sees only safelisted headers (Content-Type, etc.).
Expose-Headers names additional readable headers — a token in a
response header needs to be listed to be readable.
```

## 8. `Access-Control-Max-Age` — the preflight cache

```text
seconds — how long the browser caches the preflight answer. a long
value = a stale permission persists. a test must beat the cache.
```

## 9. The non-CORS headers that gate the read

```text
Set-Cookie / SameSite           — does the cookie attach
Vary: Origin                    — per-origin caching
Cache-Control                   — shared-cache behavior
Content-Type                    — simple-vs-preflight (request) /
                                  JS-servable (JSONP response)
Cross-Origin-Opener-Policy      — a window-reference gate (separate)
Cross-Origin-Resource-Policy    — a resource-load gate (separate)
Cross-Origin-Embedder-Policy    — a document-isolation gate (separate)
```

## 10. CORP/COOP/COEP — the related isolation headers

```text
Cross-Origin-Resource-Policy: same-origin — blocks <img>/<script>
cross-origin loads — a resource gate, not a fetch-read gate.
Cross-Origin-Opener-Policy — a window.postMessage/opener gate.
Cross-Origin-Embedder-Policy — requires corp on subresources.
these gate LOADING, not fetch-READING — a separate layer.
```

## 11. The request-side simple-header safelist

```text
the SAFELISTED request headers (no preflight):
Accept, Accept-Language, Content-Language,
Content-Type (only urlencoded/multipart/text-plain),
Range (a limited set), DPR/Downlink/Save-Data/Viewport-Width/Width
any other header → a preflight.
```

## 12. The header-combination matrix — what each pairing means

```text
ACAO:reflected + ACAC:true         → credentialed read — vuln
ACAO:null + ACAC:true              → opaque read — vuln
ACAO:* + ACAC:true                 → invalid — rejected
ACAO:fixed + ACAC:true             → credentialed for that origin
ACAO:* (no ACAC)                   → public read
no ACAO                            → no CORS read
ACA-Expose-Headers + a token hdr   → a readable token
Vary:Origin + reflected ACAO       → per-origin — clean test
no Vary + reflected ACAO           → a cache-poison surface
```
