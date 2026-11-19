# Detection surface — where the cache layer is, exhaustively

The complete map of where a cache lives and where the keying fails.

---

## 1. The front-end cache — the reverse-proxy layer

```text
a reverse-proxy cache (nginx proxy_cache, Varnish, a CDN edge) sits
in front of the app — it stores the origin's responses per-key —
the shared copy is the vulnerability.
```

## 2. The app-level cache — the in-app layer

```text
an app-level cache (Rails.cache, Django cache_page, flask_caching)
stores the app's rendered responses — a per-URL or a per-fragment key —
the same key-mismatch applies.
```

## 3. The CDN edge — the distributed layer

```text
a CDN edge (Cloudflare, CloudFront, Fastly, Akamai) caches at the
edge — a cache rule/policy determines the key — an unkeyed input is
a request part the rule ignores.
```

## 4. The browser cache — the client-side layer

```text
a browser cache (Cache-Control, ETag) stores the response client-side —
a per-user cache — not a shared store — a different class.
```

## 5. The detection signals — the headers that name a cache

```bash
# the status + the via — which layer
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age|via|x-varnish|x-served-by|server|x-cached'
#   X-Cache-Status + Server: nginx → an nginx cache
#   CF-Cache-Status + Server: cloudflare → a Cloudflare cache
#   X-Varnish → a Varnish cache
#   X-Served-By: cache-<id> → a Fastly cache
#   X-Cache: Hit from cloudfront → a CloudFront cache
```

## 6. The cache-status map — which header for which layer

```text
nginx        → X-Cache-Status: HIT/MISS/EXPIRED/STALE/BYPASS
Varnish      → X-Varnish: <two IDs> (a hit) or <one ID> (a miss)
Cloudflare   → CF-Cache-Status: HIT/MISS/DYNAMIC/EXPIRED
CloudFront   → X-Cache: Hit from cloudfront / Miss
Fastly       → X-Served-By: cache-<id> / X-Cache: HIT
Akamai       → X-Cache: TCP_HIT / TCP_MISS
generic      → Via, Age, X-Cache
```

## 7. The keying signals — the headers that name the key

```bash
# the Vary header — which headers vary the cache
curl -sI "$BASE/" | grep -i 'vary'
#   Vary: Cookie → the cache keys on the cookie
#   Vary: Accept-Encoding → the cache keys on the encoding
#   Vary: X-Custom → the cache keys on X-Custom
#   (no Vary) → the cache ignores those headers
```

## 8. The cacheable signals — the headers that name a cacheable page

```text
a Cache-Control: public, max-age → a cacheable page
a Cache-Control: no-store/private → a non-cached page
an ETag / a Last-Modified → a cacheable page
```

## 9. The source signals — the config that names the cache

```bash
# the cache config — the layer + the key
grep -rnoiE 'proxy_cache|cache_key|vcl_hash|hash_data|Rails.cache|cache_page|flask_caching|cf-cache|cloudflare|edge|cdn' <src> | head -20
```

## 10. The unkeyed-input signals — the headers the app reads

```bash
# the unkeyed-input surface — the app reads, the cache ignores
grep -rnoiE 'X-Forwarded|X-Original|X-Rewrite|Referer|User-Agent|Accept-Language|Accept-Charset|Accept|header|reflection|echo|request.headers|request\.META|request\.env' <src> | head -30
```

## 11. The deception signals — the privileged page

```bash
# the privileged page — a settings/profile/dashboard
grep -rnoiE 'settings|profile|dashboard|admin|authenticated|session|personalized|login|private' <src> | head -20
```

## 12. The per-surface map — which signals name which surface

```text
a 'proxy_cache|cache_key|X-Cache-Status' → an nginx cache
a 'vcl_hash|hash_data|Varnish'           → a Varnish cache
a 'cf-cache|cloudflare'                  → a Cloudflare cache
a 'Rails.cache|cache_page|flask_caching' → an app-level cache
a 'Vary|vary'                            → the key's discriminator
a 'X-Forwarded|X-Original|X-Rewrite'     → an unkeyed-header surface
a 'Referer|User-Agent|Accept'            → a reflected-header surface
a 'settings|profile|dashboard|admin'     → a deception surface
a 'Cache-Control|no-store|private'       → a cacheable surface
```
